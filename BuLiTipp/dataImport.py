#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
import string, datetime, sys, os, codecs

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BuLiTipp.settings")
	import BuLiTipp.settings
	from BuLiTippApp.models import Spielzeit, Spiel, Verein, Spieltag
	
	print "Datei:\t\t" + sys.argv[1]
	file = sys.argv[1]
	
	#f = open(file, "r")
	f = codecs.open(file, encoding='utf-8')
	spieltag=False
	vereine	= []
	
	spielzeit=Spielzeit()
	
	#BEZEICHNER
	f.readline()
	spielzeit.bezeichner=f.readline()
	
	#SAISONTIPPEND
	f.readline()
	date = f.readline()[:-1]
	spielzeit.saisontipp_end=datetime.datetime.strptime(date, "%d/%m/%Y %H:%M")
	
	#POKAL
	f.readline()
	spielzeit.isPokal = f.readline()[:-1]=='true'
	
	#Confirmation
	print "Bezeichner:	" + spielzeit.bezeichner
	print "Saisontipp Ende	" + unicode(spielzeit.saisontipp_end)
	print "Pokal:		" + unicode(spielzeit.isPokal)
	right = raw_input("Ist dies richtig?")
	if (not right=="y"):
		print "Abbruch!"
		exit(0);
	
	spielzeit.save()
	for st in spielzeit.spieltag_set.all():
		st.delete()
	stag = None
	datum =	None
	last_datum = None
	nummer = 0
	new_vereine = 0
	
	def retrieveOrCreate(s):
		try:
			# TODO: find Verein with similar writing
			v = Verein.objects.filter(name=s)[0]
			return v
		except:
			global new_vereine
			v = Verein()
			v.name = s
			v.save()
			new_vereine += 1
			return v
	
	def parseDate(datum):
		DATA_FORMAT_LONG = [
			'%d/%m/%Y | %H:%M',
			'%d.%m.%Y, %H.%M',
			'%d.%m.%Y'
			]
		''' possible formats:
			%d/%m/%Y | %H:%M
			%H:%M	(uses last parsed date)
		'''
		global last_datum
		for format in DATA_FORMAT_LONG:
			try:
				datum_ = datetime.datetime.strptime(datum, format)
				last_datum = datum_
				return datum_
			except:
				pass
		try:
			uhrzeit = datetime.datetime.strptime(datum,"%H:%M")
			datum_ = last_datum.replace(hour=uhrzeit.hour, minute=uhrzeit.minute)
			return datum_
		except:
			pass
	
	for line in f:
		#FORMAT
		# Date(in different formats)	<TAB>	Verein1	<TAB>	<TRENNER>	<TAB>	Verein2
		print "processing: " + unicode(line)
		if spieltag:
			nummer += 1
			v=line.split("\t")
			datum =	v[0]
			v1=string.strip(v[1])
			v2=string.strip(v[3])
			print "am Datum: " + datum
			if not v1 in vereine:
				vereine.append(v1)
			if not v2 in vereine:
				vereine.append(v2)
			print "v1:"+v1+", v2:"+v2
			spieltag = False
			stag = Spieltag()
			stag.spielzeit=spielzeit
			stag.nummer=nummer
			# datum
			stag.datum = parseDate(datum)
			
			stag.save()
			spiel =	Spiel()
			spiel.heimmannschaft=retrieveOrCreate(v1)
			spiel.auswaertsmannschaft=retrieveOrCreate(v2)
			spiel.spieltag=stag
			spiel.ergebniss="DNF"
			spiel.datum = parseDate(datum)
			spiel.save()
		elif line.startswith("SPIELTAG"):
			print "encountered SPIELTAG" + line
			spieltag = True
		elif line.startswith('"'):
			print "encountered BEZEICHNER" + line
			stag.bezeichner = line.split('"')[1]
			stag.save()
		else:
			v=line.split("\t")
			datum =	v[0]
			v1=string.strip(v[1])
			v2=string.strip(v[3])
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
			spiel.datum = parseDate(datum)
			print "datum: " + unicode(spiel.datum)
			spiel.save()
	print str(len(vereine))	+ "Vereine gefunden"
	print str(new_vereine) + "neue Vereine gefunden!"

