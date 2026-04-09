{
    "name": "BTP - Budget chantier",
    "version": "19.0.1.0.0",
    "category": "Construction",
    "summary": "Budget initial/révisé et génération depuis devis (DQE)",
    "author": "Votre Société",
    "license": "OPL-1",
    "depends": [
        "btp_base",
        "btp_etude_prix",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/btp_budget_views.xml",
        "wizard/devis_to_budget_views.xml",
        "views/btp_budget_menus.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "application": False,
}
