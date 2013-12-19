#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
import string, datetime
from models import Spielzeit, Spiel, Verein, Spieltag

file = "data/2013_2014"

f = open(file, "r")
spieltag=False
vereine	= []

spielzeit=Spielzeit()
spielzeit.bezeichner="2013/2014"
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
		v.save()
		return v


for line in f:
#	print "processing: " + line
	if spieltag:
		nummer += 1
		datum =	line.split()[0]
		datum =	datum[0:10]
		print "am Datum: " + datum
		v=line.split("-")
		offset=0
		if len(v) > 4:
			offset=4
		v1=v[0+offset]
		v2=v[1+offset]
		v1 = v1.split("Uhr")[1]
		v1 = string.strip(v1)
		v2 = string.strip(v2)
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
		stag.save()
		spiel =	Spiel()
		spiel.heimmannschaft=retrieveOrCreate(v1)
		spiel.auswaertsmannschaft=retrieveOrCreate(v2)
		spiel.spieltag=stag
		spiel.ergebniss="DNF"
		spiel.save()
	elif line.split()[1].startswith("SPIELTAG"):
		print "encountered SPIELTAG" + line
		spieltag = True
	else:
		v=line.split("-")
		offset=0
		if len(v) > 4:
			offset=4
		v1=v[0+offset]
		v2=v[1+offset]
		v1 = v1.split("Uhr")[1]
		v1 = string.strip(v1)
		v2 = string.strip(v2)
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
		spiel.save()
print str(len(vereine))	+ "Vereine gefunden"

