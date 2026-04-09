from odoo import fields, models


class BtpCostCategory(models.Model):
    _name = "btp.cost.category"
    _description = "Catégorie de coût (BTP)"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)


class BtpResourceNature(models.Model):
    _name = "btp.resource.nature"
    _description = "Nature de ressource (BTP)"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    cost_category_id = fields.Many2one(
        "btp.cost.category",
        string="Catégorie de coût",
        help="Catégorie de coût par défaut associée à cette nature (matériaux, main-d'œuvre, etc.).",
        ondelete="restrict",
    )


class BtpGeoZone(models.Model):
    _name = "btp.geo.zone"
    _description = "Zone géographique (BTP)"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(index=True)
    active = fields.Boolean(default=True)


class BtpMarketType(models.Model):
    _name = "btp.market.type"
    _description = "Type de marché (BTP)"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

