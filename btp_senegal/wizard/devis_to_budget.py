from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BtpDevisToBudgetWizard(models.TransientModel):
    _name = "btp.devis.to.budget.wizard"
    _description = "Générer un budget depuis un devis"

    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)

    devis_id = fields.Many2one(
        "btp.devis",
        string="Devis",
        required=True,
        domain="[('state', '=', 'validated'), ('company_id', '=', company_id)]",
    )
    chantier_id = fields.Many2one(
        "btp.chantier",
        string="Chantier",
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    budget_type = fields.Selection(
        [
            ("initial", "Initial"),
            ("revised", "Révisé"),
        ],
        default="initial",
        required=True,
    )
    auto_validate = fields.Boolean(string="Valider automatiquement", default=False)

    @api.onchange("devis_id")
    def _onchange_devis_id(self):
        for rec in self:
            if rec.devis_id and not rec.chantier_id and rec.devis_id.chantier_id:
                rec.chantier_id = rec.devis_id.chantier_id
            if rec.devis_id:
                rec.company_id = rec.devis_id.company_id

    def action_generate(self):
        self.ensure_one()
        if self.devis_id.state != "validated":
            raise ValidationError(_("Le devis doit être validé."))
        if not self.devis_id.line_ids:
            raise ValidationError(_("Le devis ne contient aucune ligne."))

        budget = self.env["btp.budget"].create(
            {
                "chantier_id": self.chantier_id.id,
                "devis_id": self.devis_id.id,
                "type": self.budget_type,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "ouvrage_id": line.ouvrage_id.id,
                            "name": line.name,
                            "uom_id": line.uom_id.id,
                            "quantity": line.quantity,
                            "unit_cost_direct": line.unit_cost_direct,
                            "unit_sale_price": line.unit_sale_price,
                        },
                    )
                    for line in self.devis_id.line_ids
                ],
            }
        )
        if self.auto_validate:
            budget.action_validate()

        return {
            "type": "ir.actions.act_window",
            "res_model": "btp.budget",
            "view_mode": "form",
            "res_id": budget.id,
        }
