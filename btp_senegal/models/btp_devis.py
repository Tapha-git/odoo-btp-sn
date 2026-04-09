from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BtpDevis(models.Model):
    _name = "btp.devis"
    _description = "Devis BTP (DQE)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"
    _check_company_auto = True

    name = fields.Char(string="Référence", required=True, copy=False, readonly=True, default=lambda self: _("Nouveau"))
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", store=True, readonly=True)

    partner_id = fields.Many2one("res.partner", string="Client (Maître d'ouvrage)", tracking=True)
    chantier_id = fields.Many2one("btp.chantier", string="Chantier (optionnel)", tracking=True, check_company=True)

    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("review", "En revue"),
            ("validated", "Validé"),
            ("cancel", "Annulé"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )

    line_ids = fields.One2many("btp.devis.line", "devis_id", string="Lignes DQE")

    amount_cost_direct = fields.Monetary(string="Déboursé sec total", compute="_compute_amounts", store=True)
    amount_sale = fields.Monetary(string="Prix de vente total", compute="_compute_amounts", store=True)

    @api.depends("line_ids.subtotal_cost_direct", "line_ids.subtotal_sale")
    def _compute_amounts(self):
        for rec in self:
            rec.amount_cost_direct = sum(rec.line_ids.mapped("subtotal_cost_direct"))
            rec.amount_sale = sum(rec.line_ids.mapped("subtotal_sale"))

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", _("Nouveau")) == _("Nouveau"):
                vals["name"] = seq.next_by_code("btp.devis") or _("Nouveau")
        return super().create(vals_list)

    def action_set_review(self):
        self.write({"state": "review"})

    def action_validate(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("Impossible de valider un devis sans lignes."))
            rec.state = "validated"

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_recompute_prices(self):
        for rec in self:
            rec.line_ids._compute_unit_prices()


class BtpDevisLine(models.Model):
    _name = "btp.devis.line"
    _description = "Devis BTP - Ligne"
    _order = "sequence, id"
    _check_company_auto = True

    sequence = fields.Integer(default=10)
    devis_id = fields.Many2one("btp.devis", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="devis_id.company_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="devis_id.currency_id", store=True, readonly=True)

    ouvrage_id = fields.Many2one("btp.ouvrage", string="Ouvrage", required=True, ondelete="restrict")
    ouvrage_version_id = fields.Many2one(
        "btp.ouvrage.version",
        string="Version",
        required=True,
        ondelete="restrict",
        domain="[('ouvrage_id', '=', ouvrage_id), ('state', '=', 'validated')]",
    )

    name = fields.Char(string="Désignation", required=True)
    uom_id = fields.Many2one("uom.uom", string="Unité", required=True, ondelete="restrict")
    quantity = fields.Float(string="Quantité", default=1.0, required=True)

    unit_cost_direct = fields.Monetary(string="Déboursé sec (PU)", compute="_compute_unit_prices", store=True, readonly=True)
    unit_sale_price = fields.Monetary(string="Prix de vente (PU)", compute="_compute_unit_prices", store=True, readonly=True)

    subtotal_cost_direct = fields.Monetary(string="Déboursé sec", compute="_compute_subtotals", store=True)
    subtotal_sale = fields.Monetary(string="Prix de vente", compute="_compute_subtotals", store=True)

    @api.depends("quantity", "unit_cost_direct", "unit_sale_price")
    def _compute_subtotals(self):
        for rec in self:
            rec.subtotal_cost_direct = (rec.quantity or 0.0) * (rec.unit_cost_direct or 0.0)
            rec.subtotal_sale = (rec.quantity or 0.0) * (rec.unit_sale_price or 0.0)

    @api.onchange("ouvrage_id")
    def _onchange_ouvrage_id(self):
        for rec in self:
            if not rec.ouvrage_id:
                continue
            rec.ouvrage_version_id = rec.ouvrage_id.validated_version_id
            rec.name = rec.ouvrage_id.name
            rec.uom_id = rec.ouvrage_id.uom_id
            rec._compute_unit_prices()

    @api.depends("ouvrage_version_id.cost_direct", "ouvrage_version_id.sale_unit_price")
    def _compute_unit_prices(self):
        for rec in self:
            if not rec.ouvrage_version_id:
                rec.unit_cost_direct = 0.0
                rec.unit_sale_price = 0.0
                continue
            rec.unit_cost_direct = rec.ouvrage_version_id.cost_direct
            rec.unit_sale_price = rec.ouvrage_version_id.sale_unit_price
