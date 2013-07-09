from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as djlogin, logout as djlogout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from models import Spieltag, Spielzeit, Spiel, Tipp, Kommentar
from datetime import datetime

def home(request):
	return redirect("BuLiTippApp.views.index")

def best(request):
	userpunkte=[]
	#fuer jeden user
	for user in User.objects.all():
		#ermittle alle tipps
		tipps = Tipp.objects.filter(user_id=user.id)
		#summiere die punkte der Tipps
		punkte = sum(map(lambda tipp: 0 if tipp.punkte() is None else tipp.punkte(), tipps))
		userpunkte.append((user, punkte))
	userpunkte.sort(key=lambda punkt:punkt[1], reverse=True)
	return render_to_response("bestenliste.html",{"userpunkte":userpunkte})
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

def index(request):
	return index2(request, -1)
def index2(request, spielzeit_id):
	# show Punkte, letzter Spieltag, naechster Spieltag
	spielzeiten=[]
	aktuelle_spielzeit=None
	spieltipp_next=None
	spieltipp_previous=None
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
	except:
		spielzeiten=Spielzeit.objects.all()
	
	return render_to_response("index.html",\
		{"spielzeiten":spielzeiten, \
		"aktuelle_spielzeit":aktuelle_spielzeit, \
		"spieltipp_next":spieltipp_next, \
		"spieltipp_previous":spieltipp_previous} ,\
		context_instance=RequestContext(request))
#	return HttpResponse("This is the Index view.")

def logout(request):
	djlogout(request)
	return redirect("/BuLiTipp/", context_instance=RequestContext(request))

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
		return redirect("/", context_instance=RequestContext(request))
	return render_to_response("register.html", context_instance=RequestContext(request))
	

def login(request):
	if "username" in request.POST.keys():
		u = request.POST['username']
		p = request.POST['password']
		user = authenticate(username=u, password=p)
		if user is not None:
			if user.is_active:
				djlogin(request, user)
				if "next" in request.POST.keys() and len(request.POST["next"])>0:
					return redirect(request.POST["next"])
				else:
					return redirect("/BuLiTipp/", context_instance=RequestContext(request))
					#return HttpResponseRedirect(reverse("BuLiTippApp.views.index") )
			else:
				return HttpResponse("Falscher Username/Password!")
		else:
			return HttpResponse("Falscher Username/Password!")
	return render_to_response("login.html", context_instance=RequestContext(request))

@login_required
def detail(request, spieltag_id):
	spieltag = get_object_or_404(Spieltag, pk=spieltag_id)
	spielzeit = Spielzeit.objects.get(pk=spieltag.spielzeit_id)
	spieltag_next = int(spieltag_id) + 1
	spieltag_previous = int(spieltag_id) - 1
	tipps = Tipp.objects.filter(spiel_id__spieltag_id=spieltag_id).filter(user_id=request.user.id)
	tipps = {t.spiel_id: t for t in tipps}
	spieltipp = spieltag.spieltipp(request.user.id)
	return render_to_response("spieltag/detail.html", \
		{"spieltag" : spieltag, \
		"spielzeit" : spielzeit, \
		"spieltag_next" : str(spieltag_next), \
		"spieltag_previous" : str(spieltag_previous), \
		"spieltipp": spieltipp}, \
		context_instance=RequestContext(request))

@login_required
def tippen(request, spieltag_id):
	''' request.POST.items() enthaelt die Tipps in der Form: [("tipp_"spielID : tipp), ]
	'''
	import string
	def tipp_filter(k): return k.startswith("tipp_")
	tipps = filter(tipp_filter, request.POST.keys())
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
		tipp.save()
		#tipp speichern
	s = ""
	for k, v in request.POST.items():
		s+= "%s: %s; " % (k, v)
	return HttpResponseRedirect(reverse("BuLiTippApp.views.detail", args=(spieltag_id,)))
