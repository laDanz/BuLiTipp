#!/usr/bin/python
# -*- coding: latin-1 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as djlogin, logout as djlogout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from models import Spieltag, Spielzeit, Spiel, Tipp, Kommentar, News, Meistertipp, Verein, Herbstmeistertipp, Absteiger
from datetime import datetime
from sets import Set
import operator

def home(request):
	return redirect("BuLiTippApp.views.index")

def news(request):
	news=News.objects.all().order_by("datum").reverse()
	return render_to_response("news.html",\
		{"news":news} ,\
		context_instance=RequestContext(request))

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
	points_spieltag = sum(map(lambda tipp: 0 if tipp.punkte() is None else tipp.punkte(), tipps))
	
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
	points_sum = sum(map(lambda tipp: 0 if tipp.punkte() is None else tipp.punkte(), tipps))
	spieltage_tipped = len(Set([tipp.spiel.spieltag.id for tipp in tipps]))
	if (spieltage_tipped ==0):
		spieltage_tipped = 1
	spieltag_punkte_diff_player = points_spieltag - (points_sum / spieltage_tipped)
	
	#tipps
	tipps = Tipp.objects.filter(spiel_id__spieltag_id=spieltag.id)
	points_spieltag_sum = sum(map(lambda tipp: 0 if tipp.punkte() is None else tipp.punkte(), tipps))
	
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
                "spieltag_punkte_diff_player":spieltag_punkte_diff_player,\
				"spieltipp":spieltipp_previous} ,\
                context_instance=RequestContext(request))


def best(request, full=True):
	''' Ausgabe beschränken auf max. ersten 3 Plätze + eigener Platz + den davor und den dahinter 
	'''
	userpunkte=[]
	#fuer jeden user
	for user in User.objects.all():
		#ermittle alle tipps
		tipps = Tipp.objects.filter(user_id=user.id)
		#summiere die punkte der Tipps
		punkte = sum(map(lambda tipp: 0 if tipp.punkte() is None else tipp.punkte(), tipps))
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
# sicherheitsabfrage!?	
def delete_kommentar(request):
	kommentar_id=request.POST["kommentar_id"]
	spieltag_id=request.POST["spieltag_id"]
	Kommentar.objects.get(pk=kommentar_id).delete()
	return HttpResponseRedirect(reverse("BuLiTippApp.views.detail", args=(spieltag_id,)))
	
def post_kommentar(request):
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
	return HttpResponseRedirect(reverse("BuLiTippApp.views.detail", args=(spieltag_id,)))

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
	
	return render_to_response("index.html",\
		{"spielzeiten":spielzeiten, \
		"aktuelle_spielzeit":aktuelle_spielzeit, \
		"spieltipp_next":spieltipp_next, \
		"spieltipp_previous":spieltipp_previous, \
		"news":news} ,\
		context_instance=RequestContext(request))
#	return HttpResponse("This is the Index view.")

def logout(request):
	djlogout(request)
	return redirect(reverse("BuLiTippApp.views.index"), context_instance=RequestContext(request))

def register(request):
	''' if POST: register User, if username is free, then login user and redirect to "/"
		else: show "register.html"
	'''
	if "username" in request.POST.keys():
		u = request.POST['username']
		p = request.POST['password']
		e = request.POST["email"]
		f = request.POST["first_name"]
		#assert username unique
		try:
			user = User.objects.create_user(u, e, p)
			user = authenticate(username=u, password=p)
			djlogin(request, user)
		except IntegrityError:
			return HttpResponse("Username bereits belegt!")
		group = Group.objects.filter(name="BuLiTipp")[0]
		user.groups.add(group)
		user.save()
		return redirect(reverse("BuLiTippApp.views.index"), context_instance=RequestContext(request))
	return render_to_response("register.html", context_instance=RequestContext(request))
	
# using django.contrib.auth.views.login instead as login view
#def login(request):
#	if "username" in request.POST.keys():
#		u = request.POST['username']
#		p = request.POST['password']
#		user = authenticate(username=u, password=p)
#		if user is not None:
#			if user.is_active:
#				djlogin(request, user)
#				next=request.GET.get('next', '')
#				print "Get: "+str(request.GET)
#				print "Post: "+str(request.POST)
#				print "Next: "+next
#				if next != "":
#					return redirect(next)
#				else:
#					return redirect(reverse("BuLiTippApp.views.home"))
#					#return HttpResponseRedirect(reverse("BuLiTippApp.views.index") )
#			else:
#				return HttpResponse("Falscher Username/Password!")
#		else:
#			return HttpResponse("Falscher Username/Password!")
#	return render_to_response("login.html", context_instance=RequestContext(request))

@login_required
def detail(request, spieltag_id, spielzeit_id=-1, info=""):
	spieltag = get_object_or_404(Spieltag, pk=spieltag_id)
	spielzeit = Spielzeit.objects.get(pk=spieltag.spielzeit_id)
	spieltag_next = int(spieltag_id) + 1
	spieltag_previous = int(spieltag_id) - 1
	tipps = Tipp.objects.filter(spiel_id__spieltag_id=spieltag_id).filter(user_id=request.user.id)
	tipps = {t.spiel_id: t for t in tipps}
	spieltipp = spieltag.spieltipp(request.user.id)
	args={"spieltag" : spieltag, "spielzeit" : spielzeit, \
		"spieltag_next" : str(spieltag_next), "spieltag_previous" : str(spieltag_previous), \
		"spieltipp": spieltipp}
	if info is not None:
		args["info"]=info
	return render_to_response("spieltag/detail.html", args, context_instance=RequestContext(request))
@login_required
def tippen(request, spieltag_id):
	''' request.POST.items() enthaelt die Tipps in der Form: [("tipp_"spielID : tipp), ]
	'''
	import string
	info=None
	tipps = filter(lambda key: key.startswith("tipp_"), request.POST.keys())
	#fuer jeden tipp im POST
	for tipp_ in tipps:
		tipp, spiel_id = string.split(tipp_, "_")
		#suche ob es fuer diesen (user, spiel) schon ein tipp gibt
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
		info="Erfolgreich gespeichert!"
	#GET -> redirect to detail page
	if len(tipps)==0:
		return HttpResponseRedirect(reverse("BuLiTippApp.views.detail", args=(spieltag_id,)))
	return detail(request, spieltag_id, info=info)

@login_required
def saisontipp(request, spielzeit_id=None):
	spielzeiten = Spielzeit.objects.all()
	if spielzeit_id is None:
		spielzeit_id = spielzeiten[0].id
		return HttpResponseRedirect(reverse("BuLiTippApp.views.saisontipp", args=(spielzeit_id,)))
	spielzeit = Spielzeit.objects.get(pk=spielzeit_id)
	is_pokal = "pokal" in spielzeit.bezeichner.lower()
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
		return HttpResponseRedirect(reverse("BuLiTippApp.views.saisontipp", args=(spielzeit_id,)))
	return render_to_response( \
		"saisontipp.html", \
		{  \
		"mannschaften":mannschaften, \
		"spielzeiten" :spielzeiten,  \
		"meistertipp" :meistertipp,  \
		"absteiger1"  :absteiger1,   \
		"absteiger2"  :absteiger2,   \
		"absteiger3"  :absteiger3,   \
		"herbstmeistertipp" :herbstmeistertipp,  \
		"spielzeit_id" :spielzeit_id,  \
		"spielzeit" :spielzeit,  \
		"is_pokal"    :is_pokal,     \
		}, \
		context_instance=RequestContext(request))
