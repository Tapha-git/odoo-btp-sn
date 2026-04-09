from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BtpOuvrage(models.Model):
    _name = "btp.ouvrage"
    _description = "Ouvrage (Bibliothèque)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code, name"
    _check_company_auto = True

    code = fields.Char(string="Code ouvrage", required=True, index=True, tracking=True)
    name = fields.Char(string="Désignation", required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", store=True, readonly=True)

    uom_id = fields.Many2one("uom.uom", string="Unité", required=True, ondelete="restrict")

    version_ids = fields.One2many("btp.ouvrage.version", "ouvrage_id", string="Versions")
    validated_version_id = fields.Many2one(
        "btp.ouvrage.version",
        string="Version validée",
        compute="_compute_validated_version",
        store=True,
        readonly=True,
    )

    _code_company_uniq = models.Constraint(
        "UNIQUE (company_id, code)",
        "Le code ouvrage doit être unique par société.",
    )

    @api.depends("version_ids.state")
    def _compute_validated_version(self):
        for rec in self:
            rec.validated_version_id = rec.version_ids.filtered(lambda v: v.state == "validated")[:1].id

    def action_create_version(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Nouvelle version"),
            "res_model": "btp.ouvrage.version",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_ouvrage_id": self.id,
            },
        }


class BtpOuvrageVersion(models.Model):
    _name = "btp.ouvrage.version"
    _description = "Ouvrage - Version"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"
    _check_company_auto = True

    name = fields.Char(string="Libellé version", required=True, tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)

    ouvrage_id = fields.Many2one("btp.ouvrage", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="ouvrage_id.company_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="ouvrage_id.currency_id", store=True, readonly=True)
    uom_id = fields.Many2one(related="ouvrage_id.uom_id", store=True, readonly=True)

    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("validated", "Validée"),
            ("archived", "Archivée"),
        ],
        default="draft",
        required=True,
        index=True,
        tracking=True,
    )

    line_ids = fields.One2many("btp.ouvrage.sousdetail", "version_id", string="Sous-détails")

    overhead_site_pct = fields.Float(string="Frais de chantier (%)", default=0.0)
    overhead_general_pct = fields.Float(string="Frais généraux (%)", default=0.0)
    risk_pct = fields.Float(string="Aléas (%)", default=0.0)
    margin_pct = fields.Float(string="Marge (%)", default=0.0)

    cost_direct = fields.Monetary(string="Déboursé sec (PU)", compute="_compute_costs", store=True)
    cost_total = fields.Monetary(string="Coût complet (PU)", compute="_compute_costs", store=True)
    sale_unit_price = fields.Monetary(string="Prix de vente (PU)", compute="_compute_costs", store=True)

    @api.constrains("overhead_site_pct", "overhead_general_pct", "risk_pct", "margin_pct")
    def _check_percentages(self):
        for rec in self:
            for field_name in ["overhead_site_pct", "overhead_general_pct", "risk_pct", "margin_pct"]:
                val = rec[field_name]
                if val < 0.0 or val > 100.0:
                    raise ValidationError(_("Les pourcentages doivent être compris entre 0 et 100."))

    @api.depends(
        "line_ids.quantity",
        "line_ids.unit_cost",
        "overhead_site_pct",
        "overhead_general_pct",
        "risk_pct",
        "margin_pct",
    )
    def _compute_costs(self):
        for rec in self:
            cost_direct = sum(rec.line_ids.mapped("subtotal"))
            cost_total = cost_direct * (1 + rec.overhead_site_pct / 100.0) * (1 + rec.overhead_general_pct / 100.0)
            cost_total = cost_total * (1 + rec.risk_pct / 100.0)
            sale_unit_price = cost_total * (1 + rec.margin_pct / 100.0)
            rec.cost_direct = cost_direct
            rec.cost_total = cost_total
            rec.sale_unit_price = sale_unit_price

    def action_validate(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("Impossible de valider une version sans sous-détails."))
            rec.ouvrage_id.version_ids.filtered(lambda v: v.state == "validated" and v.id != rec.id).write(
                {"state": "archived"}
            )
            rec.state = "validated"

    def action_archive(self):
        self.write({"state": "archived"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})


class BtpOuvrageSousDetail(models.Model):
    _name = "btp.ouvrage.sousdetail"
    _description = "Ouvrage - Sous-détail"
    _order = "sequence, id"
    _check_company_auto = True

    sequence = fields.Integer(default=10)
    version_id = fields.Many2one("btp.ouvrage.version", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="version_id.company_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="version_id.currency_id", store=True, readonly=True)

    resource_nature_id = fields.Many2one(
        "btp.resource.nature",
        string="Nature",
        required=True,
        ondelete="restrict",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Article",
        domain="[('company_id', 'in', [False, company_id])]",
    )
    name = fields.Char(string="Désignation", required=True)
    uom_id = fields.Many2one("uom.uom", string="Unité", required=True, ondelete="restrict")
    quantity = fields.Float(string="Quantité", default=1.0, required=True)
    unit_cost = fields.Monetary(string="Coût unitaire", required=True, default=0.0)
    subtotal = fields.Monetary(string="Sous-total", compute="_compute_subtotal", store=True)

    @api.depends("quantity", "unit_cost")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.quantity or 0.0) * (rec.unit_cost or 0.0)
