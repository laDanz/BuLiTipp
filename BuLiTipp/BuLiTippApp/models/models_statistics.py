from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from punkterechner import Punkterechner
from models import Spielzeit, Verein

# Create your models here.

class Tabelle(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
        spielzeit = models.ForeignKey(Spielzeit)
        platz = models.IntegerField()
        mannschaft = models.ForeignKey(Verein)
        punkte = models.IntegerField()
        def __unicode__(self):
                return "%s: %s(%s)" % (str(self.platz), unicode(self.mannschaft), str(self.punkte))
        def getMannschaftPlatz(self, spielzeit):
                if (spielzeit is not None):
                        sid = spielzeit.id
                else:
                        sid = None
                if (sid is None):
                        return {t.mannschaft.id: t.platz for t in Tabelle.objects.all()}
                else:
                        return {t.mannschaft.id: t.platz for t in Tabelle.objects.filter(spielzeit_id=sid)}
        def refresh(self):
                Tabelle.objects.all().delete()
                pr = Punkterechner()
                #fuer jede spielzeit:
                for sz in Spielzeit.objects.all():
                        #fuer jedes abgelaufene spiel:
                        mannschaft_punkte_tore={}
                        for st in sz.spieltag_set.all():
                               for s in st.spiel_set.all():
                                        #ermittlke punkte und schreibe sie den vereinen gut
                                        m1 = s.heimmannschaft.id
                                        m2 = s.auswaertsmannschaft.id
                                        if (m1 in mannschaft_punkte_tore.keys()):
                                                alt1 = mannschaft_punkte_tore[m1][0]
                                                tor1 = mannschaft_punkte_tore[m1][1]
                                        else:
                                                alt1 = 0
						tor1 = 0
                                        if (m2 in mannschaft_punkte_tore.keys()):
                                                alt2 = mannschaft_punkte_tore[m2][0]
                                                tor2 = mannschaft_punkte_tore[m2][1]
                                        else:
                                                alt2 = 0
						tor2 = 0
                                        try:
                                                toto = pr.toto(s.ergebniss)
                                        except:
                                                continue
                                        if (toto == 1):
                                                p1=3
                                                p2=0						
                                        elif (toto == 2):
                                                p1=0
                                                p2=3
                                        elif (toto == 0):
                                                p1=1
                                                p2=1
					diff = pr.diff(s.ergebniss)
                                        mannschaft_punkte_tore[m1]=[alt1 + p1, tor1-diff]
                                        mannschaft_punkte_tore[m2]=[alt2 + p2, tor2+diff]
                        mannschaft_punkte_tore = sorted(mannschaft_punkte_tore.iteritems(), key=lambda (k, v): (-v[0]*1000-v[1], k) )
                        for (i, v) in enumerate(mannschaft_punkte_tore):
                                t=Tabelle()
                                t.spielzeit = sz
                                t.platz = i+1
				print v
                                t.mannschaft_id = v[0]
                                t.punkte = v[1][0]
                                t.save()

