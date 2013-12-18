"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from django.utils import timezone

from models import ErgebnisTO, TippTO, SpielTO, BestenlistenPlatzTO, TabellenPlatzTO
from models import Spielzeit, Spieltag, Spiel, Tipp, Verein
from django.contrib.auth.models import User

ich = anderer = verein1 = verein2 = None
st = sz = None
def createUsers():
    global ich
    ich = User()
    ich.username = "ich"
    ich.save()
    
    global anderer
    anderer = User()
    anderer.username = "anderer User"
    anderer.save()

def createVereine():
    global verein1
    verein1 = Verein()
    verein1.name = "Verein 1"
    verein1.save()
    
    global verein2
    verein2 = Verein()
    verein2.name = "Verein 2"
    verein2.save()

def createSpieltag():
    global sz
    sz = Spielzeit()
    sz.bezeichner = "Test Spielzeit"
    sz.save()
    
    global st
    st = Spieltag()
    st.nummer = 1
    st.datum = timezone.now()
    st.spielzeit = sz;
    st.save()
    
    

class ErgebnisTOTestCase(TestCase):
    def setUp(self):
        pass

    def test_ergebnisse_sieg(self):
        e1 = ErgebnisTO("3:1")
        
        self.assertEqual(e1.heimTore, 3)
        self.assertEqual(e1.auswTore, 1)
        self.assertEqual(e1.toto, 1)
        self.assertEqual(str(e1), "3:1")

    def test_ergebnisse_unentschieden(self):
        e1 = ErgebnisTO("2:2")
        
        self.assertEqual(e1.heimTore, 2)
        self.assertEqual(e1.auswTore, 2)
        self.assertEqual(e1.toto, 0)
        self.assertEqual(str(e1), "2:2")

    def test_ergebnisse_niederlage(self):
        e1 = ErgebnisTO("0:1")
        
        self.assertEqual(e1.heimTore, 0)
        self.assertEqual(e1.auswTore, 1)
        self.assertEqual(e1.toto, 2)
        self.assertEqual(str(e1), "0:1")
        
class TippTOTestCase(TestCase):
    s = None
    def setUp(self):
        createUsers()
        createVereine()
        createSpieltag()
        self.s = Spiel()
        self.s.heimmannschaft = verein1
        self.s.auswaertsmannschaft = verein2
        self.s.ergebniss = "2:1"
        self.s.spieltag = st
        self.s.save()
        

    def test_tipp_richtig(self):
        t = Tipp()
        t.spiel = self.s
        t.ergebniss = "2:1"
        t.user = ich
        t.save()
        
        to = TippTO(t)
        
        self.assertEqual(str(to), "2:1(3)")
    def test_tipp_falsch(self):
        t = Tipp()
        t.spiel = self.s
        t.ergebniss = "1:2"
        t.user = ich
        t.save()
        
        to = TippTO(t)
        
        self.assertEqual(str(to), "1:2(0)")
    def test_tipp_differenz(self):
        t = Tipp()
        t.spiel = self.s
        t.ergebniss = "3:2"
        t.user = ich
        t.save()
        
        to = TippTO(t)
        
        self.assertEqual(str(to), "3:2(2)")
    def test_tipp_tendenz(self):
        t = Tipp()
        t.spiel = self.s
        t.ergebniss = "3:1"
        t.user = ich
        t.save()
        
        to = TippTO(t)
        
        self.assertEqual(str(to), "3:1(1)")
        
    def test_tipp_none(self):
        to = TippTO(None)

class SpielTOTestCase(TestCase):
    s = None
    def setUp(self):
        createUsers()
        createVereine()
        createSpieltag()
        self.s = Spiel()
        self.s.heimmannschaft = verein1
        self.s.auswaertsmannschaft = verein2
        self.s.ergebniss = "2:1"
        self.s.spieltag = st
        self.s.save()

    def test_spiel(self):
        spiel = SpielTO(self.s)
        
        self.assertEqual(str(spiel), "%s vs %s: %s" % (str(self.s.heimmannschaft), str(self.s.auswaertsmannschaft), self.s.ergebniss))

class BestenlistenplatzTOTestCase(TestCase):
    def setUp(self):
        createUsers()
        pass

    def test_bestenlistenplatz(self):
        blp = BestenlistenPlatzTO(2, ich, 13)
        
        self.assertEqual(str(blp), "2. ich 13")

class TabellenplatzTOTestCase(TestCase):
    def setUp(self):
        createVereine()
        pass

    def test_tabellenplatz(self):
        p1 = TabellenPlatzTO(1, verein1, 63, 13, 99)
        p2 = TabellenPlatzTO(2, verein2, 61, 13, 88)
        
        self.assertEqual(str(p1), "1. Verein 1 63 13 99")
        self.assertEqual(str(p2), "2. Verein 2 61 13 88")