from odoo.tests.common import TransactionCase


class TestBtpDevisToBudget(TransactionCase):
    def test_generate_budget_from_devis(self):
        chantier = self.env["btp.chantier"].create({"name": "Chantier Budget Test"})

        ouvrage = self.env["btp.ouvrage"].create(
            {
                "code": "OUV-BUD",
                "name": "Ouvrage budget",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        version = self.env["btp.ouvrage.version"].create(
            {
                "ouvrage_id": ouvrage.id,
                "name": "V1",
                "state": "validated",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "resource_nature_id": self.env.ref("btp_senegal.nature_material").id,
                            "name": "Ligne",
                            "uom_id": self.env.ref("uom.product_uom_unit").id,
                            "quantity": 1,
                            "unit_cost": 1000,
                        },
                    )
                ],
                "margin_pct": 10,
            }
        )
        devis = self.env["btp.devis"].create({"state": "validated"})
        self.env["btp.devis.line"].create(
            {
                "devis_id": devis.id,
                "ouvrage_id": ouvrage.id,
                "ouvrage_version_id": version.id,
                "name": ouvrage.name,
                "uom_id": ouvrage.uom_id.id,
                "quantity": 2,
            }
        )

        wizard = self.env["btp.devis.to.budget.wizard"].create(
            {"devis_id": devis.id, "chantier_id": chantier.id, "budget_type": "initial", "auto_validate": True}
        )
        action = wizard.action_generate()
        budget = self.env["btp.budget"].browse(action["res_id"])

        self.assertEqual(budget.state, "validated")
        self.assertEqual(budget.chantier_id.id, chantier.id)
        self.assertEqual(len(budget.line_ids), 1)
        self.assertEqual(budget.line_ids.quantity, 2)
