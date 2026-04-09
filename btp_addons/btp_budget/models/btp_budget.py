from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BtpBudget(models.Model):
    _name = "btp.budget"
    _description = "Budget chantier"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"
    _check_company_auto = True

    name = fields.Char(string="Référence", required=True, copy=False, readonly=True, default=lambda self: _("Nouveau"))
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)

    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", store=True, readonly=True)

    chantier_id = fields.Many2one("btp.chantier", string="Chantier", required=True, tracking=True, check_company=True)
    devis_id = fields.Many2one("btp.devis", string="Devis source", readonly=True, check_company=True)

    type = fields.Selection(
        [
            ("initial", "Initial"),
            ("revised", "Révisé"),
        ],
        default="initial",
        required=True,
        tracking=True,
        index=True,
    )
    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("validated", "Validé"),
            ("cancel", "Annulé"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )

    line_ids = fields.One2many("btp.budget.line", "budget_id", string="Lignes budget")

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
                vals["name"] = seq.next_by_code("btp.budget") or _("Nouveau")
        return super().create(vals_list)

    def action_validate(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("Impossible de valider un budget sans lignes."))
            rec.state = "validated"
            if rec.type == "initial":
                rec.chantier_id.budget_initial = rec.amount_cost_direct
            else:
                rec.chantier_id.budget_revised = rec.amount_cost_direct

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})


class BtpBudgetLine(models.Model):
    _name = "btp.budget.line"
    _description = "Budget chantier - Ligne"
    _order = "sequence, id"
    _check_company_auto = True

    sequence = fields.Integer(default=10)
    budget_id = fields.Many2one("btp.budget", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="budget_id.company_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="budget_id.currency_id", store=True, readonly=True)
    chantier_id = fields.Many2one(related="budget_id.chantier_id", store=True, readonly=True)

    ouvrage_id = fields.Many2one("btp.ouvrage", string="Ouvrage", ondelete="restrict")
    name = fields.Char(string="Désignation", required=True)
    uom_id = fields.Many2one("uom.uom", string="Unité", required=True, ondelete="restrict")
    quantity = fields.Float(string="Quantité", default=1.0, required=True)

    unit_cost_direct = fields.Monetary(string="Déboursé sec (PU)", required=True, default=0.0)
    unit_sale_price = fields.Monetary(string="Prix de vente (PU)", required=True, default=0.0)

    subtotal_cost_direct = fields.Monetary(string="Déboursé sec", compute="_compute_subtotals", store=True)
    subtotal_sale = fields.Monetary(string="Prix de vente", compute="_compute_subtotals", store=True)

    @api.depends("quantity", "unit_cost_direct", "unit_sale_price")
    def _compute_subtotals(self):
        for rec in self:
            rec.subtotal_cost_direct = (rec.quantity or 0.0) * (rec.unit_cost_direct or 0.0)
            rec.subtotal_sale = (rec.quantity or 0.0) * (rec.unit_sale_price or 0.0)

