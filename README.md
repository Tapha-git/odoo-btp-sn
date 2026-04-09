# Odoo BTP Sénégal (OHADA) - Addons

Addons Odoo 19 pour une entreprise BTP au Sénégal (workflow chantier, étude de prix, budget, etc.).

## Addons

- `btp_addons/btp_base`
- `btp_addons/btp_etude_prix`
- `btp_addons/btp_budget`

## Démarrage (Docker)

Le `docker-compose.yaml` expose Odoo sur `http://localhost:8069` et monte les addons BTP dans `/mnt/extra-addons`.

## Installation

Dans Odoo (base `admin`), installe :

- **BTP - Base**
- **BTP - Étude de prix**
- **BTP - Budget chantier**

