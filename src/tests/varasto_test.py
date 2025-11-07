"""Tämä tiedosto sisältää yksikkötestit Varasto-projektille."""
import unittest
from varasto import Varasto


class TestVarasto(unittest.TestCase):
    """Luokka TestVarasto tarjoaa yksikkötestejä"""
    def setUp(self):
        self.varasto = Varasto(10)

    def test_konstruktori_luo_tyhjan_varaston(self):
        """Testaa uuden varaston luominen."""
        # https://docs.python.org/3/library/unittest.html
        #unittest.TestCase.assertAlmostEqual
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_uudella_varastolla_oikea_tilavuus(self):
        """Testaa, että uudella varastolla on oikea tilavuus."""
        self.assertAlmostEqual(self.varasto.tilavuus, 10)

    def test_lisays_lisaa_saldoa(self):
        """Testaa, että varastoon lisääminen lisää varastossa olevien
        tavaroiden määrää eli saldoa."""
        self.varasto.lisaa_varastoon(8)

        self.assertAlmostEqual(self.varasto.saldo, 8)

    def test_lisays_lisaa_pienentaa_vapaata_tilaa(self):
        """Testaa, että varastoon lisääminen pienentää varastossa jäljellä
        olevaa tilaa."""
        self.varasto.lisaa_varastoon(8)

        # vapaata tilaa pitäisi vielä olla tilavuus-lisättävä määrä eli 2
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_ottaminen_palauttaa_oikean_maaran(self):
        """Testaa, että varastosta ottaminen palauttaa oikean määrän."""
        self.varasto.lisaa_varastoon(8)

        saatu_maara = self.varasto.ota_varastosta(2)

        self.assertAlmostEqual(saatu_maara, 2)

    def test_ottaminen_lisaa_tilaa(self):
        """Testaa, että varastosta ottaminen lisää varastossa jäljellä
        olevaa tilaa."""
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(2)

        # varastossa pitäisi olla tilaa 10 - 8 + 2 eli 4
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 4)

    def test_konstruktori_negatiivinen_tilavuus(self):
        """Testaa, onko varaston tilavuus negatiivinen."""
        varasto = Varasto(-1)
        self.assertAlmostEqual(varasto.tilavuus, 0)

    def test_konstruktori_negatiivinen_alkusaldo(self):
        """Testaa, onko varaston alkusaldo negatiivinen."""
        varasto = Varasto(10, -1)
        self.assertAlmostEqual(varasto.saldo, 0)

    def test_konstruktori_liian_suuri_alkusaldo(self):
        """Testaa, onko alkusaldo suurempi kuin varaston tilavuus."""
        varasto = Varasto(10, 15)
        self.assertAlmostEqual(varasto.saldo, 10)

    def test_lisaa_negatiivinen_maara(self):
        """Testaa, jos varastosta otetaan negatiivinen määrä."""
        self.varasto.lisaa_varastoon(-1)
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_lisaa_liikaa(self):
        """Testaa, jos varastoon lisätään enemmän kuin sinne mahtuu."""
        self.varasto.lisaa_varastoon(11)
        self.assertAlmostEqual(self.varasto.saldo, 10)

    def test_ota_negatiivinen_maara(self):
        """Testaa, jos varastosta otetaan negatiivinen määrä."""
        self.varasto.lisaa_varastoon(5)
        saatu_maara = self.varasto.ota_varastosta(-1)
        self.assertAlmostEqual(saatu_maara, 0)
        self.assertAlmostEqual(self.varasto.saldo, 5)

    def test_ota_liikaa(self):
        """Testaa, jos varastosta otetaan enemmän kuin siellä on tavaraa"""
        self.varasto.lisaa_varastoon(5)
        saatu_maara = self.varasto.ota_varastosta(7)
        self.assertAlmostEqual(saatu_maara, 5)
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_str_metodi(self):
        """Testaa merkkijonoesitystä"""
        self.varasto.lisaa_varastoon(5)
        self.assertEqual(str(self.varasto), "saldo = 5, vielä tilaa 5")
