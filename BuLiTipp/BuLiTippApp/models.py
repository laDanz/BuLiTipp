from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from punkterechner import Punkterechner

# Create your models here.

class News(models.Model):
	author = models.ForeignKey(User)
	datum = models.DateTimeField()
	text = models.CharField(max_length=1000)
	

class Spielzeit(models.Model):
	bezeichner = models.CharField(max_length=50)
	def __init__(self, *args, **kwargs):
		super(Spielzeit, self).__init__(*args, **kwargs)
	def __unicode__(self):
		return self.bezeichner
	def save(self):
		first=False
		if self.id is None: first=True
		super(Spielzeit, self).save()
		if first is True:
			for i in range(1, 35):
				s = Spieltag()
				s.spielzeit_id = self.id
				s.nummer = i
				s.datum = timezone.now()
				s.save()
	def next_spieltag(self):
		''' Gibt den naechsten Spieltag, anhand Datum, zurueck.
		    Wenn kein naechster Spieltag, wird der letzte Spieltag zurueck gegeben.
		'''
		now = timezone.now()
		try:
			return self.spieltag_set.filter(datum__gte=now)[0]
		except:
			return self.spieltag_set.all().order_by("nummer").reverse()[0]
	def userpunkteplatz(self):
		return Bestenliste().spielzeit(self.id)
	

class Spieltag(models.Model):
	spielzeit = models.ForeignKey(Spielzeit)
	datum = models.DateTimeField()
	nummer = models.IntegerField()
	admin_order_field = "nummer"
#	def __init__(self, *args, **kwargs):
#		super(Spieltag, self).__init__(*args, **kwargs)
		#self.spielzeit=spielzeit
		#self.datum=datum
		#self.nummer=nummer
	def __unicode__(self):
		return "%d/%s" % (self.nummer, self.spielzeit)
	def is_tippable(self):
		return timezone.now()<self.datum
	def next(self):
		if self.nummer>=34:
			return None
		try:
			return Spieltag.objects.filter(spielzeit_id=self.spielzeit.id).filter(nummer=self.nummer+1)[0]
		except:
			return None
	def previous(self):
		if self.nummer<=1:
			return None
		try:
			return Spieltag.objects.filter(spielzeit_id=self.spielzeit.id).filter(nummer=self.nummer-1)[0]
		except:
			return None
	def spieltipp(self, user_id):
		tipps = Tipp.objects.filter(spiel_id__spieltag_id=self.id).filter(user_id=user_id)
		tipps = {t.spiel_id: t for t in tipps}
		punkte = {t.spiel_id: t.punkte() for t in tipps.values() }
		fremdtipps={}
		if not self.is_tippable():
			for spiel in self.spiel_set.all():
				ftipps= spiel.tipps()
				ftipps= ftipps.exclude(user_id=user_id)
				fremdtipps[spiel.id] = [(t.user.username, t.ergebniss, t.punkte()) for t in ftipps]
		return [(spiel, tipps[spiel.id] if spiel.id in tipps.keys() else None, punkte[spiel.id] if spiel.id in punkte.keys() else None, fremdtipps[spiel.id] if spiel.id in fremdtipps.keys() else None) for spiel in self.spiel_set.all()]
	def userpunkteplatz(self):
		return Bestenliste().spieltag(self.id)

class Bestenliste():
	def all(self, user_id=-1, full=True):
		return self.query(user_id=user_id, full=full)
	def spieltag(self, spieltag_id, user_id=-1, full=True):
		return self.query(spieltag_id=spieltag_id, user_id=user_id, full=full)
	def spielzeit(self, spielzeit_id, user_id=-1, full=True):
		return self.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full)
	def query(self, user_id=-1, full=True, spieltag_id=None, spielzeit_id=None):
		userpunkte=[]
		#fuer jeden user
		for user in User.objects.all():
			#ermittle alle tipps
	                tipps = Tipp.objects.filter(user_id=user.id)
			if spieltag_id is not None:
				tipps=tipps.filter(spiel_id__spieltag_id=spieltag_id)
			if spielzeit_id is not None:
				tipps=tipps.filter(spiel_id__spieltag_id__spielzeit_id=spielzeit_id)
			#summiere die punkte der Tipps
			punkte = sum(map(lambda tipp: 0 if tipp.punkte() is None else tipp.punkte(), tipps))
			userpunkte.append((user, punkte))
		userpunkte.sort(key=lambda punkt:punkt[1], reverse=True)
		userpunkteplatz=[(userpunkt[0], userpunkt[1], platz+1) for platz, userpunkt in enumerate(userpunkte)]
	        for i, userp in enumerate(userpunkte):
			if user_id == userp[0].id:
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
		return userpunkteplatz

class Verein(models.Model):
	name = models.CharField(max_length=75)
	def __unicode__(self):
		return self.name

class Spiel(models.Model):
	heimmannschaft = models.ForeignKey(Verein, related_name="heimmannschaft")
	auswaertsmannschaft = models.ForeignKey(Verein, related_name="auswaertsmannschaft")
	spieltag = models.ForeignKey(Spieltag)
	ergebniss = models.CharField(max_length=5)
	def __unicode__(self):
		return "%s vs %s" % (unicode(self.heimmannschaft), unicode(self.auswaertsmannschaft))
	def tipps(self):
		return self.tipp_set.all()

class Tipp(models.Model):
	user = models.ForeignKey(User)
	spiel = models.ForeignKey(Spiel)
	def ergebniss_h(self):
		e=str(self.ergebniss)
		if ":" in e:
			return e.split(":")[0]
		return None
	def ergebniss_a(self):
		e=str(self.ergebniss)
		if ":" in e:
			return e.split(":")[1]
		return None
	ergebniss = models.CharField(max_length=5)
	def __unicode__(self):
		return "%s: %s (%s)" % (self.spiel, self.ergebniss, self.user_id)
	def punkte(self):
		return Punkterechner().punkte(self)
	
class Kommentar(models.Model):
	datum = models.DateTimeField()
	text = models.CharField(max_length=500)
	user = models.ForeignKey(User)
	reply_to = models.ForeignKey('self', null=True)
	spieltag = models.ForeignKey(Spieltag, null=True)
