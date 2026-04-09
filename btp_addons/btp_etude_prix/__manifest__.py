{
    "name": "BTP - Étude de prix",
    "version": "19.0.1.0.0",
    "category": "Construction",
    "summary": "Bibliothèque d'ouvrages, sous-détails, DQE et devis BTP",
    "author": "Votre Société",
    "license": "LGPL-3",
    "depends": [
        "btp_base",
        "mail",
        "product",
        "uom",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/btp_ouvrage_views.xml",
        "views/btp_devis_views.xml",
        "views/btp_etude_menus.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "application": False,
    "installable": True,
}
