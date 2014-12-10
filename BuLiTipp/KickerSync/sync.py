import urllib2
from tidylib import tidy_document
import lxml.etree as lET
import xml.etree.ElementTree as ET

from datetime import datetime, date, timedelta
from KickerSync import transformation
from BuLiTippApp.models import Spiel, Verein
from KickerSync.models import SpieltagXMLData

'''enabling debug mode can cause encoding problems'''
DEBUG = False


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
		return lET.fromstring(old_object.xmldata)
	url = getUrlFromSpieltag(spieltag)
	data = urllib2.urlopen(url)
	data_read=data.read()
	if DEBUG:
		print "response from URL " + url
		print data_read
	document, errors = tidy_document(data_read, options={'numeric-entities':1, 'output-xml':1})
	#fix cdata
	document=document.replace("]]>", "<!-- ]]> -->")
	document=document.replace("&#160;", " ")
	document="<?xml version='1.0' encoding='ISO-8859-1' ?>"+document
	if DEBUG:
		print "tidylib document"
		print document
		print "tidylib errors"
		print errors
	dom = lET.fromstring(document)
	xslt =lET.fromstring(transformation.transformation)
	transform = lET.XSLT(xslt)
	newdom = transform(dom)
	if DEBUG:
		print "dom after transformation"
		print(lET.tostring(newdom, pretty_print=True))
	xmldata=SpieltagXMLData()
	xmldata.spieltagid=spieltag.id
	xmldata.xmldata=lET.tostring(newdom)
	xmldata.save()
	if DEBUG:
		print "Saved XMLData for Spieltag " +str(spieltag.id) +" to DB"
	return newdom.getroot()


def compareSpieltag(spieltag):
	root = getSpieltagData(spieltag)
	assert root.tag == 'spieltag'
	spiele = []
	# first_datum is the date of the spieltag, according to sync data
	first_datum = None
	for spiel in spieltag.spiel_set.all().order_by("datum"):
		spiele.append(spiel)
		for xmlspiel in root:
			time = xmlspiel.find('zeitpunkt').text
			format = xmlspiel.find('zeitpunkt').get('format')
			# default year, if none was given
			if not (("%y" in format) or ("%Y" in format)):
				format = format + " %Y"
				time = time + " " + str(date.today().year)
			localspiel = Spiel()
			hm = findMannschaft(xmlspiel.find('heimmannschaft').text)
			if(hm):
				localspiel.heimmannschaft = hm
			am = findMannschaft(xmlspiel.find('auswmannschaft').text)
			if(am):
				localspiel.auswaertsmannschaft = am
			localspiel.datum = datetime.strptime(time, format)
			localspiel.ergebniss = xmlspiel.find('ergebnis').text
			if first_datum == None or first_datum > localspiel.datum:
				first_datum = localspiel.datum
			if (compareSpiel(spiel, localspiel)):
				break
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
	v=Verein.objects.filter(name__icontains=name)
	if v.count()==1:
		if DEBUG:
			print "found Verein " + name
		return v[0]
	if DEBUG:
		print "Verein " + name + " not found"
	return None;


def getUrlFromSpieltag(spieltag):
	url="http://www.kicker.de/news/fussball/bundesliga/spieltag/1-bundesliga/2014-15/"+ str(spieltag.nummer) +"/0/spieltag.html"
	return url




