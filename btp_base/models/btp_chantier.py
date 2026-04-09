from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BtpChantier(models.Model):
    _name = "btp.chantier"
    _description = "Chantier"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code desc, id desc"
    _check_company_auto = True

    code = fields.Char(
        string="Code chantier",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("Nouveau"),
        index=True,
        tracking=True,
    )
    name = fields.Char(string="Libellé", required=True, tracking=True)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client (Maître d'ouvrage)",
        tracking=True,
        check_company=False,
    )
    maitre_oeuvre_id = fields.Many2one(
        "res.partner",
        string="Maître d'œuvre",
        tracking=True,
        check_company=False,
    )
    bureau_controle_id = fields.Many2one(
        "res.partner",
        string="Bureau de contrôle",
        tracking=True,
        check_company=False,
    )

    geo_zone_id = fields.Many2one("btp.geo.zone", string="Zone géographique", ondelete="restrict")
    address = fields.Char(string="Localisation / Adresse")
    market_type_id = fields.Many2one("btp.market.type", string="Type de marché", ondelete="restrict")

    date_start_planned = fields.Date(string="Début prévisionnel", tracking=True)
    date_end_planned = fields.Date(string="Fin prévisionnelle", tracking=True)
    date_start_actual = fields.Date(string="Début réel", tracking=True)
    date_end_actual = fields.Date(string="Fin réelle", tracking=True)

    conducteur_travaux_id = fields.Many2one(
        "res.users",
        string="Conducteur de travaux",
        tracking=True,
        check_company=False,
    )
    chef_chantier_id = fields.Many2one(
        "res.users",
        string="Chef de chantier",
        tracking=True,
        check_company=False,
    )

    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Centre analytique",
        tracking=True,
        check_company=True,
        help="Centre analytique principal du chantier (centre de profit).",
    )
    project_id = fields.Many2one(
        "project.project",
        string="Projet Odoo",
        tracking=True,
        check_company=True,
        help="Projet standard Odoo associé (optionnel).",
    )

    amount_contract = fields.Monetary(string="Montant marché", tracking=True)
    budget_initial = fields.Monetary(string="Budget initial", tracking=True)
    budget_revised = fields.Monetary(string="Budget révisé", tracking=True)

    progress_rate = fields.Float(string="Taux d'avancement (%)", tracking=True)
    margin_expected = fields.Monetary(string="Marge prévisionnelle")
    margin_real = fields.Monetary(string="Marge réelle")
    cashflow_expected = fields.Monetary(string="Trésorerie prévisionnelle")
    cashflow_real = fields.Monetary(string="Trésorerie réalisée")

    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("study", "Étude"),
            ("validated", "Validé"),
            ("in_progress", "En cours"),
            ("suspended", "Suspendu"),
            ("done", "Clôturé"),
            ("cancel", "Annulé"),
        ],
        string="Statut",
        required=True,
        default="draft",
        tracking=True,
        index=True,
    )

    @api.constrains("progress_rate")
    def _check_progress_rate(self):
        for rec in self:
            if rec.progress_rate < 0.0 or rec.progress_rate > 100.0:
                raise ValidationError(_("Le taux d'avancement doit être compris entre 0 et 100%."))

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("code", _("Nouveau")) == _("Nouveau"):
                vals["code"] = seq.next_by_code("btp.chantier") or _("Nouveau")
        records = super().create(vals_list)
        records._ensure_analytic_account()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(k in vals for k in ["name", "partner_id", "company_id"]) and self:
            self._ensure_analytic_account()
        return res

    def _ensure_analytic_account(self):
        plan = self.env.ref("btp_base.analytic_plan_chantiers", raise_if_not_found=False)
        for rec in self:
            if rec.analytic_account_id or not plan:
                continue
            rec.analytic_account_id = self.env["account.analytic.account"].create(
                {
                    "name": f"[{rec.code}] {rec.name}",
                    "code": rec.code,
                    "plan_id": plan.id,
                    "partner_id": rec.partner_id.id,
                    "company_id": rec.company_id.id,
                }
            )

    def action_set_study(self):
        self.write({"state": "study"})

    def action_validate(self):
        self.write({"state": "validated"})

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_suspend(self):
        self.write({"state": "suspended"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

