'''
Created on 19.12.2013

@author: ladanz
'''
from django.contrib.auth.models import User
from transferObjects import BestenlistenPlatzTO, BestenlisteTO, TabellenPlatzTO, TabelleTO
from models_statistics import Tabelle
from models import Spielzeit, Spieltag
from django.db.models.aggregates import Sum

class BestenlisteDAO():
    @staticmethod
    def all(user_id=-1, full=True):
        return BestenlisteDAO.query(user_id=user_id, full=full)
    @staticmethod
    def spieltag(spieltag_id, user_id=-1, full=True):
        return BestenlisteDAO.query(spieltag_id=spieltag_id, user_id=user_id, full=full)
    @staticmethod
    def spielzeit(spielzeit_id, user_id=-1, full=True, aktuell_spieltag_id=None):
        '''aktuell_spieltag_id : calculate all Punkte til that spieltag. Result will include Punkte from the given spieltag.
        '''
        sz = Spielzeit.objects.get(pk=spielzeit_id)
        if aktuell_spieltag_id == None:
            try:
                if sz.has_ended():
                    before_spieltag_id = sz.next_spieltag().previous().id
                else:
                    before_spieltag_id = sz.next_spieltag().previous().previous().id
            except:
                before_spieltag_id = 0
        else:
            # actually inaccurate, but sufficient and faster
            before_spieltag_id = int(aktuell_spieltag_id)-1
        aktuell = BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full, aktuell_spieltag_id=aktuell_spieltag_id)
        vorher = BestenlisteDAO.query(spielzeit_id=spielzeit_id, user_id=user_id, full=full, aktuell_spieltag_id=before_spieltag_id)
        for blp in aktuell.bestenlistenPlatz:
            for blp_old in vorher.bestenlistenPlatz:
                if blp.user.id == blp_old.user.id:
                    blp.delta = blp_old.position - blp.position
        return aktuell
    @staticmethod
    def query(user_id=-1, full=True, spieltag_id=None, spielzeit_id=None, aktuell_spieltag_id=None):
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
            if aktuell_spieltag_id is not None:
                punkte = punkte.filter(spieltag__id__lte=aktuell_spieltag_id)
            #summiere die punkte der Tipps
            punkte = punkte.aggregate(Sum("punkte"))["punkte__sum"]
            blp.append(BestenlistenPlatzTO(None, user, punkte if punkte else 0))
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
        tabellenplatz = Tabelle.objects.filter(spielzeit_id = spielzeit_id).order_by("platz").select_related('mannschaft')
        for t in tabellenplatz:
            # TODO: implement tore, spiele
            tp.append(TabellenPlatzTO(t.platz, t.mannschaft, t.punkte, 0, 0))
        # TODO: muss noch gefuellt werden?
        return TabelleTO(tp, None, None)