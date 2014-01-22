'''
Created on 19.12.2013

@author: ladanz
'''
from django.contrib.auth.models import User
from transferObjects import BestenlistenPlatzTO, BestenlisteTO, TabellenPlatzTO, TabelleTO
from models_statistics import Tabelle

class BestenlisteDAO():
    @staticmethod
    def all(user_id=-1, full=True):
        return BestenlisteDAO.query(user_id=user_id, full=full)
    @staticmethod
    def spieltag(spieltag_id, user_id=-1, full=True):
        return BestenlisteDAO.query(spieltag_id=spieltag_id, user_id=user_id, full=full)
    @staticmethod
    def spielzeit(spielzeit_id, user_id=-1, full=True):
        return BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full)
    @staticmethod
    def query(user_id=-1, full=True, spieltag_id=None, spielzeit_id=None):
        from models_statistics import Punkte
        blp=[]
        #fuer jeden user
        # FIXME based on TippGemeinschaften
        for user in User.objects.filter(is_active = True).filter(groups = 1):
            punkte = Punkte.objects.filter(user=user)
            if spieltag_id is not None:
                punkte = punkte.filter(spieltag__id=spieltag_id)
            if spielzeit_id is not None:
                punkte = punkte.filter(spieltag__spielzeit_id=spielzeit_id)
            #summiere die punkte der Tipps
            punkte = sum(punkte)
            blp.append(BestenlistenPlatzTO(None, user, punkte))
        blp.sort(key=lambda blp:blp.punkte, reverse=True)
        platz = 1
        for bl in blp:
            bl.position = platz
            platz += 1
        # TODO: muss noch gefuellt werden?
        return BestenlisteTO(blp, None, None)

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