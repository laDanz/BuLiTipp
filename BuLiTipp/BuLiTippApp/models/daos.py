# -*- coding: utf-8 -*-
'''
Created on 19.12.2013

@author: ladanz
'''
from django.contrib.auth.models import User
from itertools import chain
from transferObjects import BestenlistenPlatzTO, BestenlisteTO, TabellenPlatzTO, TabelleTO
from models_statistics import Tabelle
from models import Spielzeit, Spieltag, Tippgemeinschaft, Verein
import collections
from sets import Set

class BestenlisteDAO():
	@staticmethod
	def all(user_id=None, full=True):
		return BestenlisteDAO.query(user_id=user_id, full=full)
	@staticmethod
	def spieltag(spieltag_id, user_id=None, full=True):
		return BestenlisteDAO.query(spieltag_id=spieltag_id, user_id=user_id, full=full)
	@staticmethod
	def spielzeit(spielzeit_id, user_id=None, full=True, aktuell_spieltag_id=None):
		'''aktuell_spieltag_id : calculate all Punkte til that spieltag. Result will include Punkte from the given spieltag.
		'''
		sz = Spielzeit.objects.get(pk=spielzeit_id)
		if aktuell_spieltag_id == None:
			try:
				if sz.has_ended():
					before_spieltag_id = sz.next_spieltag().previous().id
				else:
					before_spieltag_id = sz.next_spieltag().previous().previous().id
			except:
				before_spieltag_id = 0
		else:
			# actually inaccurate, but sufficient and faster
			before_spieltag_id = int(aktuell_spieltag_id)-1
		aktuell = BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full, aktuell_spieltag_id=aktuell_spieltag_id)
		vorher = BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full, aktuell_spieltag_id=before_spieltag_id)
		if hasattr(aktuell, "keys"):
			for k in aktuell.keys():
				for blp in aktuell[k].bestenlistenPlatz:
					for blp_old in vorher[k].bestenlistenPlatz:
						if blp.user == blp_old.user:
							blp.delta = blp_old.position - blp.position
							break
		else:
			for blp in aktuell[0].bestenlistenPlatz:
				for blp_old in vorher[0].bestenlistenPlatz:
					if blp.user == blp_old.user:
						blp.delta = blp_old.position - blp.position
						break
		return aktuell
	@staticmethod
	def query(user_id=None, full=True, spieltag_id=None, spielzeit_id=None, aktuell_spieltag_id=None):
		''' Result: {tg:bestenlistTO}
		'''
		from models_statistics import Punkte
		result={}
		if user_id:
			tgs = Tippgemeinschaft.objects.filter(users__id = user_id)
			if spieltag_id:
				tgs = tgs.filter(spielzeit__spieltag__id = spieltag_id)
			if spielzeit_id:
				tgs = tgs.filter(spielzeit__id = spielzeit_id)
		else:
			tgs = [1]
		#tgs des users
		for tg in tgs:
			blp=[]
			if user_id:
				users = tg.users.all()
			else:
				users = User.objects.filter(is_active = True).filter(groups = 1)# FIXME?
			for user in users:
				punkte = Punkte.objects.filter(user=user)
				if spieltag_id is not None:
					punkte = punkte.filter(spieltag__id=spieltag_id)
				if spielzeit_id is not None:
					punkte = punkte.filter(spieltag__spielzeit_id=spielzeit_id)
				if aktuell_spieltag_id is not None:
					punkte = punkte.filter(spieltag__id__lte=aktuell_spieltag_id)
				#summiere die punkte der Tipps
				punkte = sum(punkte)
				blp.append(BestenlistenPlatzTO(None, user, punkte))
			blp.sort(key=lambda blp:blp.punkte, reverse=True)
			platz = 1
			for bl in blp:
				bl.position = platz
				platz += 1
			# TODO: muss noch gefuellt werden?
			if user_id:
				bl = BestenlisteTO(blp, None, None)
				bl.reduce(user_id = user_id)
				result[tg] = bl
			else:
				return {"":BestenlisteTO(blp, None, None)}
		if user_id:
			if spieltag_id:
				tgs = Tippgemeinschaft.objects.filter(spielzeit__spieltag__id = spieltag_id)
			if spielzeit_id:
				tgs = Tippgemeinschaft.objects.filter(spielzeit__id = spielzeit_id)
			blp=[]
			#alle tgs dieser spielzeit/spieltag für übersicht zusammenrechnen
			for tg in tgs:
				users = tg.users.all()
				punkte = Punkte.objects.filter(user__in=users)
				if spieltag_id is not None:
					punkte = punkte.filter(spieltag__id=spieltag_id)
				if spielzeit_id is not None:
					punkte = punkte.filter(spieltag__spielzeit_id=spielzeit_id)
				if aktuell_spieltag_id is not None:
					punkte = punkte.filter(spieltag__id__lte=aktuell_spieltag_id)
				punkte = sum(punkte)*10/len(users)/10.
				user = User()
				user.username = tg.bezeichner
				user.id = tg.bezeichner
				blp.append(BestenlistenPlatzTO(None, user, punkte))
			if len(result) == 0 or 1 :#FIXME immer anzeigen?
				#falls net in TG, Spieler selbst zur Übersicht hinzufügen
				user = User.objects.get(pk=user_id)
				punkte = Punkte.objects.filter(user=user)
				if spieltag_id is not None:
					punkte = punkte.filter(spieltag__id=spieltag_id)
				if spielzeit_id is not None:
					punkte = punkte.filter(spieltag__spielzeit_id=spielzeit_id)
				if aktuell_spieltag_id is not None:
					punkte = punkte.filter(spieltag__id__lte=aktuell_spieltag_id)
				#summiere die punkte der Tipps
				punkte = sum(punkte)
				blp.append(BestenlistenPlatzTO(None, user, punkte))
			tg = Tippgemeinschaft()
			tg.bezeichner = "Übersicht"
			blp.sort(key=lambda blp:blp.punkte, reverse=True)
			platz = 1
			for bl in blp:
				bl.position = platz
				platz += 1
			result[tg] = BestenlisteTO(blp, None, None)
		result = collections.OrderedDict(sorted(result.items(),key=lambda t:t[0].id, reverse=False))
		return result

class TabelleDAO():
	@staticmethod
	def spielzeit(spielzeit_id):
		tp = []
		tabellenplatz = Tabelle.objects.filter(spielzeit_id = spielzeit_id).order_by("platz")
		for t in tabellenplatz:
			# TODO: implement tore, spiele
			tp.append(TabellenPlatzTO(t.platz, t.mannschaft, t.punkte, 0, 0))
		# TODO: muss noch gefuellt werden?
		return TabelleTO(tp, None, None)

class VereinDAO():
	@staticmethod
	def spielzeit(spielzeit_id):
		verein = Set(Verein.objects.filter(auswaertsmannschaft__spieltag__spielzeit_id=spielzeit_id))
		verein.union( Set(Verein.objects.filter(heimmannschaft__spieltag__spielzeit_id=spielzeit_id)) )
		return sorted(verein, key=lambda verein: verein.name)