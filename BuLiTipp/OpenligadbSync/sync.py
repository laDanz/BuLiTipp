import urllib2, json, sys

from datetime import datetime, date, timedelta
from BuLiTippApp.models import Spiel, Verein
from OpenligadbSync.models import SpieltagXMLData

'''enabling debug mode can cause encoding problems'''
DEBUG = True


def syncSpieltag(compared_spieltag, spielid):
	if (spielid):
		for spiel in compared_spieltag.spiele:
			if(int(spielid)==spiel.id):
				assert spiel.syncresult is not None
				assert spiel.syncresult.datum is not None
				assert spiel.syncresult.ergebniss is not None
				spiel.datum = spiel.syncresult.datum
				spiel.ergebniss = spiel.syncresult.ergebniss
				spiel.save()
	else:
		# no spiel provided to sync, just sync the spieltag datum
		compared_spieltag.datum=compared_spieltag.sync_datum
		compared_spieltag.save()
	return compared_spieltag


def getSpieltagData(spieltag):
	old_object=SpieltagXMLData.objects.filter(spieltagid=spieltag.id)
	if old_object.count()==1:
		if DEBUG:
			print "Found old xmlData for Spieltag " + str(spieltag.id) + " in DB"
		old_object=old_object[0]
		spieltag.syncresult_datum=old_object.datum
		spieltag.syncresult_id=old_object.id
		return json.loads(old_object.xmldata)
	url = getUrlFromSpieltag(spieltag)
	data = urllib2.urlopen(url)
	data_read=data.read()
	encoding=data.headers['content-type'].split('charset=')[-1]
	data_read=unicode(data_read, encoding)
	if DEBUG:
		print "response from URL " + url
		print (data_read).encode('utf-8')
	xmldata=SpieltagXMLData()
	xmldata.spieltagid=spieltag.id
	xmldata.xmldata=data_read
	xmldata.save()
	if DEBUG:
		print "Saved XMLData for Spieltag " +str(spieltag.id) +" to DB"
	return json.loads(data_read)


def compareSpieltag(spieltag):
	root = getSpieltagData(spieltag)
	spiele = []
	# first_datum is the date of the spieltag, according to sync data
	first_datum = None
	for spiel in spieltag.spiel_set.all().order_by("datum"):
		spiele.append(spiel)
		for xmlspiel in root:
			try:
				time = xmlspiel['MatchDateTime']
				format = '%Y-%m-%dT%H:%M:%S'
				localspiel = Spiel()
				hm = findMannschaft(xmlspiel['Team1']['TeamName'])
				if(hm):
					localspiel.heimmannschaft = hm
				am = findMannschaft(xmlspiel['Team2']['TeamName'])
				if(am):
					localspiel.auswaertsmannschaft = am
				localspiel.datum = datetime.strptime(time, format)
				localspiel.ergebniss = 'DNF'
				try:
					for res in xmlspiel['MatchResults']:
						if res['ResultName'] == 'Endergebnis':
							localspiel.ergebniss = str(res['PointsTeam1'])+':'+str(res['PointsTeam2'])
				except:
					print("Unexpected error:", sys.exc_info()[0])
				if first_datum == None or first_datum > localspiel.datum:
					first_datum = localspiel.datum
				if (compareSpiel(spiel, localspiel)):
					break
			except:
				print("Unexpected error:", sys.exc_info()[0])
				raise
	spieltag.spiele=spiele
	# save the parsed date of the spieltag to "sync_datum"
	spieltag.sync_datum=first_datum
	return spieltag

def compareSpiel(spiel, localspiel):
	try:
		if(spiel.heimmannschaft == localspiel.heimmannschaft and spiel.auswaertsmannschaft == localspiel.auswaertsmannschaft):
			spiel.syncresult=localspiel
			if DEBUG:
				print "Found match: " + str(spiel.heimmannschaft) + " vs " + str(spiel.auswaertsmannschaft)
			return True
	except:
		pass
		return False

def findMannschaft(name):
	name=(name).encode('utf-8')
	if DEBUG:
		print "looking for " + name
	v=Verein.objects.filter(name__icontains=name)
	if v.count()==1:
		if DEBUG:
			print "found Verein " + name
		return v[0]
	if DEBUG:
		print "Verein " + name + " not found"
	return None;


def getUrlFromSpieltag(spieltag):
	url="http://www.openligadb.de/api/getmatchdata/em-2016/2016/"
	return url




