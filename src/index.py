"""
Tässä ohjelmassa luodaan kaksi varastoa mehua ja olutta varten.
Ohjelmassa käytetään Varasto-luokan olioita.

- Varastoille määritellään tilavuudet ja alkusaldot.
- Varastoihin lisätään tavaraa tai sieltä otetaan tavaraa
- Tulostetaan varaston saldo tai paljonko sieltä saatiin otettua tavaraa.
- Ohjelmassa käsitellään myös mahdollisia virhetilanteita, jos
alkusaldo tai otettava määrä on negatiivinen.
"""

from varasto import Varasto

def tulosta_varastot(tuote1, tuote2):
    """Tulosta varastot"""
    print()
    print("Luonnin jälkeen:")
    print(f"Mehuvarasto: {tuote1}")
    print(f"Olutvarasto: {tuote2}")

def olut_getter(olutta):
    print("Olut getterit:")
    print(f"saldo = {olutta.saldo}")
    print(f"tilavuus = {olutta.tilavuus}")
    print(f"paljonko_mahtuu = {olutta.paljonko_mahtuu()}")

def mehu_setter(mehua):
    print("Mehu setterit:")
    print("Lisätään 50.7")
    mehua.lisaa_varastoon(50.7)
    print(f"Mehuvarasto: {mehua}")
    print("otetaan 3.14")
    mehua.ota_varastosta(3.14)
    print(f"Mehuvarasto: {mehua}")

def lisaa_olutta(olutta, maara):
    print(f"Olutvarasto: {olutta}")
    print(f"olutta.lisaa_varastoon({maara})")
    olutta.lisaa_varastoon(maara)
    print(f"Olutvarasto: {olutta}")

def lisaa_mehua(mehua, maara):
    print(f"Mehuvarasto: {mehua}")
    print(f"mehua.lisaa_varastoon({maara})")
    mehua.lisaa_varastoon(maara)
    print(f"Mehuvarasto: {mehua}")

def ota_olutta(olutta, maara):
    print(f"Olutvarasto: {olutta}")
    print(f"olutta.ota_varastosta({maara})")
    saatiin = olutta.ota_varastosta(maara)
    print(f"saatiin: {saatiin}")
    print(f"Olutvarasto: {olutta}")

def ota_mehua(mehua, maara):
    print(f"Mehuvarasto: {mehua}")
    print(f"mehua.ota_varastosta({maara})")
    saatiin = mehua.ota_varastosta(maara)
    print(f"saatiin: {saatiin}")
    print(f"Mehuvarasto: {mehua}")

def virhetilanteita(neg_tilavuus1, tilavuus2, neg_saldo2):
    print("Virhetilanteita:")
    print(f"Varasto{neg_tilavuus1}")
    huono = Varasto(neg_tilavuus1)
    print(f"{huono}")

    print(f"Varasto({tilavuus2}, {neg_saldo2})")
    huono = Varasto(tilavuus2, neg_saldo2)
    print(f"{huono}")

def main():
    """Pääohjelma"""
    mehua, olutta = Varasto(100.0), Varasto(100.0, 20.2)

    tulosta_varastot(mehua, olutta)

    olut_getter(olutta)

    mehu_setter(mehua)

    virhetilanteita(-100.0, 100.0, -50.7)

    lisaa_olutta(olutta, 1000.0)

    lisaa_mehua(mehua, -666.0)

    ota_olutta(olutta, 1000.0)

    ota_mehua(mehua, -32.9)

if __name__ == "__main__":
    main()