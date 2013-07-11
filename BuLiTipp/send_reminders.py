#!/usr/bin/env python
# -*- coding: latin-1 -*-
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BuLiTipp.settings")

from BuLiTippApp.models import Spielzeit, Tipp
from django.contrib.auth.models import User
import BuLiTippApp.mail as mail

ERINNERUNG_SUBJECT = "Jetzt den nächsten Spieltag tippen!"
ERINNERUNG_MSG = "Hallo %s,\n\nEs wird höchste Zeit, dass du den nächsten Spieltag tippst!\nGehe gleich auf http://ladanz.kicks-ass.net:8000 um deinen Tipp abzugeben!\n\nViele Grüße,\ndie BuLiTippApp" 

def run(test=False):
	global ERINNERUNG_SUBJECT
	global ERINNERUNG_MSG
	all_spielzeiten=Spielzeit.objects.all()
	latest_spielzeit=all_spielzeiten[len(all_spielzeiten)-1]
	next_spieltag=latest_spielzeit.next_spieltag()
	#print "Naechster Spieltag: " + str(next_spieltag)
	spiele_anz = len(next_spieltag.spiel_set.all())
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
					ERINNERUNG_MSG_ = ERINNERUNG_MSG % str(user.username)
					mail.send(ERINNERUNG_SUBJECT, user.email, ERINNERUNG_MSG_)
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
	mail.send("This is just a Test!","cdanzmann@gmail.com","If you can read this, the mailservice is working")

if __name__ == "__main__":
	if "install" in sys.argv:
		install()
	elif "test" in sys.argv:
		test()
	else:
		run()
