from odoo.tests.common import TransactionCase


class TestBtpEtudePrix(TransactionCase):
    def test_ouvrage_version_compute(self):
        ouvrage = self.env["btp.ouvrage"].create(
            {
                "code": "OUV-TST",
                "name": "Ouvrage test",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        version = self.env["btp.ouvrage.version"].create(
            {
                "ouvrage_id": ouvrage.id,
                "name": "V1",
                "overhead_site_pct": 10,
                "overhead_general_pct": 0,
                "risk_pct": 0,
                "margin_pct": 10,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "resource_nature_id": self.env.ref("btp_senegal.nature_material").id,
                            "name": "Ligne",
                            "uom_id": self.env.ref("uom.product_uom_unit").id,
                            "quantity": 2,
                            "unit_cost": 1000,
                        },
                    )
                ],
            }
        )
        self.assertEqual(version.cost_direct, 2000)
        self.assertEqual(version.cost_total, 2200)
        self.assertEqual(version.sale_unit_price, 2420)
