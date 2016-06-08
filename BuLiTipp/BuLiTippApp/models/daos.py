# -*- coding: utf-8 -*-
'''
Created on 19.12.2013

@author: ladanz
'''
from django.contrib.auth.models import User
from transferObjects import BestenlistenPlatzTO, BestenlisteTO, TabellenPlatzTO, TabelleTO
from models_statistics import Tabelle
from models import Spielzeit, Tippgemeinschaft, Verein
import collections
from sets import Set

class BestenlisteDAO():
	@staticmethod
	def all(user_id=None, full=True):
		return BestenlisteDAO.query(user_id=user_id, full=full)
	@staticmethod
	def spieltag(spieltag_id, user_id=None, full=True, plaetze_amount=10):
		return BestenlisteDAO.query(spieltag_id=spieltag_id, user_id=user_id, full=full, plaetze_amount=plaetze_amount)
	@staticmethod
	def spielzeit(spielzeit_id, user_id=None, full=True, aktuell_spieltag_id=None, tg_oriented=True, plaetze_amount=10):
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
		aktuell = BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full, aktuell_spieltag_id=aktuell_spieltag_id, tg_oriented=tg_oriented, plaetze_amount=plaetze_amount)
		vorher = BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full, aktuell_spieltag_id=before_spieltag_id, tg_oriented=tg_oriented, plaetze_amount=plaetze_amount)
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
	def query(user_id=None, full=True, spieltag_id=None, spielzeit_id=None, aktuell_spieltag_id=None, tg_oriented=True, plaetze_amount=10):
		''' Result: {tg:bestenlistTO}
		'''
		from models_statistics import Punkte
		result={}
		if user_id and tg_oriented:
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
			if user_id and tg_oriented:
				users = tg.users.all()
			elif user_id:
				#users from all tgs i'm in?
				tgs = Tippgemeinschaft.objects.filter(users=user_id).filter(spielzeit__id=spielzeit_id)
				users_from_tg = Set()
				for tg in tgs:
					users_from_tg = users_from_tg.union(Set([u["id"] for u in tg.users.values()]))
				users = User.objects.filter(id__in=users_from_tg)
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
			last_points = -1
			plaetze_skipped = 0
			for bl in blp:
				if(bl.punkte == last_points):
					plaetze_skipped += 1
				else:
					plaetze_skipped = 0
				bl.position = platz - plaetze_skipped
				platz += 1
				last_points = bl.punkte
			# TODO: muss noch gefuellt werden?
			bl = BestenlisteTO(blp, None, None)
			if user_id and tg_oriented:
				bl.reduce(user_id = user_id, plaetze_amount=plaetze_amount)
				result[tg] = bl
			else:
				if not full:
					bl.reduce(user_id = user_id, plaetze_amount=plaetze_amount)
				return {"":bl}
		if user_id and tg_oriented:
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
				try:
					punkte = sum(punkte)*10/len(users)/10.
				except:
					punkte = 0
				user = User()
				user.username = tg.bezeichner
				user.id = tg.bezeichner
				blp.append(BestenlistenPlatzTO(None, user, punkte))
			#Spieler selbst zur Übersicht hinzufügen
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
			tg.id = 99999 #fixme
			tg.bezeichner = "Übersicht"
			blp.sort(key=lambda blp:blp.punkte, reverse=True)
			platz = 1
			last_points = -1
			plaetze_skipped = 0
			for bl in blp:
				if(bl.punkte == last_points):
					plaetze_skipped += 1
				else:
					plaetze_skipped = 0
				bl.position = platz - plaetze_skipped
				platz += 1
				last_points = bl.punkte
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
