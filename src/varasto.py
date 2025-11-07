"""Tämä moduuli sisältää luokan Varasto."""

class Varasto:
    """Varasto on luokka, joka tarjoaa metodeja tavaroiden
    lisäämiseen varastoon,tavaroiden ottamiseen varastosta
    ja antamaan tiedon varaston
    saldosta.
    """
    def __init__(self, tilavuus, alku_saldo = 0):
        """_Alustaa Varasto-olion tilavuudella ja alkusaldolla"""
        self.tilavuus = tilavuus if tilavuus > 0.0 else 0.0

        if alku_saldo < 0.0:
            # virheellinen, nollataan
            self.saldo = 0.0
        elif alku_saldo <= tilavuus:
            # mahtuu
            self.saldo = alku_saldo
        else:
            # täyteen ja ylimäärä hukkaan!
            self.saldo = tilavuus

    # huom: ominaisuus voidaan myös laskea. Ei tarvita erillistä
    #kenttää viela_tilaa tms.
    def paljonko_mahtuu(self):
        """Palauttaa tiedon, paljonko varastossa on tilaa jäljellä."""
        return self.tilavuus - self.saldo

    def lisaa_varastoon(self, maara):
        """Lisää tavaroita varastoon."""
        if maara < 0:
            return
        if maara <= self.paljonko_mahtuu():
            self.saldo = self.saldo + maara
        else:
            self.saldo = self.tilavuus

    def ota_varastosta(self, maara):
        """Ota tavaroita varastosta.
        Palauttaa, paljonko tavaroita voidaan ottaa"""
        if maara < 0:
            return 0.0
        if maara > self.saldo:
            kaikki_mita_voidaan = self.saldo
            self.saldo = 0.0

            return kaikki_mita_voidaan

        self.saldo = self.saldo - maara

        return maara

    def __str__(self):
        """Palauttaa Varasto-oliosta merkkijonoesityksen,
        joka sisältää varaston saldon ja paljonko varastossa
        on tilaa jäljellä"""
        return f"""saldo = {self.saldo}, vielä tilaa {self.paljonko_mahtuu()}"""
