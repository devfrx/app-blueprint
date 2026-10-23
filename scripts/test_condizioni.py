import unittest

import condizioni as c

SCHEDA = {"esposizione": "pubblicabile", "criticita": "media", "inneschi": ["ui", "dati-personali"]}


def voce(quando, natura="progetto", fase=4):
    return {"quando": quando, "natura": natura, "fase": fase}


class Analisi(unittest.TestCase):
    def test_sintassi_valida(self):
        alt = c.analizza("esposizione >= pubblico o innesco ui e criticita >= alta")
        self.assertEqual(len(alt), 2)
        self.assertEqual(len(alt[1]), 2)

    def test_sintassi_non_valida(self):
        for testo in ("", "esposizione >= pubblicoo", "innesco", "o sempre", "sempre e", "criticita => alta",
                      "qualcosa"):
            with self.subTest(testo=testo), self.assertRaises(c.CondizioneNonValida):
                c.analizza(testo)

    def test_innesco_sconosciuto(self):
        with self.assertRaises(c.CondizioneNonValida):
            c.analizza("innesco blockchain", inneschi_noti={"ui"})

    def test_negazione(self):
        alt = c.analizza("non innesco ui")
        self.assertFalse(c.vale(alt, "personale", "bassa", {"ui"}))
        self.assertTrue(c.vale(alt, "personale", "bassa", set()))


class Applicabilita(unittest.TestCase):
    def test_sempre(self):
        self.assertEqual(c.stato_voce(voce("sempre"), SCHEDA), c.APPLICABILE)

    def test_pubblicabile_progetto_vale_come_pubblico(self):
        self.assertEqual(c.stato_voce(voce("esposizione >= pubblico"), SCHEDA), c.APPLICABILE)

    def test_pubblicabile_esercizio_rinviata(self):
        self.assertEqual(c.stato_voce(voce("esposizione >= pubblico", "esercizio"), SCHEDA), c.RINVIATA)

    def test_esercizio_applicabile_se_vale_gia(self):
        self.assertEqual(c.stato_voce(voce("innesco dati-personali o esposizione >= pubblico", "esercizio"), SCHEDA),
                         c.APPLICABILE)

    def test_personale_non_applicabile(self):
        scheda = dict(SCHEDA, esposizione="personale")
        self.assertEqual(c.stato_voce(voce("esposizione >= pubblico", "esercizio"), scheda), c.NON_APPLICABILE)
        self.assertEqual(c.stato_voce(voce("esposizione >= pubblicabile"), scheda), c.NON_APPLICABILE)

    def test_pubblico(self):
        scheda = dict(SCHEDA, esposizione="pubblico")
        self.assertEqual(c.stato_voce(voce("esposizione >= pubblico", "esercizio"), scheda), c.APPLICABILE)

    def test_criticita_e_innesco(self):
        self.assertEqual(c.stato_voce(voce("criticita >= alta"), SCHEDA), c.NON_APPLICABILE)
        self.assertEqual(c.stato_voce(voce("innesco denaro"), SCHEDA), c.NON_APPLICABILE)
        self.assertEqual(c.stato_voce(voce("innesco ui"), SCHEDA), c.APPLICABILE)

    def test_fuori_catena(self):
        self.assertEqual(c.stato_voce(voce("sempre", fase=13), SCHEDA), c.FUORI_CATENA)
        self.assertEqual(c.stato_voce(voce("innesco denaro", fase=15), SCHEDA), c.NON_APPLICABILE)

    def test_ordine_degli_id(self):
        ordinati = sorted(["5.06", "5.05", "T.01", "5.05.1", "10.01", "D.01", "5.05.4", "2.15"], key=c.chiave_id)
        self.assertEqual(ordinati, ["2.15", "5.05", "5.05.1", "5.05.4", "5.06", "10.01", "D.01", "T.01"])


if __name__ == "__main__":
    unittest.main()
