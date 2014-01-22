#!/usr/bin/env python
# -*- coding: latin-1 -*-
import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BuLiTipp.settings")
import BuLiTipp.settings


from BuLiTippApp.models import Spielzeit, Tipp
from django.contrib.auth.models import User
from django.utils import timezone
import BuLiTippApp.mail as mail

ERINNERUNG_SUBJECT = "Jetzt den nächsten Spieltag tippen!"
ERINNERUNG_MSG = 'Hallo %s,\n\nEs wird höchste Zeit, dass du den nächsten Spieltag tippst!\nGehe gleich auf http://TippBuLi.de/BuLiTipp/BuLiTipp/spieltag/%s/%s/ um deinen Tipp abzugeben!\n\nViele Grüße,\ndie BuLiTippApp\n\n*psst* unter uns: Du kannst auch gleich mehrere Spieltage "voraus" tippen ;)'
ERINNERUNG_MSG_HTML = '<html>Hallo %s,<br><br>Es wird h&ouml;chste Zeit, dass du den n&auml;chsten Spieltag tippst!<br>Gehe gleich auf <a href="http://TippBuLi.de/BuLiTipp/BuLiTipp/spieltag/%s/%s/">http://TippBuLi.de/</a> um deinen Tipp abzugeben!<br><br>Viele Gr&uuml;&szlig;e,<br>die BuLiTippApp<br><br><b>*psst*: Nur unter uns:</b> Du kannst auch gleich mehrere Spieltage "voraus" tippen ;)'

def run(test=False):
	global ERINNERUNG_SUBJECT
	global ERINNERUNG_MSG
	all_spielzeiten=Spielzeit.objects.all()
	for sp in all_spielzeiten:
		if test:
			print "processing " + sp.bezeichner + " ..."
		latest_spielzeit=sp
		next_spieltag=latest_spielzeit.next_spieltag()
		if not next_spieltag.is_tippable():
			if test:
				print "next_spieltag not tippable, nothing to do here"
			continue
		#print "Naechster Spieltag: " + str(next_spieltag)
		spiele_anz = len(next_spieltag.spiel_set.all())
		# only send if no more than 10 days away
		send = (next_spieltag.datum - timezone.now()).days<10
		if not send and test:
			print "not sending any emails fpr this saison, since it's to far away"
		for user in User.objects.all():
			email = user.email
			tipps_anz = len(Tipp.objects.filter(spiel_id__spieltag_id=next_spieltag.id).filter(user_id=user.id).exclude(ergebniss=""))
		#	print "%s: %s/%s" % (user.username, tipps_anz, spiele_anz)
			if tipps_anz < spiele_anz:
				if email is not None and email != "":
					#this user hasn't tippt all games, let's send him a reminder mail
					if test:
						print "User %s has not tipped(%s/%s), lets send him an riminder to %s" % (user.username, tipps_anz, spiele_anz, email)
					else:
						ERINNERUNG_SUBJECT_ = ERINNERUNG_SUBJECT+"(%s)" % str(latest_spielzeit.bezeichner)
						ERINNERUNG_MSG_ = ERINNERUNG_MSG % (str(user.username), next_spieltag.sp.id, next_spieltag.id)
						ERINNERUNG_MSG_HTML_ = ERINNERUNG_MSG_HTML % (str(user.username), next_spieltag.sp.id, next_spieltag.id)
						if send:
							mail.send(ERINNERUNG_SUBJECT_, user.email, ERINNERUNG_MSG_, ERINNERUNG_MSG_HTML_)
def install():
	#um 7:15 an jedem DIe+Do gucken
	INSTALL_STRING = "15  7    * * 2,4   ladanz  cd "+ os.getcwd()  +" && ./send_reminders.py\n"
	# is 0 if installed, otherwise not installed
	CHECK_INSTALL  = "send_reminders"
	crontab_file = open("/etc/crontab", "r")
	crontab_data = crontab_file.read()
	crontab_file.close()
	if CHECK_INSTALL in crontab_data:
		print "bereits installiert"
	else:
		print "jetzt installieren!"
		try:
			f=open(os.getcwd()+"/send_reminders.py","r")
			f.close()
		except:
			raise(Exception("Please run install from the directory where send_reminders.py is installed!"))
		crontab_file = open("/etc/crontab", "a")
		crontab_file.write(INSTALL_STRING)
		crontab_file.close()
		print "erfolgreich installiert"

def test():
	print "looking for emails to send"
	run(test=True)
	
	print "send testmail"
	global ERINNERUNG_MSG
	all_spielzeiten=Spielzeit.objects.all()
        latest_spielzeit=all_spielzeiten[len(all_spielzeiten)-1]
        next_spieltag=latest_spielzeit.next_spieltag()
	ERINNERUNG_MSG_ = ERINNERUNG_MSG % ("admin", latest_spielzeit.id, next_spieltag.id)
	ERINNERUNG_MSG_HTML_ = ERINNERUNG_MSG_HTML % ("admin", latest_spielzeit.id, next_spieltag.id)
	mail.send("This is just a Test!" +"(%s)" % latest_spielzeit.bezeichner,"cdanzmann@gmail.com","If you can read this, the mailservice is working\n" + ERINNERUNG_MSG_, ERINNERUNG_MSG_HTML_)

if __name__ == "__main__":
	if "install" in sys.argv:
		install()
	elif "test" in sys.argv:
		test()
	else:
		run()
