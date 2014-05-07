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

import autocomplete_light
from smtplib import SMTPRecipientsRefused
autocomplete_light.autodiscover()

from django.db import IntegrityError
from models import Spieltag, Spielzeit, Tipp, Kommentar, News, Meistertipp, Verein, Herbstmeistertipp, Absteiger, Tabelle, Punkte, User, Spiel, Tippgemeinschaft, TG_Einladung
from models import NewsTO, SpielzeitTO, SpieltagTO, SpielTO, SpielzeitBezeichnerTO
from models import BestenlisteDAO, TabelleDAO, VereinDAO
from datetime import datetime
from sets import Set
from forms import UserModelForm, UserCreateForm
from forms import TG_createForm, TG_showForm, TG_Einladung_createForm

import operator, string
from django.forms.forms import Form
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
import ngmail as mail
import uuid

TG_KICK_SUBJECT = 'TippBuLi: Rauswurf aus Tippgemeinschaft "%s" !'
TG_KICK_MSG = 'Hallo %s,\n\nDu wurdest von %s aus der Tippgemeinschaft "%s" rausgeworfen!\n\nViele Gruesze,\ndie BuLiTippApp'
TG_KICK_MSG_HTML = '<html>Hallo %s,<br><br>Du wurdest von %s aus der Tippgemeinschaft "<b>%s</b>" rausgeworfen!<br><br>Viele Gr&uuml;&szlig;e,<br>die BuLiTippApp</html>'

TG_JOIN_SUBJECT = 'TippBuLi: Eintritt in die Tippgemeinschaft "%s" !'
TG_JOIN_MSG = 'Hallo %s,\n\n%s ist in deine Tippgemeinschaft "%s" eingetreten!\nSo lange deine Tippgemeinschaft "offen" ist, kann jeder beitreten der moechte.\n\nViele Gruesze,\ndie BuLiTippApp'
TG_JOIN_MSG_HTML = '<html>Hallo %s,<br><br>%s ist in deine Tippgemeinschaft "<b>%s</b>" eingetreten!<br>So lange deine Tippgemeinschaft "offen" ist, kann jeder beitreten der m&ouml;chte.<br><br>Viele Gr&uuml;&szlig;e,<br>die BuLiTippApp</html>'

TG_QUIT_SUBJECT = 'TippBuLi: Austritt aus Tippgemeinschaft "%s" !'
TG_QUIT_MSG = 'Hallo %s,\n\n%s ist aus deiner Tippgemeinschaft "%s" ausgetreten!\n\nViele Gruesze,\ndie BuLiTippApp'
TG_QUIT_MSG_HTML = '<html>Hallo %s,<br><br>%s ist aus deiner Tippgemeinschaft "<b>%s</b>" ausgetreten!<br><br>Viele Gr&uuml;&szlig;e,<br>die BuLiTippApp</html>'


### new:
def del_tg_user(request, tg_id, user_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse("home"))
	# security checks
	tg = Tippgemeinschaft.objects.get(pk=tg_id)
	user = User.objects.get(pk=user_id) 
	if not request.user.id in (tg.chef.id, user.id):
		messages.warning(request, "Nicht berechtigt!")
		return HttpResponseRedirect(reverse("show_tippgemeinschaft", args=[tg.id]))
	tg.users.remove(user)
	tg.save()
	von = tg.chef.first_name if tg.chef.first_name else tg.chef.username
	fuer = user.first_name if user.first_name else user.username
	if user.id == request.user.id:
		messages.success(request, "Erfolgreich ausgetreten!")
		args = (unicode(von), unicode(fuer), unicode(tg.bezeichner), )
		mail.send(TG_QUIT_SUBJECT % unicode(tg.bezeichner), user.email, 
				TG_QUIT_MSG % args, 
				TG_QUIT_MSG_HTML % args)
	else:
		messages.success(request, "Tipper erfolgreich rausgeschmissen!")
		args = (unicode(fuer), unicode(von), unicode(tg.bezeichner), )
		mail.send(TG_KICK_SUBJECT % unicode(tg.bezeichner), user.email, 
				TG_KICK_MSG % args, 
				TG_KICK_MSG_HTML % args)
	return HttpResponseRedirect(reverse("show_tippgemeinschaft", args=[tg.id]))

def tg_einladung_acc(request, tge_key):
	def render_usercreate_completition(request, tge_key, tge):
		context = {}
		pwchange_form = SetPasswordForm(user=tge.fuer)
		context["pwchange_form"] = pwchange_form
		context["tge_key"] = tge_key
		return render(request, 'tippgemeinschaft/einladung_create_user.html', context)
	def finish_account_creation(tge):
		form = SetPasswordForm(user=tge.fuer, data=request.POST)
		if form.is_valid():
			form.save()
			user = tge.fuer
			user.is_active = True
			group = Group.objects.filter(name="BuLiTipp")[0]
			user.groups.add(group)
			user.save()
			user = authenticate(username=user.username, password=request.POST["new_password1"])
			djlogin(request, user)
			messages.success(request, "Account erfolgreich aktiviert!")
	try:
		user_created = False
		tge = TG_Einladung.objects.get(key=tge_key)
		if request.method == "POST":
			finish_account_creation(tge)
			user_created = True
		if not tge.fuer.is_active:
			return render_usercreate_completition(request, tge_key, tge)
		tge.delete()
		tge.tg.users.add(tge.fuer)
		tge.tg.save()
		messages.success(request, "Einladung erfolgreich angenommen!")
		if user_created:
			return HttpResponseRedirect(reverse("user"))
		return HttpResponseRedirect(reverse("show_tippgemeinschaft", args=[tge.tg.id]))
	except:
		messages.warning(request, "Einladung besteht nicht mehr!")
		return HttpResponseRedirect(reverse("home"))

def tg_einladung_del(request, tge_key):
	try:
		tge = TG_Einladung.objects.get(key=tge_key)
		tge.delete()
		messages.success(request, "Einladung erfolgreich zurückgezogen!")
		return HttpResponseRedirect(reverse("show_tippgemeinschaft", args=[tge.tg.id]))
	except:
		messages.warning(request, "Einladung besteht nicht mehr!")
		return HttpResponseRedirect(reverse("home"))

TGE_SUBJECT = 'TippBuLi: Einladung zur Tippgemeinschaft "%s" !'
TGE_MSG = 'Hallo %s,\n\nDu hast eine Einladung von %s fuer die Tippgemeinschaft "%s" erhalten!\n\nDie Beschreibung der Tippgemeinschaft ist:\n\n%s\n\nWenn du hier klickst: %s dann nimmst du die Einladung an!\nWenn du die Einladung nicht annehmen moechtest, dann klicke hier: %s oder ignoriere diese Email.\n\nViele Gruesze,\ndie BuLiTippApp'
TGE_MSG_HTML = '<html>Hallo %s,<br><br>Du hast eine Einladung von %s f&uuml;r die Tippgemeinschaft "<b>%s</b>" erhalten!<br><br>Die Beschreibung der Tippgemeinschaft ist:<br><br><i>%s</i><br><br>Wenn du <a href="%s">hier</a> klickst dann <b>nimmst du die Einladung an</b>!<br>Wenn du die Einladung <b>nicht annehmen</b> m&ouml;chtest, dann klicke <a href="%s">hier</a> oder ignoriere diese Email.<br><br>Viele Gr&uuml;&szlig;e,<br>die BuLiTippApp</html>'

def tg_einladung_new_form(request, tg_id):
	def return_empty_form():
		context = {}
		form = TG_Einladung_createForm(tg=tg, user=request.user)
		context["news"] = get_news_by_request(request)
		context["form"] = form
		return render(request, 'tippgemeinschaft/einladung_create.html', context)
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse("home"))
	try:
		tg = Tippgemeinschaft.objects.get(pk = tg_id)
	except:
		return HttpResponseRedirect(reverse("home"))
	if request.method == 'POST':
		fuer = request.POST["fuer-autocomplete"]		
		# 2 cases: valid user, or email address
		# case 1, user
		if "user_select" in request.POST.keys():
			user_select_id = request.POST["user_select"] 
		# case 2, email:
		elif string.count(fuer, '@') == 1:
			new_user = User()
			new_user.username = fuer
			new_user.first_name = string.split(fuer, '@')[0]
			new_user.email = fuer
			new_user.is_active = False
			new_user.save()
			user_select_id = new_user.id
		else:
			messages.warning(request, "User nicht gefunden, oder ungültige eMail-Adresse!")
			return return_empty_form()
		
		tg_e = TG_Einladung()
		form = TG_Einladung_createForm(request.POST, instance = tg_e, tg=tg, user=request.user)
		if form.is_valid():
			tg_e.key = uuid.uuid4()
			tg_e.tg = tg
			tg_e.von = request.user
			tg_e.fuer_id = user_select_id
			try:
				form.save()
			except IntegrityError:
				messages.warning(request, "Bereits eine Einladung an diesen User verschickt!")
				return return_empty_form()
			#mail schicken
			von = tg_e.von.first_name if tg_e.von.first_name else tg_e.von.username
			fuer = tg_e.fuer.first_name if tg_e.fuer.first_name else tg_e.fuer.username
			args = (unicode(fuer), unicode(von), unicode(tg.bezeichner), unicode(tg.beschreibung), "http://"+request.get_host()+reverse("acc_tg_einladung", args=[tg_e.key]), "http://"+request.get_host()+reverse("del_tg_einladung", args=[tg_e.key]), )
			try:
				mail.send(TGE_SUBJECT % unicode(tg.bezeichner), 
						tg_e.fuer.email, 
						TGE_MSG % args, 
						TGE_MSG_HTML % args)
			except SMTPRecipientsRefused:
				tg_e.delete()
				if new_user:
					new_user.delete()
				messages.warning(request, "Ungültige eMail-Adresse!")
				return return_empty_form()
			messages.success(request, "Erfolgreich eingeladen!")
			return HttpResponseRedirect(reverse("show_tippgemeinschaft", args=[tg.id]))
	else:
		return return_empty_form()

def tg_show_form(request, tg_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse("home"))
	context = {}
	tg = Tippgemeinschaft.objects.get(pk = tg_id)
	if request.method == 'POST':
		if "delete" in request.POST.keys() and (request.user.is_staff or tg.chef_id == request.user.id):
			users = tg.users.all()
			#hack for the loading of the data before teletion of tg
			len(users)
			tg.delete()
			messages.success(request, "Tippgemeinschaft erfolgreich gelöscht!")
			von = tg.chef.first_name if tg.chef.first_name else tg.chef.username
			for user in users:
				fuer = user.first_name if user.first_name else user.username
				args = (unicode(fuer), unicode(von), unicode(tg.bezeichner), )
				mail.send(TG_KICK_SUBJECT % unicode(tg.bezeichner), user.email, 
						TG_KICK_MSG % args, 
						TG_KICK_MSG_HTML % args)
			return HttpResponseRedirect(reverse("user", args=["tgchange"]))
		elif "join" in request.POST.keys() and tg.open:
			tg.users.add(request.user)
			tg.save()
			messages.success(request, "Erfolgreich beigetreten!")
			fuer = tg.chef.first_name if tg.chef.first_name else tg.chef.username
			wer = request.user.first_name if request.user.first_name else request.user.username 
			args = (unicode(fuer), unicode(wer), unicode(tg.bezeichner), )
			mail.send(TG_JOIN_SUBJECT % unicode(tg.bezeichner), tg.chef.email, 
				TG_JOIN_MSG % args, 
				TG_JOIN_MSG_HTML % args)
			return HttpResponseRedirect(reverse("show_tippgemeinschaft", args=[tg.id]))
		else:
			form = TG_showForm(request.POST, instance = tg, user=request.user)
			if form.is_valid() and tg.chef.id == request.user.id:
				form.save()
				messages.success(request, "Erfolgreich geändert!")
	else:
		form = TG_showForm(instance = tg, user=request.user)
	context["news"] = get_news_by_request(request)
	context["form"] = form
	context["tg"] = tg
	return render(request, 'tippgemeinschaft/show.html', context)

def tg_new_form(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse("home"))
	context = {}
	if request.method == 'POST':
		tg = Tippgemeinschaft()
		form = TG_createForm(request.POST, instance = tg)
		if form.is_valid():
			tg.chef = request.user
			form.save()
			tg.users.add(request.user)
			tg.save()
			messages.success(request, "Erfolgreich angelegt! Versende als nächstes Einladungen!")
			return HttpResponseRedirect(reverse("show_tippgemeinschaft", args=[tg.id]))
	else:
		form = TG_createForm()
	context["news"] = get_news_by_request(request)
	context["form"] = form
	return render(request, 'tippgemeinschaft/create.html', context)

def userform(request, referer=None):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse("home"))
	context = {}
	context["news"] = get_news_by_request(request)
	user = User.objects.get(pk = request.user.id)
	pwchange_form = PasswordChangeForm(user=request.user)
	context["pwchange_form"] = pwchange_form
	context["tg_created"] = Tippgemeinschaft.objects.filter(chef__id=user.id).order_by("spielzeit")
	context["tg_member"] = Tippgemeinschaft.objects.filter(users=user.id).exclude(chef__id=user.id).order_by("spielzeit")
	context["tg_open"] = Tippgemeinschaft.objects.filter(open=True).exclude(chef__id=user.id).exclude(users=user.id).order_by("spielzeit")
	if request.method == 'POST':
		form = UserModelForm(request.POST, instance = user)
		if form.is_valid():
			form.save()
			messages.success(request, "Erfolgreich gespeichert!")
	else:
		form = UserModelForm(instance=user)
	context["form"] = form
	if(referer):
		context["referer"] = referer
	return render(request, 'user/user.html', context)

open_registration = True

def register(request):
	context = {}
	context["news"] = get_news_by_request(request)
	user = User()
	if request.method == 'POST':
		form = UserCreateForm(request.POST, instance = user)
		if form.is_valid():
			pw = user.password
			user.set_password(user.password)
			if not open_registration:
				user.is_active = False
			form.save()
			if open_registration:
				group = Group.objects.filter(name="BuLiTipp")[0]
				user.groups.add(group)
				user = authenticate(username=user.username, password=pw)
				djlogin(request, user)
				messages.success(request, "Benutzer erfolgreich angelegt! Tritt als nächstes einer Tippgemeinschaft bei!")
				return HttpResponseRedirect(reverse("user", args=["tgchange"]))
			else:
				mail.send("BuLiTipp: User registriert", "cdanzmann@gmail.com", "Bitte administriere den neuen User " + user.username+ " !")
				messages.success(request, "Benutzer erfolgreich angelegt! Du kannst dich einloggen sobald der Administrator dich freigeschaltet hat.")
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
		context["spielzeit"]=get_spielzeit_by_request(request, spielzeit_id, aktuell_spieltag_id=spieltag_id, user_id=request.user.id)
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
			try:
				return HttpResponseRedirect(reverse("home", kwargs={"spieltag_id":kwargs["spieltag_id"],"spielzeit_id":kwargs["spielzeit_id"]}))
			except:
				return HttpResponseRedirect(reverse("home"))
		return super(SpieltagView, self).get(request, *args, **kwargs)

class SpieltagPrintView(SpieltagView):
	template_name = 'spieltag/print/st_index.html'

class SaisontippView(TemplateView):
	template_name = 'saisontipp/st_index.html'
	referer = "saisontipp"
	def get_context_data(self, **kwargs):
		context = super(SaisontippView, self).get_context_data(**kwargs)
		return context
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		if "spielzeit_id" in kwargs and kwargs["spielzeit_id"]:
			spielzeit_id = kwargs["spielzeit_id"]
		else:
			# FIXME: implement for real
			spielzeit_id = Spielzeit.objects.all()[0].id
		if not request.user.is_authenticated():
			return HttpResponseRedirect(reverse("home"))
		context["news"]=get_news_by_request(request)
		context["spielzeiten"]=get_spielzeiten_by_request(request)
		context["spielzeit"]=get_spielzeit_by_request(request, spielzeit_id)
		context["mannschaften"] = VereinDAO.spielzeit(spielzeit_id)
		try:
			context["meistertipp"] = Meistertipp.objects.get(user_id=request.user.id, spielzeit_id=spielzeit_id)
			context["herbstmeistertipp"] = Herbstmeistertipp.objects.get(user_id=request.user.id, spielzeit_id=spielzeit_id)
			context["absteiger"] = Absteiger.objects.filter(user_id=request.user.id, spielzeit_id=spielzeit_id)
		except:
			pass
		context["referer"]=self.referer
		return self.render_to_response(context)

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
	news = News.objects.all().order_by("datum").reverse().select_related('author')
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

def get_spielzeit_by_request(request, spielzeit_id, aktuell_spieltag_id=None, user_id=None):
	if spielzeit_id == None:
		sz = Spielzeit.objects.all().order_by("id").reverse()[0]
	else:
		sz = Spielzeit.objects.get(pk=spielzeit_id)
	st = sz.next_spieltag()
	if st.is_tippable():
			st_prev = st.previous()
			if st_prev != None:
				st = st_prev
	aktueller_spieltagTO = SpieltagTO(st)
	tabelle = TabelleDAO.spielzeit(sz.id)
	bestenliste = BestenlisteDAO.spielzeit(sz.id, aktuell_spieltag_id=aktuell_spieltag_id, user_id=user_id)
	spieltage = []
	for st in sz.spieltag_set.all().order_by("nummer"):#FIXME
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
	# limit to TG members
	tgs = Tippgemeinschaft.objects.filter(users=request.user.id).filter(spielzeit__id=st.spielzeit.id)
	users_from_tg = Set()
	for tg in tgs:
		users_from_tg = users_from_tg.union(Set([u["id"] for u in tg.users.values()]))
	tipps = Tipp.objects.filter(spiel__spieltag_id=st.id).filter(user__id__in=users_from_tg)
	user_tipped = Set([tipp.user_id for tipp in tipps])
	try:
		user_tipped.remove(request.user.id)
	except:
		pass
	for spiel in st.spiel_set.all().select_related().order_by("datum"):
		count_spiele += 1
		tipps = spiel.tipp_set.all()
		try:
			eigenerTipp = tipps.filter(user_id = request.user.id).select_related('user')[0]
			count_eigene_tipps += 1
		except:
			eigenerTipp = None
		andereTipps = tipps.exclude(user_id = request.user.id).select_related('user')
		andereTipps_ = []
		for id in user_tipped:
			atipp = andereTipps.filter(user_id=id)
			if len(atipp)>0:
				andereTipps_.append(atipp[0])
			else:
				andereTipps_.append(None)
		andereTipps = andereTipps_
		for tipp in andereTipps:
			if tipp == None:
				continue
			try:
				count_andere_tipps[tipp.user_id] = count_andere_tipps[tipp.user_id] + 1
			except:
				count_andere_tipps[tipp.user_id] = 1
		spieleTOs.append(SpielTO(spiel, eigenerTipp, andereTipps))
	naechster = st.next()
	vorheriger = st.previous()
	bestenliste = BestenlisteDAO.spieltag(st.id, request.user.id)
	voll_getippt = {}
	voll_getippt[request.user.id] = count_spiele == count_eigene_tipps
	for user_id, tipps in count_andere_tipps.iteritems():
		voll_getippt[user_id] = count_spiele == tipps
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

@login_required
@csrf_protect
@sensitive_post_parameters()
def change_pw(request):
	context = {}
	form = UserModelForm(instance=request.user)
	context["form"] = form
	context["referer"] = "pwchange"
	if request.method == "POST":
		form = PasswordChangeForm(user=request.user, data=request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Passwort geändert!")
		context["pwchange_form"] = form
	return render(request, 'user/user.html', context)

def home(request):
	return redirect(reverse("home"))

def logout(request):
	djlogout(request)
	return redirect(reverse("home"), context_instance=RequestContext(request))

@login_required
def delete_account(request):
	# redirect on cancel to account page
	if "cancel" in request.POST.keys() :
		return redirect(reverse("user"), context_instance=RequestContext(request))
	# on submit: delete user, redirect to index page
	if "submit" in request.POST.keys() :
		user = request.user
		user.delete()
		djlogout(request)
		return redirect(reverse("home"), context_instance=RequestContext(request))
	return render_to_response("user/delete_account.html", {}, context_instance=RequestContext(request))

### old:

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
def saisontipp(request, spielzeit_id):
	try:
		absteigertipp_id = []
		absteigertipp_id.append(request.POST["absteigertipp1_id"])
		absteigertipp_id.append(request.POST["absteigertipp2_id"])
		absteigertipp_id.append(request.POST["absteigertipp3_id"])
		absteiger=Absteiger.objects.filter(user_id=request.user.id, spielzeit_id=spielzeit_id)
		absteiger.delete()
		for id_ in absteigertipp_id:
			absteiger=Absteiger()
			absteiger.user=request.user
			absteiger.spielzeit_id=spielzeit_id
			absteiger.mannschaft=Verein.objects.get(pk=id_)
			absteiger.save()
	except:
		pass
	try:
		meistertipp=Meistertipp.objects.get(user_id=request.user.id, spielzeit_id=spielzeit_id)
	except:
		meistertipp=None
	try:
		herbstmeistertipp=Herbstmeistertipp.objects.get(user_id=request.user.id, spielzeit_id=spielzeit_id)
	except:
		herbstmeistertipp=None
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
		messages.success(request, "Erfolgreich gespeichert!")
	return HttpResponseRedirect(reverse("saisontipp", args=(spielzeit_id)))

