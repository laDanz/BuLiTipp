from django.utils import timezone
import string, datetime
from models import Spielzeit, Spiel, Verein, Spieltag

file = "data/DFB_1"
test=False

f = open(file, "r")
spieltag=False
vereine	= []
neue_vereine = []
spielzeit=Spielzeit()
spielzeit.bezeichner="DFB Pokal"
if not test:
	spielzeit.save()
for st in spielzeit.spieltag_set.all():
	st.delete()
stag = None
datum =	None
nummer=0

def retrieveOrCreate(s):
	try:
		v = Verein.objects.filter(name=s)[0]
		return v
	except:
		v = Verein()
		v.name = s
		print "Neuer Verein: %s" % (s,)
		neue_vereine.append(s)
		if not test:
			v.save()
		return v

spieltag=True
for line in f:
#	print "processing: " + line
	if spieltag:
		nummer += 1
		datum =	line.split(",")[0]
		datum =	datum[0:10]
		print "am Datum: " + datum
		v=line.split("-")
		v1=v[0]
		v2=v[1]
		if test:
			print "v2: %s" % (v2)
		v1 = v1.split("\t")[1]
		v1 = string.strip(v1)
		if test:
			print "v2: %s" % (v2.split("\t")[1])
		v2 = string.strip(v2.split("\t")[1])
		if not v1 in vereine:
			vereine.append(v1)
		if not v2 in vereine:
			vereine.append(v2)
		print "v1:"+v1+", v2:"+v2
		spieltag = False
		stag = Spieltag()
		stag.spielzeit=spielzeit
		stag.nummer=nummer
		stag.datum = datetime.datetime.strptime(datum,"%d.%m.%Y")
		if not test:
			stag.save()
		spiel =	Spiel()
		spiel.heimmannschaft=retrieveOrCreate(v1)
		spiel.auswaertsmannschaft=retrieveOrCreate(v2)
		spiel.spieltag=stag
		spiel.ergebniss="DNF"
		if not test:
			spiel.save()
	else:
		v=line.split("-")
		v1=v[0]
		v2=v[1]
		v1 = v1.split("\t")[1]
		v1 = string.strip(v1)
		if test:
			print "v2: %s" % (v2)
		v2 = string.strip(v2.split("\t")[1])
		if not v1 in vereine:
			vereine.append(v1)
		if not v2 in vereine:
			vereine.append(v2)
		print "v1:"+v1+", v2:"+v2
		spiel =	Spiel()
		spiel.heimmannschaft=retrieveOrCreate(v1)
		spiel.auswaertsmannschaft=retrieveOrCreate(v2)
		spiel.spieltag=stag
		spiel.ergebniss="DNF"
		if not test:
			spiel.save()
print str(len(vereine))	+ "Vereine gefunden"
print str(len(neue_vereine)) + "neue Vereine gefunden"

