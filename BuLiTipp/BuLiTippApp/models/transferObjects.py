'''
Created on 18.12.2013

@author: ladanz

Contains transfer objects for front end visualization.
'''

from punkterechner import Punkterechner

class NewsTO(object):

    def __init__(self, news):
        self.news = news
        self.anzahl_insg = news.count()
        # TODO: implement for real
        self.anzahl_ungelesen = self.anzahl_insg

class ErgebnisTO(object):
    '''
    "toto" steht fuer die toto Representation dieses Spiels, also 1, wenn Sieg Heimmannschaft; 2, wenn Sieg Auswaertsmannschaft; 0, wenn unentschieden 
    '''
    def __init__(self, ergebnis=None):
        try:
            self.heimTore = int(ergebnis.split(":")[0])
            self.auswTore = int(ergebnis.split(":")[1])
            self.toto = Punkterechner().toto(ergebnis)
        except:
            self.heimTore = None
            self.auswTore = None
            self.toto = None
    def __unicode__(self):
        return "%s:%s" % (self.heimTore, self.auswTore)
    def __str__(self):
        return unicode(self)

class TippTO(object):
    def __init__(self, tipp=None):
        try:
            self.user = tipp.user
            self.ergebnis = ErgebnisTO(tipp.ergebniss)
            self.punkte = tipp.punkte()
        except:
            self.user = None
            self.ergebnis = None
            self.punkte = None
    def __unicode__(self):
        return "%s(%s)" % (self.ergebnis, self.punkte)
    def __str__(self):
        return unicode(self)

class SpielTO(object):
    def __init__(self, spiel=None, eigenerTipp=None, andereTipps=[]):
        self.heimTeam = spiel.heimmannschaft
        self.auswTeam = spiel.auswaertsmannschaft
        self.ergebnis = ErgebnisTO(spiel.ergebniss)
        self.datum = spiel.datum
        self.tippbar = spiel.is_tippable()
        self.eigenerTipp = TippTO(eigenerTipp)
        andere = []
        for tipp in andereTipps:
            andere.append(TippTO(tipp))
        self.andereTipps = andere
    def __unicode__(self):
        return "%s vs %s: %s" % (str(self.heimTeam), str(self.auswTeam), self.ergebnis)
    def __str__(self):
        return unicode(self)

class SpieltagTO(object):
    def __init__(self, spieltag=None, spieleTOs=[], vollstaendigGetippt=False, naechster=None, vorheriger=None):
        self.bezeichner = spieltag.bezeichner
        self.nummer = spieltag.nummer
        self.datum = spieltag.datum
        self.spiele = spieleTOs
        self.vollstaendig_getippt = vollstaendigGetippt
        if naechster != None:
            self.naechster = SpieltagTO(naechster)
        if vorheriger != None:
            self.vorheriger = SpieltagTO(vorheriger)
    def __unicode__(self):
        return "Spieltag %s(%s)" % (str(self.nummer), self.bezeichner)
    def __str__(self):
        return unicode(self)

class SpielzeitTO(object):
    def __init__(self, spielzeit=None, aktueller_spieltagTO=None, tabelle=None, bestenliste=None):
        self.bezeichner = spielzeit.bezeichner
        self.istPokal = spielzeit.isPokal
        self.aktuellerSpieltag = aktueller_spieltagTO
        self.tabelle = tabelle
        self.bestenliste = bestenliste
    def __unicode__(self):
        return "Spielzeit %s(Pokal:%s)" % (self.bezeichner, self.istPokal)
    def __str__(self):
        return unicode(self)

class BestenlistenPlatzTO(object):
    def __init__(self, position=None, user=None, punkte=None):
        self.position = position
        self.user = user
        self.punkte = punkte
    def __unicode__(self):
        return "%s. %s %s" % (str(self.position), self.user.username, self.punkte)
    def __str__(self):
        return unicode(self)

class BestenlisteTO(object):
    '''
    Die Belegung von spieltag und spielzeit gibt die Gueltigkeit dieser Tabelle an.
    Wenn spieltag und spielzeit None sind, dann ist es eine Bestenliste ueber alle Spielzeiten.
    Wenn spieltag gefuellt ist, dann gilt die Bestenliste genau fuer diesen Spieltag.
    Wenn nur spielzeit gefuellt ist, dann gilt die bestenliste fuer die gesamte Spielzeit.
    '''
    def __init__(self, plaetze=[], spielzeitTO=None, spieltagTO=None):
        self.bestenlistenPlatz = plaetze
        self.spieltag = spieltagTO
        self.spielzeit = spielzeitTO

class TabellenPlatzTO(object):
    def __init__(self, position=None, verein=None, punkte=None, spiele=None, tore=None):
        self.position = position
        self.verein = verein
        self.punkte = punkte
        self.spiele = spiele
        self.tore = tore
    def __unicode__(self):
        return "%s. %s %s %s %s" % (str(self.position), self.verein.name, self.punkte, self.spiele, self.tore)
    def __str__(self):
        return unicode(self)

class TabelleTO(object):
    def __init__(self, plaetze=[], spielzeitTO=None, spieltagTO=None):
        self.tabellenPlatz = plaetze
        self.spieltag = spieltagTO
        self.spielzeit = spielzeitTO
