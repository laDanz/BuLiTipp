# -*- coding: utf-8 -*-
'''
Created on 19.12.2013

@author: ladanz
'''
from django.contrib.auth.models import User
from itertools import chain
from transferObjects import BestenlistenPlatzTO, BestenlisteTO, TabellenPlatzTO, TabelleTO
from models_statistics import Tabelle
from models import Spielzeit, Spieltag, Tippgemeinschaft

class BestenlisteDAO():
    @staticmethod
    def all(user_id=None, full=True):
        return BestenlisteDAO.query(user_id=user_id, full=full)
    @staticmethod
    def spieltag(spieltag_id, user_id=None, full=True):
        return BestenlisteDAO.query(spieltag_id=spieltag_id, user_id=user_id, full=full)
    @staticmethod
    def spielzeit(spielzeit_id, user_id=None, full=True, before_spieltag_id=None):
        '''before_spieltag_id : calculate all Punkte til that spieltag. Result will not include Punkte from the given spieltag.
        '''
        sz = Spielzeit.objects.get(pk=spielzeit_id)
        if before_spieltag_id == None:
            before_spieltag_id = sz.next_spieltag().previous().id
            aktuell_spieltag_id = sz.next_spieltag().id
        else:
            aktuell_spieltag_id = before_spieltag_id
            before_spieltag_id = Spieltag.objects.get(pk=before_spieltag_id).previous().id
        aktuell = BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full, before_spieltag_id=aktuell_spieltag_id)
        vorher = BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full, before_spieltag_id=before_spieltag_id)
        for blp in aktuell[0].bestenlistenPlatz:
            for blp_old in vorher[0].bestenlistenPlatz:
                if blp.user.id == blp_old.user.id:
                    blp.delta = blp_old.position - blp.position
        return aktuell[0]
    @staticmethod
    def query(user_id=None, full=True, spieltag_id=None, spielzeit_id=None, before_spieltag_id=None):
        from models_statistics import Punkte
        result={}
        #fuer jeden user
        users = User.objects.filter(is_active = True).filter(groups = 1)
        if user_id:
            tgs = Tippgemeinschaft.objects.filter(users__id = user_id)
            if spieltag_id:
                tgs = tgs.filter(spielzeit__spieltag__id = spieltag_id)
        else:
            tgs = [1]
        for tg in tgs:
            blp=[]
            if user_id:
                users = tg.users.all()
            for user in users:
                punkte = Punkte.objects.filter(user=user)
                if spieltag_id is not None:
                    punkte = punkte.filter(spieltag__id=spieltag_id)
                if spielzeit_id is not None:
                    punkte = punkte.filter(spieltag__spielzeit_id=spielzeit_id)
                if before_spieltag_id is not None:
                    punkte = punkte.filter(spieltag__id__lt=before_spieltag_id)
                #summiere die punkte der Tipps
                punkte = sum(punkte)
                blp.append(BestenlistenPlatzTO(None, user, punkte))
            blp.sort(key=lambda blp:blp.punkte, reverse=True)
            platz = 1
            for bl in blp:
                bl.position = platz
                platz += 1
            # TODO: muss noch gefuellt werden?
            if user_id:
                result[tg] = BestenlisteTO(blp, None, None)
            else:
                return [BestenlisteTO(blp, None, None)]
        if user_id:
            tgs = Tippgemeinschaft.objects.filter(spielzeit__spieltag__id = spieltag_id)
            blp=[]
            for tg in tgs:
                users = tg.users.all()
                punkte = Punkte.objects.filter(user__in=users)
                if spieltag_id is not None:
                    punkte = punkte.filter(spieltag__id=spieltag_id)
                punkte = sum(punkte)*10/len(users)/10.
                user = User()
                user.username = tg.bezeichner
                blp.append(BestenlistenPlatzTO(None, user, punkte))
            tg = Tippgemeinschaft()
            tg.bezeichner = "Übersicht"
            blp.sort(key=lambda blp:blp.punkte, reverse=True)
            platz = 1
            for bl in blp:
                bl.position = platz
                platz += 1
            result[tg] = BestenlisteTO(blp, None, None)
        return result

class TabelleDAO():
    @staticmethod
    def spielzeit(spielzeit_id):
        tp = []
        tabellenplatz = Tabelle.objects.filter(spielzeit_id = spielzeit_id).order_by("platz")
        for t in tabellenplatz:
            # TODO: implement tore, spiele
            tp.append(TabellenPlatzTO(t.platz, t.mannschaft, t.punkte, 0, 0))
        # TODO: muss noch gefuellt werden?
        return TabelleTO(tp, None, None)