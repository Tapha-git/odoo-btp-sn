# Odoo BTP Sénégal (OHADA) - Addons

Addons Odoo 19 pour une entreprise BTP au Sénégal (workflow chantier, étude de prix, budget, etc.).

## Addons

- `btp_base`
- `btp_etude_prix`
- `btp_budget`
- `btp_suite` (module à publier/vendre sur Odoo Apps)

## Démarrage (Docker)

Le `docker-compose.yaml` expose Odoo sur `http://localhost:8069` et monte les addons BTP dans `/mnt/extra-addons`.

## Installation

Dans Odoo (base `admin`), installe :

- **BTP - Base**
- **BTP - Étude de prix**
- **BTP - Budget chantier**
