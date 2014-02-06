#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as djlogin, logout as djlogout
from django.contrib.auth.models import User as djUser, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.template.response import TemplateResponse

from django.db import IntegrityError
from models import Spieltag, Spielzeit, Tipp, Kommentar, News, Meistertipp, Verein, Herbstmeistertipp, Absteiger, Tabelle, Punkte, User, Spiel
from models import NewsTO, SpielzeitTO, SpieltagTO, SpielTO, SpielzeitBezeichnerTO
from models import BestenlisteDAO, TabelleDAO
from datetime import datetime
from sets import Set
from forms import UserModelForm, UserCreateForm

import operator
from django.forms.forms import Form
import mail

### new:
def userform(request):
	context = {}
	context["news"] = get_news_by_request(request)
	user = User.objects.get(pk = request.user.id)
	if request.method == 'POST':
		form = UserModelForm(request.POST, instance = user)
		if form.is_valid():
			form.save()
			messages.success(request, "Erfolgreich gespeichert!")
	else:
		form = UserModelForm(instance=user)
	context["form"] = form
	return render(request, 'user/user.html', context)

def register(request):
	context = {}
	context["news"] = get_news_by_request(request)
	user = User()
	if request.method == 'POST':
		form = UserCreateForm(request.POST, instance = user)
		if form.is_valid():
			pw = user.password
			user.set_password(user.password)
			user.is_active = False
			form.save()
			group = Group.objects.filter(name="BuLiTipp")[0]
			#user.groups.add(group)
			user = authenticate(username=user.username, password=pw)
			#djlogin(request, user)
			mail.send("BuLiTipp: User registriert", "cdanzmann@gmail.com", "Bitte administriere den neuen User " + user.username+ " !")
			messages.success(request, "Benutzer erfolgreich angelegt! Du kannst dich einloggen sobald der Administrator dich freigeschaltet hat.")
			#return HttpResponseRedirect(reverse("user"))
			return HttpResponseRedirect(reverse("home"))
	else:
		form = UserCreateForm(instance=user)
	context["form"] = form
	return render(request, 'registration/register.html', context)

class NewsPageView(TemplateView):
	template_name = 'messages/ms_index.html'
	referer = "news"

	def get_context_data(self, **kwargs):
		context = super(NewsPageView, self).get_context_data(**kwargs)
		return context
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		# may not be logged in
		try:
			user = User.objects.get(pk=request.user.id)
			user.letzte_news_gelesen = datetime.now()
			user.save()
		except:
			pass
		context["news"]=get_news_by_request(request)
		context["referer"]=self.referer #request.META["HTTP_REFERER"]
		return self.render_to_response(context)

class HomePageView(TemplateView):
	template_name = 'home/hm_index.html'
	referer = "home"
	def get_context_data(self, **kwargs):
		context = super(HomePageView, self).get_context_data(**kwargs)
		return context
	def get(self, request, *args, **kwargs):
		if "spieltag_id" in kwargs:
				spieltag_id = kwargs["spieltag_id"]
		else:
				spieltag_id = None
		if "spielzeit_id" in kwargs:
				spielzeit_id = kwargs["spielzeit_id"]
		else:
				spielzeit_id = None
		context = self.get_context_data(**kwargs)
		context["news"]=get_news_by_request(request)
		context["spielzeiten"]=get_spielzeiten_by_request(request)
		context["spielzeit"]=get_spielzeit_by_request(request, spielzeit_id, before_spieltag_id=spieltag_id)
		context["spieltag"]=get_spieltag_by_request(request, spielzeit_id, spieltag_id)
		context["kommentare"]=get_kommentare_by_request(request, spielzeit_id, context["spieltag"].id)
		context["referer"]=self.referer #request.META["HTTP_REFERER"]
		return self.render_to_response(context)
	def post(self, request, *args, **kwargs):
		return self.get(request, *args, **kwargs)

class SpieltagView(HomePageView):
	template_name = 'spieltag/st_index.html'
	referer = "spieltag"
	def get(self, request, *args, **kwargs):
		if not request.user.is_authenticated():
			context = self.get_context_data(**kwargs)
			return self.render_to_response(context)
		return super(SpieltagView, self).get(request, *args, **kwargs)

class SpieltagPrintView(SpieltagView):
	template_name = 'spieltag/print/st_index.html'

class BestenlisteView(TemplateView):
	template_name = 'bestenliste/bl_index.html'
	referer = "bestenliste"
	def get_context_data(self, **kwargs):
		context = super(BestenlisteView, self).get_context_data(**kwargs)
		return context
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		if not request.user.is_authenticated():
			return self.render_to_response(context)
		szs=[]
		for sz in get_spielzeiten_by_request(request):
			sz_ = get_spielzeit_by_request(request, sz.id)
			sz_.aktuellerSpieltag = get_spieltag_by_request(request, sz.id, sz_.aktuellerSpieltag.id)
			szs.append(sz_)
		context["spielzeiten"]=szs
		context["news"]=get_news_by_request(request)
		context["referer"]=self.referer
		return self.render_to_response(context)

def get_kommentare_by_request(request, spielzeit_id, spieltag_id):
	return Kommentar.objects.filter(spieltag__id = spieltag_id).order_by("datum").reverse()

def get_news_by_request(request):
	news = News.objects.all().order_by("datum").reverse()
	newsto = NewsTO(news)
	try:
		user = User.objects.get(pk=request.user.id)
		date = user.letzte_news_gelesen
	except:
		date = None
	if date is None:
		date = datetime(year=2000, month=1, day=1)
	newsto.anzahl_ungelesen = news.filter(datum__gt = date).count()
	return newsto

def get_spielzeiten_by_request(request):
	szTOs=[]
	for sz in Spielzeit.objects.all().order_by("id").reverse():
		szTOs.append(SpielzeitBezeichnerTO(sz))
	return szTOs

def get_spielzeit_by_request(request, spielzeit_id, before_spieltag_id=None):
	if spielzeit_id == None:
		sz = Spielzeit.objects.all().order_by("id").reverse()[0]
	else:
		sz = Spielzeit.objects.get(pk=spielzeit_id)
	if not before_spieltag_id is None:
		try:
			before_spieltag_id = Spieltag.objects.get(pk=before_spieltag_id).next().id
		except:
			pass
	st = sz.next_spieltag()
	if st.is_tippable():
			st_prev = st.previous()
			if st_prev != None:
				st = st_prev
	aktueller_spieltagTO = SpieltagTO(st)
	tabelle = TabelleDAO.spielzeit(sz.id)
	bestenliste = BestenlisteDAO.spielzeit(sz.id, before_spieltag_id=before_spieltag_id)
	spieltage = []
	for st in sz.spieltag_set.all().order_by("nummer"):
		spieltage.append(SpieltagTO(st))
	return SpielzeitTO(sz, aktueller_spieltagTO, tabelle, bestenliste, spieltage)

def get_spieltag_by_request(request, spielzeit_id, spieltag_id):
	if spielzeit_id == None:
		if spieltag_id != None:
			# wenn spieltag, aber nicht spielzeit übergeben ist, dann bestimme spielzeit aus spieltag
			sz = Spieltag.objects.get(pk=spieltag_id).spielzeit
		else:
			sz = Spielzeit.objects.all().order_by("id").reverse()[0]
	else:
		sz = Spielzeit.objects.get(pk=spielzeit_id)
	if spieltag_id == None:
		st = sz.next_spieltag()
		if st.is_tippable():
			st_prev = st.previous()
			if st_prev != None:
				st = st_prev
	else:
		st = sz.spieltag_set.get(pk=spieltag_id)
	return get_spieltagTO_by_request(request, st)

def get_spieltagTO_by_request(request, st):
	count_spiele = 0
	count_eigene_tipps = 0
	count_andere_tipps = {}
	spieleTOs = []
	for spiel in st.spiel_set.all().order_by("datum"):
		count_spiele += 1
		tipps = spiel.tipp_set.all()
		try:
			eigenerTipp = tipps.filter(user_id = request.user.id)[0]
			count_eigene_tipps += 1
		except:
			eigenerTipp = None
		andereTipps = tipps.exclude(user_id = request.user.id)
		for tipp in andereTipps:
			try:
				count_andere_tipps[tipp.user] = count_andere_tipps[tipp.user] + 1
			except:
				count_andere_tipps[tipp.user] = 1
		spieleTOs.append(SpielTO(spiel, eigenerTipp, andereTipps))
	naechster = st.next()
	vorheriger = st.previous()
	bestenliste = BestenlisteDAO.spieltag(st.id)
	voll_getippt = {}
	voll_getippt[request.user.id] = count_spiele == count_eigene_tipps
	for user, tipps in count_andere_tipps.iteritems():
		voll_getippt[user.id] = count_spiele == tipps
	return SpieltagTO(st, spieleTOs, voll_getippt, naechster, vorheriger, bestenliste)

class ImpressumView(TemplateView):
	template_name = 'home/hm_impress.html'

	def get_context_data(self, **kwargs):
		context = super(ImpressumView, self).get_context_data(**kwargs)
		return context

def delete_kommentar(request, spieltag_id=None, spielzeit_id=None):
	kommentar_id=request.POST["kommentar_id"]
	spieltag_id=request.POST["spieltag_id"]
	Kommentar.objects.get(pk=kommentar_id).delete()
	return HttpResponseRedirect(reverse("spieltag", args=(spielzeit_id, spieltag_id)))
	
def post_kommentar(request, spieltag_id=None, spielzeit_id=None):
	text=request.POST["text"]
	user=request.user
	spieltag_id=request.POST["spieltag_id"]
	reply_to=request.POST["reply_to"]
	kommentar=Kommentar()
	kommentar.text=text
	kommentar.user=user
	if spieltag_id != "":
		kommentar.spieltag_id = spieltag_id
	else:
		kommentar.reply_to_id = reply_to
		#for redirect FIXME:hack
		komm = Kommentar.objects.get(pk=reply_to)
		while komm.spieltag_id == None:
			komm = Kommentar.objects.get(pk=komm.reply_to)
		spieltag_id = komm.spieltag_id
	kommentar.datum=datetime.now()
	kommentar.save()
	return HttpResponseRedirect(reverse("spieltag", args=(spielzeit_id, spieltag_id)))

@login_required
def tippen(request, spielzeit_id, spieltag_id):
	''' request.POST.items() enthaelt die Tipps in der Form: [("tipp_"spielID : tipp), ]
	'''
	import string
	tipped = 0
	tipps = filter(lambda key: key.startswith("tipp_"), request.POST.keys())
	#fuer jeden tipp im POST
	for tipp_ in tipps:
		tipp, spiel_id = string.split(tipp_, "_")
		spiel = Spiel.objects.get(pk=spiel_id)
		if not spiel.is_tippable():
			continue
		#suche ob es fuer diesen (user, spiel) schon ein tipp gibt
		# FIXME: better validation?
		if ":" in request.POST[tipp_]:
			try:
				tipp = Tipp.objects.get(spiel_id=spiel_id, user_id=request.user.id)
			except:
				#wenn nein: lege einen an
				tipp = Tipp()
				tipp.spiel_id = spiel_id
				tipp.user = request.user
			tipp.ergebniss = request.POST[tipp_]
			#tipp speichern
			tipp.save()
			tipped += 1
	spiele_count = Spiel.objects.filter(spieltag__id = spieltag_id).count()
	if tipped == spiele_count:
		messages.success(request, 'Erfolgreich getippt!')
	else:
		messages.warning(request, 'Achtung! Es wurden nicht alle Spiele getippt!')
	if "referer" in request.POST.keys():
		if request.POST["referer"] == "spieltag":
			return HttpResponseRedirect(reverse("spieltag", args=(spielzeit_id, spieltag_id)))
		elif request.POST["referer"] == "home":
			return HttpResponseRedirect(reverse("spieltag", args=(spielzeit_id, spieltag_id)))
	return HomePageView.as_view()(request, spieltag_id=spieltag_id, spielzeit_id=spielzeit_id)

### old:

def home(request):
	return redirect("BuLiTippApp.views.index")

@login_required
def user_site(request, spielzeit_id=None):
	user = request.user
	
# 	points_spielzeit = {}
# 	for sz in Spielzeit.objects.all():
# 		tipps = Tipp.objects.filter(user_id=user.id).filter(spiel__spieltag__spielzeit_id=sz.id)
# 		points = sum(map(lambda tipp: 0 if tipp.punkte() is None else tipp.punkte(), tipps))
# 		points_spielzeit.append((sz, points))
	spielzeiten = Spielzeit.objects.order_by('id').reverse()
	if spielzeit_id is None:
		aktuelle_spielzeit = spielzeiten[0]
	else:
		aktuelle_spielzeit = Spielzeit.objects.get(pk=spielzeit_id)
	spieltag = aktuelle_spielzeit.next_spieltag()

	if(spieltag is None or (spieltag.previous() is not None and spieltag.previous().is_tippable())):
		#noch kein abgeschlossener Spieltag -> noch keine Statistik!
		return render_to_response("stats/user.html",\
					{"spieltag":spieltag,\
					"spielzeit":aktuelle_spielzeit,\
					"spielzeiten":spielzeiten} ,\
					context_instance=RequestContext(request))
		
	if(spieltag.is_tippable()):
		spieltag=spieltag.previous()
		
	spieltipp_previous = spieltag.spieltipp(request.user.id)


	#alle tipps eines users an diesem spieltag	
	tipps = Tipp.objects.filter(user_id=user.id, spiel_id__spieltag_id=spieltag.id)
	punkte = Punkte.objects.filter(user=user, spieltag=spieltag)
	points_spieltag = sum(punkte)
	
	punkte_anteile = {}
	for tipp in tipps:
		if tipp.punkte() in punkte_anteile.keys():
			anteile = punkte_anteile[tipp.punkte()]
		else:
			anteile = 0 
		punkte_anteile[tipp.punkte()]=anteile+1
	tipp_anzahl=len(tipps)
	for key in punkte_anteile.keys():
		punkte_anteile[key]=(punkte_anteile[key]*100)/tipp_anzahl
	punkte_anteile=reversed(sorted(punkte_anteile.iteritems()))
	
	#alle tipps des users dieser spielzeit
	tipps = Tipp.objects.filter(user_id=user.id, spiel_id__spieltag__spielzeit_id=aktuelle_spielzeit.id)
	punkte = Punkte.objects.filter(user=user, spieltag__spielzeit_id=aktuelle_spielzeit.id)
	points_sum = sum(punkte)
	#nur die spieltage, die abgelaufen sind
	set_ = Set([tipp.spiel.spieltag.id if tipp.spiel.spieltag.is_tippable() == False else None for tipp in tipps])
	set_.add(None)
	spieltage_tipped = len(set_)-1
	if (spieltage_tipped ==0):
		spieltage_tipped = 1
	spieltag_punkte_diff_player = points_spieltag - (points_sum / spieltage_tipped)
	
	#tipps
	tipps = Tipp.objects.filter(spiel_id__spieltag_id=spieltag.id)
	punkte = Punkte.objects.filter(spieltag=spieltag)
	points_spieltag_sum = sum(punkte)
	
	spiele_punkte = {}
	for tipp in tipps:
		if tipp.spiel in spiele_punkte.keys():
			pkt = spiele_punkte[tipp.spiel]
		else:
			pkt = 0 
		tipp_punkte = tipp.punkte()
		if(tipp_punkte is None):
			tipp_punkte = 0
		spiele_punkte[tipp.spiel]=pkt+tipp_punkte
	spiele_punkte = sorted(spiele_punkte.iteritems(), key=operator.itemgetter(1))
	try:
		best_tipp = spiele_punkte[-1]
	except:
		best_tipp = None
	try:
		worst_tipp = spiele_punkte[0]
	except:
		worst_tipp = None
	
	user_tipped = len(Set([tipp.user.id for tipp in tipps]))
	if (user_tipped == 0):
		user_tipped = 1;
	points_diff = points_spieltag - (points_spieltag_sum / user_tipped)
	
	
	return render_to_response("stats/user.html",\
					{"spieltag":spieltag,\
					"spielzeit":aktuelle_spielzeit,\
					"spieltag_punkte":points_spieltag,\
					"spieltag_punkte_diff":points_diff,\
					"best_tipp":best_tipp,\
					"worst_tipp":worst_tipp,\
					"punkte_anteile":punkte_anteile,\
					"spielzeiten":spielzeiten,\
					"tabelle":Tabelle().getMannschaftPlatz(aktuelle_spielzeit),\
					"spieltag_punkte_diff_player":spieltag_punkte_diff_player,\
					"spieltipp":spieltipp_previous} ,\
					context_instance=RequestContext(request))


def best(request, full=True):
	''' Ausgabe beschränken auf max. ersten 3 Plätze + eigener Platz + den davor und den dahinter 
	'''
	userpunkte=[]
	#fuer jeden user
	for user in User.objects.all():
		#summiere die punkte der Tipps
		punkte = sum(Punkte.objects.filter(user__id=user.id))
		userpunkte.append((user, punkte))
	userpunkte.sort(key=lambda punkt:punkt[1], reverse=True)
	userpunkteplatz=[(userpunkt[0], userpunkt[1], platz+1) for platz, userpunkt in enumerate(userpunkte)]
	user=request.user
	for i, userp in enumerate(userpunkte):
		if user.id == userp[0].id:
			platz=i
			break
	first=True
	j=0
	if not full:
		for i, userp in enumerate(userpunkteplatz[:]):
			if i < 3 or platz -2 < i < platz + 2:
				j+=1
				first=True
				continue
			if first:
				first=False
				userpunkteplatz[i]=("...", "...", "...")
				j+=1
			else:
				del userpunkteplatz[j]
	return render_to_response("bestenliste/detail.html",{"userpunkteplatz":userpunkteplatz}, context_instance=RequestContext(request))
	
def index(request, spielzeit_id=-1):
	# show Punkte, letzter Spieltag, naechster Spieltag
	spielzeiten=[]
	aktuelle_spielzeit=None
	spieltipp_next=None
	spieltipp_previous=None
	news=News.objects.all().order_by("datum").reverse()[:3]
	#logik, ob eine spezielle spielzeit ausgewählt ist, oder erst noch ausgewählt werden muss
	try:
		aktuelle_spielzeit=Spielzeit.objects.get(pk=spielzeit_id)
		spieltag = aktuelle_spielzeit.next_spieltag()
		if(spieltag is not None and spieltag.is_tippable()):
			spieltipp_next = spieltag.spieltipp(request.user.id)
		else:
			#letzten Spieltag erreicht
			spieltipp_next=None
		if(spieltag.previous() is not None):
			if(spieltag.is_tippable()):
				spieltipp_previous = spieltag.previous().spieltipp(request.user.id)
			else:
				#kein naechster spieltag
				spieltipp_previous = spieltag.spieltipp(request.user.id)
		else:
			spieltipp_previous=None
		#fix fuer spielzeiten, die nur einen Spieltag haben
		if(spieltipp_next is None and spieltipp_previous is None):
			spieltipp_previous = spieltag.spieltipp(request.user.id)
	except:
		spielzeiten=Spielzeit.objects.all()
	args = {"spielzeiten":spielzeiten, \
		"aktuelle_spielzeit":aktuelle_spielzeit, \
		"spieltipp_next":spieltipp_next, \
		"spieltipp_previous":spieltipp_previous, \
		"news":news}
	if not aktuelle_spielzeit is None and not aktuelle_spielzeit.isPokal:
		args["tabelle"] = Tabelle().getMannschaftPlatz(aktuelle_spielzeit)
	return render_to_response("index.html",\
		args ,\
		context_instance=RequestContext(request))
#	return HttpResponse("This is the Index view.")

def logout(request):
	djlogout(request)
	return redirect(reverse("BuLiTippApp.views.index"), context_instance=RequestContext(request))


@login_required
def detail(request, spieltag_id, spielzeit_id=-1, info=""):
	spieltag = get_object_or_404(Spieltag, pk=spieltag_id)
	spielzeit = Spielzeit.objects.get(pk=spieltag.spielzeit_id)
	spieltag_next = int(spieltag_id) + 1
	spieltag_previous = int(spieltag_id) - 1
	#tipps = Tipp.objects.filter(spiel_id__spieltag_id=spieltag_id).filter(user_id=request.user.id)
	#tipps = {t.spiel_id: t for t in tipps}
	spieltipp = spieltag.spieltipp(request.user.id)
	args={"spieltag" : spieltag, "spielzeit" : spielzeit, \
		"spieltag_next" : str(spieltag_next), "spieltag_previous" : str(spieltag_previous), \
		"spieltipp": spieltipp}
	if not spielzeit.isPokal:
		args["tabelle"] = Tabelle().getMannschaftPlatz(spielzeit)
	if info is not None:
		args["message"]=info
	return render_to_response("spieltag/detail.html", args, context_instance=RequestContext(request))


@login_required
def saisontipp(request, spielzeit_id=None, message=None):
	spielzeiten = Spielzeit.objects.all()
	if spielzeit_id is None:
		spielzeit_id = spielzeiten[0].id
		return HttpResponseRedirect(reverse("BuLiTippApp.views.saisontipp", args=(spielzeit_id,)))
	spielzeit = Spielzeit.objects.get(pk=spielzeit_id)
	is_pokal = spielzeit.isPokal
	mannschaften=Verein.objects.all()
	try:
		meistertipp=Meistertipp.objects.get(user_id=request.user.id, spielzeit_id=spielzeit_id)
	except:
		meistertipp=None
	try:
		herbstmeistertipp=Herbstmeistertipp.objects.get(user_id=request.user.id, spielzeit_id=spielzeit_id)
	except:
		herbstmeistertipp=None
	try:
		absteiger1=Absteiger.objects.filter(user_id=request.user.id, spielzeit_id=spielzeit_id)[0]
	except:
		absteiger1=None
	try:
		absteiger2=Absteiger.objects.filter(user_id=request.user.id, spielzeit_id=spielzeit_id)[1]
	except:
		absteiger2=None
	try:
		absteiger3=Absteiger.objects.filter(user_id=request.user.id, spielzeit_id=spielzeit_id)[2]
	except:
		absteiger3=None
	if "absteigertipp1_id" in request.POST.keys():
		absteigertipp1_id = request.POST["absteigertipp1_id"]
		if absteiger1 is not None:
			absteiger1.delete()
		absteiger1=None
		if absteiger1 is None:
			absteiger1=Absteiger()
		absteiger1.user=request.user
		absteiger1.spielzeit_id=spielzeit_id
		absteiger1.mannschaft_id=absteigertipp1_id
		absteiger1.save()
	if "absteigertipp2_id" in request.POST.keys():
		absteigertipp2_id = request.POST["absteigertipp2_id"]
		if absteiger2 is not None:
			absteiger2.delete()
		absteiger2=None
		if absteiger2 is None:
			absteiger2=Absteiger()
		absteiger2.user=request.user
		absteiger2.spielzeit_id=spielzeit_id
		absteiger2.mannschaft_id=absteigertipp2_id
		absteiger2.save()
	if "absteigertipp3_id" in request.POST.keys():
		absteigertipp3_id = request.POST["absteigertipp3_id"]
		if absteiger3 is not None:
			absteiger3.delete()
		absteiger3=None
		if absteiger3 is None:
			absteiger3=Absteiger()
		absteiger3.user=request.user
		absteiger3.spielzeit_id=spielzeit_id
		absteiger3.mannschaft_id=absteigertipp3_id
		absteiger3.save()
	if "herbstmeistertipp_id" in request.POST.keys():
		herbstmeistertipp_id = request.POST["herbstmeistertipp_id"]
		if herbstmeistertipp is None:
			herbstmeistertipp=Herbstmeistertipp()
		herbstmeistertipp.user=request.user
		herbstmeistertipp.spielzeit_id=spielzeit_id
		herbstmeistertipp.mannschaft_id=herbstmeistertipp_id
		herbstmeistertipp.save()
	if "meistertipp_id" in request.POST.keys():
		meistertipp_id = request.POST["meistertipp_id"]
		if meistertipp is None:
			meistertipp=Meistertipp()
		meistertipp.user=request.user
		meistertipp.spielzeit_id=spielzeit_id
		meistertipp.mannschaft_id=meistertipp_id
		meistertipp.save()
		return saisontipp(request, spielzeit_id, "Erfolgreich gespeichert!")
	return render_to_response( \
		"saisontipp.html", \
		{  \
		"mannschaften":mannschaften, \
		"spielzeiten" :spielzeiten,  \
		"meistertipp" :meistertipp,  \
		"absteiger1"  :absteiger1,	\
		"absteiger2"  :absteiger2,	\
		"absteiger3"  :absteiger3,	\
		"herbstmeistertipp" :herbstmeistertipp,  \
		"spielzeit_id" :spielzeit_id,  \
		"spielzeit" :spielzeit,  \
		"is_pokal"	:is_pokal,	\
		"message"	:message,		\
		}, \
		context_instance=RequestContext(request))

@login_required
def account(request, info=""):
	# redirect on cancel to index page
	if "cancel" in request.POST.keys() :
		return redirect(reverse("BuLiTippApp.views.index"), context_instance=RequestContext(request))
	if "delete" in request.POST.keys() :
		return delete_account(request)
	args = {}
	user = request.user
	# if POST, then update submitted user values
	if "submit" in request.POST.keys() :
		user.first_name = request.POST["first_name"]
		user.last_name = request.POST["last_name"]
		user.email = request.POST["email"]
		user.save()
		info = "Speichern erfolgreich!"
	if info is not None:
		args["message"]=info
	return render_to_response("user/account.html", args, context_instance=RequestContext(request))

@login_required
def delete_account(request, info=""):
	# redirect on cancel to account page
	if "cancel" in request.POST.keys() :
		return redirect(reverse("BuLiTippApp.views.account"), context_instance=RequestContext(request))
	# on submit: delete user, redirect to index page
	if "submit" in request.POST.keys() :
		user = request.user
		user.delete()
		djlogout(request)
		return redirect(reverse("BuLiTippApp.views.index"), context_instance=RequestContext(request))
	return render_to_response("user/delete_account.html", {}, context_instance=RequestContext(request))

@login_required
@csrf_protect
@sensitive_post_parameters()
def change_pw(request):
	from django.contrib.auth.forms import PasswordChangeForm
	post_change_redirect = reverse('BuLiTippApp.views.change_pw_done')
	template_name = "user/pwchange.html"
	password_change_form=PasswordChangeForm
	
	if request.method == "POST":
		if "cancel" in request.POST.keys() :
			return redirect(reverse("BuLiTippApp.views.account"), context_instance=RequestContext(request))
		form = password_change_form(user=request.user, data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(post_change_redirect)
	else:
		form = password_change_form(user=request.user)
	context = {
		'form': form,
	}
	return TemplateResponse(request, template_name, context, current_app="BuLiTippApp")

@login_required
def change_pw_done(request):
	template_name='user/pwchangedone.html'
	context = {}

	return TemplateResponse(request, template_name, context, current_app=None)
