from odoo.tests.common import TransactionCase


class TestBtpChantier(TransactionCase):
    def test_chantier_sequence_and_analytic(self):
        chantier = self.env["btp.chantier"].create({"name": "Chantier Test"})
        self.assertTrue(chantier.code)
        self.assertTrue(chantier.analytic_account_id)

