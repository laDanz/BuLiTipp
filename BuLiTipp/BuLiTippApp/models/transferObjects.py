#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

'''
Created on 18.12.2013

@author: ladanz

Contains transfer objects for front end visualization.
'''
from sets import Set
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
		if self.heimTore == None or self.auswTore == None:
				return "DNF"
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
		self.id = spiel.id
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
		return "%s vs %s: %s" % (unicode(self.heimTeam), unicode(self.auswTeam), self.ergebnis)
	def __str__(self):
		return unicode(self)

class SpieltagTO(object):
	def __init__(self, spieltag=None, spieleTOs=[], vollstaendigGetippt={}, naechster=None, vorheriger=None, bestenliste=None):
		self.id = spieltag.id
		self.bezeichner = spieltag.bezeichner
		self.nummer = spieltag.nummer
		self.datum = spieltag.datum
		self.spiele = spieleTOs
		self.tippbar = spieltag.is_tippable()
		self.vollstaendig_getippt = vollstaendigGetippt
		if naechster != None:
				self.naechster = SpieltagTO(naechster)
		if vorheriger != None:
				self.vorheriger = SpieltagTO(vorheriger)
		self.bestenliste = bestenliste
		self.tippbare_spiele = 0
		for spiel in spieleTOs:
			if spiel.tippbar:
				self.tippbare_spiele += 1
	def __unicode__(self):
		return "Spieltag %s(%s)" % (str(self.nummer), unicode(self.bezeichner))
	def __str__(self):
		return unicode(self)

class SpielzeitBezeichnerTO(object):
	def __init__(self, spielzeit=None):
		self.id = spielzeit.id
		self.bezeichner = spielzeit.bezeichner
		self.istPokal = spielzeit.isPokal
		self.tippbar = spielzeit.is_tippable()
		self.tippbar_bis = spielzeit.saisontipp_end
	def __unicode__(self):
		return "Spielzeit %s(Pokal:%s)" % (self.bezeichner, self.istPokal)
	def __str__(self):
		return unicode(self)

class SpielzeitTO(SpielzeitBezeichnerTO):
	def __init__(self, spielzeit=None, aktueller_spieltagTO=None, tabelle=None, bestenliste=None, spieltage=None):
		super(SpielzeitTO, self).__init__(spielzeit)
		self.aktuellerSpieltag = aktueller_spieltagTO
		self.tabelle = tabelle
		self.bestenliste = bestenliste
		self.spieltage = spieltage

class BestenlistenPlatzTO(object):
	def __init__(self, position=None, user=None, punkte=None):
		self.position = position
		self.user = user
		self.punkte = punkte
	def __unicode__(self):
		return "%s. %s %s" % (str(self.position), unicode(self.user.username), self.punkte)
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
	def reduce(self, plaetze_amount=10, user_id=None):
		''' Reduce the size of the bestenlist to the given amount, keeping the user inside, if given.
			Smallest possible plaetze_amount seems to be 9.(first three, last three, three around the user)
		'''
		help_position = 1
		for blp in self.bestenlistenPlatz:
			blp.help_position = help_position
			help_position += 1
		user_platz = 1
		if user_id:
			for blp in self.bestenlistenPlatz:
				if blp.user and blp.user.id and blp.user.id == user_id:
					user_platz = blp.help_position
					break
		max_platz = self.bestenlistenPlatz[-1].help_position
		shown_plaetze = Set([1,2,3,max_platz, max_platz-1, max_platz-2, user_platz])
		if user_platz > 1:
			shown_plaetze.add(user_platz-1)
		if user_platz < max_platz:
			shown_plaetze.add(user_platz+1)
		# fill with first unoccured spaces
		it = iter(self.bestenlistenPlatz)
		while len(shown_plaetze)<max_platz and len(shown_plaetze)<plaetze_amount:
			 blp = it.next()
			 shown_plaetze.add(blp.help_position)
		# the final reduce
		for blp in self.bestenlistenPlatz[:]:
			if not blp.help_position in shown_plaetze:
				self.bestenlistenPlatz.remove(blp)


class TabellenPlatzTO(object):
	def __init__(self, position=None, verein=None, punkte=None, spiele=None, tore=None):
		self.position = position
		self.verein = verein
		self.punkte = punkte
		self.spiele = spiele
		self.tore = tore
	def __unicode__(self):
		return "%s. %s %s %s %s" % (str(self.position), unicode(self.verein.name), self.punkte, self.spiele, self.tore)
	def __str__(self):
		return unicode(self)

class TabelleTO(object):
	def __init__(self, plaetze=[], spielzeitTO=None, spieltagTO=None):
		self.tabellenPlatz = plaetze
		self.spieltag = spieltagTO
		self.spielzeit = spielzeitTO
