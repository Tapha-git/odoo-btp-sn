{
    "name": "BTP - Base",
    "version": "19.0.1.0.0",
    "category": "Construction",
    "summary": "Référentiels et objet Chantier (socle BTP)",
    "author": "Votre Société",
    "license": "OPL-1",
    "depends": [
        "mail",
        "analytic",
        "project",
    ],
    "data": [
        "security/btp_security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/analytic_plan.xml",
        "views/btp_referentiel_views.xml",
        "views/btp_chantier_views.xml",
        "views/btp_menus.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "application": False,
    "installable": True,
}
