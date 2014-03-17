#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models	import User
from punkterechner import Punkterechner
from models import Spielzeit, Verein, Spiel, Spieltag, Tipp

# Create your models here.

SERIE_ANZAHL_LETZTER_SPIELE	= 5

class Tabelle(models.Model):
	class Meta:
		app_label =	'BuLiTippApp'
	spielzeit =	models.ForeignKey(Spielzeit)
	platz =	models.IntegerField()
	mannschaft = models.ForeignKey(Verein)
	punkte = models.IntegerField()
	def	__unicode__(self):
			return "%s:	%s(%s)"	% (str(self.platz),	unicode(self.mannschaft), str(self.punkte))
	def	getMannschaftPlatz(self, spielzeit):
			if (spielzeit is not None):
					sid	= spielzeit.id
			else:
					sid	= None
			if (sid	is None):
					return {t.mannschaft.id: t.platz for t in Tabelle.objects.all()}
			else:
					return {t.mannschaft.id: t.platz for t in Tabelle.objects.filter(spielzeit_id=sid)}
	def	refresh(self):
			Tabelle.objects.all().delete()
			pr = Punkterechner()
			#fuer jede spielzeit:
			for	sz in Spielzeit.objects.all():
					#fuer jedes	abgelaufene	spiel:
					mannschaft_punkte_tore={}
					for	st in sz.spieltag_set.all():
						for	s in st.spiel_set.all():
							#ermittlke punkte und schreibe sie den vereinen	gut
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
							if (toto ==	1):
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
					mannschaft_punkte_tore = sorted(mannschaft_punkte_tore.iteritems(),	key=lambda (k, v): (-v[0]*1000-v[1], k)	)
					for	(i,	v) in enumerate(mannschaft_punkte_tore):
							t=Tabelle()
							t.spielzeit	= sz
							t.platz	= i+1
							t.mannschaft_id	= v[0]
							t.punkte = v[1][0]
							t.save()

class Serie(models.Model):
	class Meta:
		app_label =	'BuLiTippApp'
	spielzeit =	models.ForeignKey(Spielzeit)
	mannschaft = models.ForeignKey(Verein)
	siege =	models.IntegerField()
	unent =	models.IntegerField()
	verlo =	models.IntegerField()
	if siege is	None:
		siege =	0
	if unent is	None:
		unent =	0
	if verlo is	None:
		verlo =	0
	def	__unicode__(self):
		return "%s:	%s/%s/%s" %	(unicode(self.mannschaft), str(self.siege),	str(self.unent), str(self.verlo))
	def	getPrintable(self):
		return "%s/%s/%s" %	(str(self.siege), str(self.unent), str(self.verlo))
	def	getSpielzeit(self, spielzeit):
			if (spielzeit is not None):
					sid	= spielzeit.id
			else:
					sid	= None
			if (sid	is None):
					return {t.mannschaft.id: t.getPrintable() for t	in Serie.objects.all()}
			else:
					return {t.mannschaft.id: t.getPrintable() for t	in Serie.objects.filter(spielzeit_id=sid)}
	def	refresh(self):
			Serie.objects.all().delete()
			pr = Punkterechner()
			#fuer jede spielzeit:
			for	sz in Spielzeit.objects.all():
				#fuer jede teilnehmende	mannschaft:
				#for m in sz.
				mannschaften = Verein.objects.filter(Q(heimmannschaft__spieltag__spielzeit_id=sz.id)|Q(auswaertsmannschaft__spieltag__spielzeit_id=sz.id)).distinct()
				for	m in mannschaften:
					serie =	Serie()
					serie.spielzeit	= sz
					serie.mannschaft = m
					serie.siege	= 0
					serie.unent	= 0
					serie.verlo	= 0
					# fuer jedes der letzten x Spiele:
					spiele = Spiel.objects.filter(Q(heimmannschaft_id=m.id)|Q(auswaertsmannschaft_id=m.id)).filter(datum__lt=timezone.now()).order_by('datum').reverse()
					spiele = spiele[:SERIE_ANZAHL_LETZTER_SPIELE]
					for	s in spiele:
						try:
							toto = pr.toto(s.ergebniss)
						except:
							continue
						if (toto ==	1):
							if m ==	s.heimmannschaft:
								serie.siege	+= 1
							else:
								serie.verlo	+= 1
						elif (toto == 2):
							if m ==	s.auswaertsmannschaft:
								serie.siege	+= 1
							else:
								serie.verlo	+= 1
						elif (toto == 0):
							serie.unent	+= 1
					serie.save()

class Punkte(models.Model):
	'''
	Setzt einen	User in	Beziehung zu den Punkten, die er an	einem bestimmten Spieltag erzielt hat.
	'''
	class Meta:
		app_label =	'BuLiTippApp'
	spieltag = models.ForeignKey(Spieltag)
	user = models.ForeignKey(User)
	punkte = models.IntegerField()
	def	__add__(self, x):
		if hasattr(x,"punkte"):
			return self.punkte + x.punkte;
		return self.punkte + x
	def	__radd__(self, x):
		return self.__add__(x)
	def	refresh(self, spieltag_id=None):
		if spieltag_id:
			Punkte.objects.filter(spieltag__id = spieltag_id).delete()
		else:
			Punkte.objects.all().delete()
		#fuer jeden	user
		for	user in	User.objects.all():
			spieltag_punkte={}
			#ermittle alle tipps
			tipps =	Tipp.objects.filter(user_id=user.id)
			if spieltag_id:
				tipps = tipps.filter(spiel__spieltag__id = spieltag_id)
			for	tipp in	tipps:
				punkte = 0 if tipp.punkte()	is None	else tipp.punkte()
				key	= tipp.spiel.spieltag.id
				alt	= spieltag_punkte[key] if key in spieltag_punkte.keys()	else 0
				spieltag_punkte[key] = alt + punkte
			#abspeichern
			for	item in	spieltag_punkte.iteritems():
				p =	Punkte()
				p.spieltag_id =	item[0]
				p.user = user
				p.punkte = item[1]
				p.save()

