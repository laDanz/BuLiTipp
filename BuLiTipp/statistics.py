from BuLiTippApp.models import Spiel, Spielzeit, Tipp, Punkte
from django.contrib.auth.models import User
from operator import itemgetter
from django.utils import timezone

sz=Spielzeit.objects.get(pk=2)

print '+++++++++++'
print 'statistics for %s' % sz.bezeichner

print "+++ ST-Nummer: Punkte  +++"
st_punkte={}
for st in sz.spieltag_set.filter(datum__lte = timezone.now()):
	pkt=sum(Punkte.objects.filter(spieltag_id=st.id))
	st_punkte[st.nummer]=pkt
print sorted(st_punkte.iteritems(), key=itemgetter(1), reverse=True)

print '+++ Spiel: Punkte +++'
s_punkte={}
for s in Spiel.objects.filter(spieltag__spielzeit_id=sz.id).filter(datum__lte = timezone.now()):
	tipps=Tipp.objects.filter(spiel_id=s.id)
	pkt=0
	for tipp in tipps:
		p=tipp.punkte()
		if p != None:
			pkt=pkt+p
	s_punkte[unicode(s)+":"+s.ergebniss]=pkt
s_punkte=sorted(s_punkte.iteritems(), key=itemgetter(1), reverse=True)
print " ++ beste"
print s_punkte[:3]
print " ++ schlechteste"
print s_punkte[-3:]

print "+++ User: getippte Tore  +++"
user_tore={}
for user in User.objects.filter(id__lt=13):
	tore=0
	for tipp in Tipp.objects.filter(user_id=user.id):
		if tipp.ergebniss != None and tipp.ergebniss != "":
			tore= tore + int(tipp.ergebniss.split(":")[0]) + int(tipp.ergebniss.split(":")[1])
	user_tore[user.username]=tore
user_tore=sorted(user_tore.iteritems(), key=itemgetter(1), reverse=True)
print user_tore

tore=0
for s in Spiel.objects.filter(spieltag__spielzeit_id=sz.id).filter(datum__lte = timezone.now()):
	if s.ergebniss != None and s.ergebniss != "" and s.ergebniss !="DNF":
		tore= tore + int(s.ergebniss.split(":")[0]) + int(s.ergebniss.split(":")[1])
print "soviel Tore waren es in echt: %s" % str(tore)

UNENTSCHIEDEN=("0:0", "1:1", "2:2", "3:3", "4:4", "5:5", )
print "+++ User: Unentschieden  +++"
user_unent={}
user_unent_recht={}
for user in User.objects.filter(id__lt=13):
	unent=0
	recht = 0
	for tipp in Tipp.objects.filter(user_id=user.id):
		if tipp.ergebniss in UNENTSCHIEDEN:
			unent += 1
			if tipp.spiel.ergebniss in UNENTSCHIEDEN:
				recht += 1
	user_unent[user.username]=unent
	user_unent_recht[user.username]=recht
user_unent=sorted(user_unent.iteritems(), key=itemgetter(1), reverse=True)
print user_unent
user_unent_recht=sorted(user_unent_recht.iteritems(), key=itemgetter(1), reverse=True)
print "Recht gehabt:"
print user_unent_recht
unent=0
for s in Spiel.objects.filter(spieltag__spielzeit_id=sz.id).filter(datum__lte = timezone.now()):
	if s.ergebniss in UNENTSCHIEDEN:
		unent += 1
print "soviel Unentschieden waren es in echt: %s" % str(unent)

print "getippte tabelle:"
v_punkte={}
for s in Spiel.objects.filter(spieltag__spielzeit_id=sz.id).filter(datum__lte = timezone.now()):
	tipps=Tipp.objects.filter(spiel_id=s.id)
	hteam = s.heimmannschaft
	ateam = s.auswaertsmannschaft
	hpkt=v_punkte[hteam] if hteam in v_punkte.keys() else 0
	apkt=v_punkte[ateam] if ateam in v_punkte.keys() else 0
	for tipp in tipps:
		try:
			h = int(tipp.ergebniss.split(":")[0])
			v = int(tipp.ergebniss.split(":")[1])
			if h > v:
				hpkt += 3
			elif h < v:
				apkt += 3
			else:
				hpkt += 1
				apkt += 1
		except:
			pass
	v_punkte[hteam]=hpkt
	v_punkte[ateam]=apkt
v_punkte=sorted(v_punkte.iteritems(), key=itemgetter(1), reverse=True)
print v_punkte

print ""
print "=== Pechvoegel ==="
print "use special punktecalculator, and refreshStatistics"
print "same for toto ergebnisse"
