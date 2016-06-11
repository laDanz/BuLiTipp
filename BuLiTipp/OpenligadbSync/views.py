# Create your views here.
from django.views.generic.base import TemplateView
from BuLiTippApp.models import Spieltag

from sync import compareSpieltag, syncSpieltag
from OpenligadbSync.models import SpieltagXMLData
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


#########################
#####     VIEWS     #####
#########################


class ParseView(TemplateView):
	template_name = 'parse.html'
	def get_context_data(self, **kwargs):
		context = super(ParseView, self).get_context_data(**kwargs)
		return context
	def get(self, request, *args, **kwargs):
		if not request.user.is_staff:
			return HttpResponseRedirect(reverse("home"))
		spieltag_id = kwargs["spieltag_id"]
		
		context = self.get_context_data(**kwargs)
		spieltag = get_spieltag_by_request(request, spieltag_id)
		context["spieltag"] = compareSpieltag(spieltag)
		return self.render_to_response(context)
	def post(self, request, *args, **kwargs):
		return self.get(request, *args, **kwargs)

class ClearCacheView(TemplateView):
	template_name = 'parse.html'
	def get(self, request, *args, **kwargs):
		if not request.user.is_staff:
			return HttpResponseRedirect(reverse("home"))
		syncresult_id = kwargs["syncresult_id"]
		olddata=SpieltagXMLData.objects.get(pk=syncresult_id)
		spieltag_id=olddata.spieltagid
		olddata.delete()
		return HttpResponseRedirect(reverse("parse", kwargs={'spieltag_id':spieltag_id, }))

class SyncView(TemplateView):
	template_name = 'parse.html'
	def get_context_data(self, **kwargs):
		context = super(SyncView, self).get_context_data(**kwargs)
		return context
	def get(self, request, *args, **kwargs):
		if not request.user.is_staff:
			return HttpResponseRedirect(reverse("home"))
		spieltag_id = kwargs["spieltag_id"]
		if "spiel_id" in kwargs:
				spiel_id = kwargs["spiel_id"]
		else:
				spiel_id = None
		context = self.get_context_data(**kwargs)
		spieltag = get_spieltag_by_request(request, spieltag_id)
		spieltag = compareSpieltag(spieltag)
		spieltag = syncSpieltag(spieltag, spiel_id)
		context["spieltag"] = spieltag
		return self.render_to_response(context)
	def post(self, request, *args, **kwargs):
		return self.get(request, *args, **kwargs)

#########################
#####    HELPERS    #####
#########################


def get_spieltag_by_request(request, spieltag_id):
	st = Spieltag.objects.get(pk=spieltag_id)
	return st
