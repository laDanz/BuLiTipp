from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from punkterechner import Punkterechner

# Create your models here.

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
		return [(spiel, tipps[spiel.id] if spiel.id in tipps.keys() else None, punkte[spiel.id] if spiel.id in punkte.keys() else None) for spiel in self.spiel_set.all()]

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