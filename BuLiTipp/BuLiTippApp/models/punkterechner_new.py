#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
class Punkterechner():
	'''Der Standard-Punkterecher: 3 Punkte fuer korrektes Ergebnis, 2 fuer Differenz, 1 fuer tendenz.
	'''
	def differenz(self, erg1, erg2):
		assert ":" in erg1
		assert ":" in erg2
		assert len(erg1.split(":"))==2
		assert len(erg2.split(":"))==2
		heim=int(erg1.split(":")[0])
		ausw=int(erg1.split(":")[1])
		erg1diff=heim-ausw
		heim=int(erg2.split(":")[0])
		ausw=int(erg2.split(":")[1])
		erg2diff=heim-ausw
		return erg1diff==erg2diff


	def tendenz(self, erg1, erg2):
		if self.toto(erg1)==self.toto(erg2):
			return True
		else:
			return False
	def toto(self, erg):
		assert ":" in erg
		assert len(erg.split(":"))==2
		heim=int(erg.split(":")[0])
		ausw=int(erg.split(":")[1])
		if heim==ausw:
			return 0
		elif heim>ausw:
			return 1
		else:
			return 2
	def diff(self, erg):
		assert ":" in erg
		assert len(erg.split(":"))==2
		heim=int(erg.split(":")[0])
		ausw=int(erg.split(":")[1])
		return ausw-heim
	def punkte(self, tipp):
		try:
			spiel = tipp.spiel
			if spiel.ergebniss == tipp.ergebniss:
				return 9
			elif self.differenz(spiel.ergebniss, tipp.ergebniss):
				result = int(7-math.fabs( int(spiel.ergebniss.split(":")[0]) - int(tipp.ergebniss.split(":")[0]) ))
				if result<0:
					result=0
				return result
			elif self.tendenz(spiel.ergebniss, tipp.ergebniss):
				result = int(4-math.fabs(math.fabs(int(spiel.ergebniss.split(":")[0]) - int(tipp.ergebniss.split(":")[0]))+math.fabs(int(spiel.ergebniss.split(":")[1]) - int(tipp.ergebniss.split(":")[1]))))
				if result<0:
					result=0
				return result
			elif int(math.fabs(math.fabs(int(spiel.ergebniss.split(":")[0]) - int(tipp.ergebniss.split(":")[0]))+math.fabs(int(spiel.ergebniss.split(":")[1]) - int(tipp.ergebniss.split(":")[1])))) == 1:
				#mercy rule: genau ein Tor daneben
				return 3
			else:
				return 0
		except:
			return 0
