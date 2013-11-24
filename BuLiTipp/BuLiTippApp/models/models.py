from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from punkterechner import Punkterechner
# Create your models here.

class News(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
	author = models.ForeignKey(User)
	datum = models.DateTimeField()
	text = models.CharField(max_length=1000)
	

class Spielzeit(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
	bezeichner = models.CharField(max_length=50)
	saisontipp_end = models.DateTimeField(null=True)
	isPokal = models.BooleanField()
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
        def is_tippable(self):
                return timezone.now()<self.saisontipp_end
	

class Spieltag(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
	spielzeit = models.ForeignKey(Spielzeit)
	datum = models.DateTimeField()
	nummer = models.IntegerField()
	bezeichner = models.CharField(max_length=50)
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
	#returns [(spiel, tipp, punkte)] for this Spieltag for a certain user
	def spieltipp(self, user_id, fremd_tipps=True):
		tipps = Tipp.objects.filter(spiel_id__spieltag_id=self.id).filter(user_id=user_id)
		tipps = {t.spiel_id: t for t in tipps}
		punkte = {t.spiel_id: t.punkte() for t in tipps.values() }
		fremdtipps={}
		if fremd_tipps:
			if not self.is_tippable():
				for spiel in self.spiel_set.all():
					ftipps= spiel.tipps()
					ftipps= ftipps.exclude(user_id=user_id)
					fremdtipps[spiel.id] = [(t.user.username, t.ergebniss, t.punkte()) for t in ftipps]
		return [(spiel, tipps[spiel.id] if spiel.id in tipps.keys() else None, punkte[spiel.id] if spiel.id in punkte.keys() else None, fremdtipps[spiel.id] if spiel.id in fremdtipps.keys() else None) for spiel in self.spiel_set.all()]
	def userpunkteplatz(self):
		return Bestenliste().spieltag(self.id)

class Bestenliste():
	class Meta:
		app_label = 'BuLiTippApp'
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
	class Meta:
		app_label = 'BuLiTippApp'
	name = models.CharField(max_length=75)
	def __unicode__(self):
		return unicode(self.name)
	def serie(self):
		from models_statistics import Serie
		return{s.spielzeit.id:s for s in Serie.objects.filter(mannschaft__id=self.id)}

class Spiel(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
	heimmannschaft = models.ForeignKey(Verein, related_name="heimmannschaft")
	auswaertsmannschaft = models.ForeignKey(Verein, related_name="auswaertsmannschaft")
	spieltag = models.ForeignKey(Spieltag)
	ergebniss = models.CharField(max_length=5)
	datum = models.DateTimeField(null=True)
	def __unicode__(self):
		return "%s vs %s" % (unicode(self.heimmannschaft), unicode(self.auswaertsmannschaft))
	def tipps(self):
		return self.tipp_set.all()
	def is_tippable(self):
		if (self.datum is not None):
	                return timezone.now()<self.datum
		if (self.spieltag is not None):
			return self.spieltag.is_tippable()
		return False


class Tipp(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
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
		s = "%s: %s (%s)" % (self.id, self.ergebniss, self.user_id)
		return unicode(s)
	def punkte(self):
		return Punkterechner().punkte(self)
	
class Kommentar(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
	datum = models.DateTimeField()
	text = models.CharField(max_length=500)
	user = models.ForeignKey(User)
	reply_to = models.ForeignKey('self', null=True)
	spieltag = models.ForeignKey(Spieltag, null=True)

############################################################################
###   saisonale Tipps   ###
############################################################################

class Meistertipp(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
		unique_together = ("user", "spielzeit")
	datum = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User)
	mannschaft = models.ForeignKey(Verein)
	spielzeit = models.ForeignKey(Spielzeit)
	def __unicode__(self):
		s = "%s: %s (%s)" % (self.user, unicode(self.mannschaft), self.spielzeit)
		return unicode(s)

class Herbstmeistertipp(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
		unique_together = ("user", "spielzeit")
	datum = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User)
	mannschaft = models.ForeignKey(Verein)
	spielzeit = models.ForeignKey(Spielzeit)
	def __unicode__(self):
		s = "%s: %s (%s)" % (self.user, unicode(self.mannschaft), self.spielzeit)
		return unicode(s)

class Absteiger(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
		unique_together = ("user", "spielzeit", "mannschaft")
	datum = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User)
	mannschaft = models.ForeignKey(Verein)
	spielzeit = models.ForeignKey(Spielzeit)
	ABSTEIGER_ANZAHL = 3
	def __unicode__(self):
		s = "%s: %s (%s)" % (self.user, unicode(self.mannschaft), self.spielzeit)
		return unicode(s)
	def save(self):
		count = 0
		try:
			count = len(Absteiger.objects.filter(user_id=self.user.id, spielzeit_id=self.spielzeit.id))
		except:
			pass
		if count>=self.ABSTEIGER_ANZAHL:
			raise Exception("no more than " + str(self.ABSTEIGER_ANZAHL)  + " Absteiger allowed")
		return super(Absteiger, self).save()
