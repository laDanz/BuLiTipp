# -*- coding: utf-8	-*-
from __future__ import unicode_literals

from django import forms
from django.forms.util import ErrorList
from models import User, ReminderOffsets, Tippgemeinschaft, TG_Einladung
import autocomplete_light
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class UserModelForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'email', 'theme', 'input_type', 'receive_newsletter', 'reminder_offset', 'id',]
	def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, 
		initial=None, error_class=ErrorList, label_suffix=':', empty_permitted=False, instance=None):
		forms.ModelForm.__init__(self, data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial, error_class=error_class, label_suffix=label_suffix, empty_permitted=empty_permitted, instance=instance)
		f=self.fields['reminder_offset']
		f.help_text = "Bitte auswählen, wie viele Tage vor Beginn eines Spieltages eine Email geschickt werden soll. Wenn man z.B.: \"0\" wählen würde, würde man am Spieltag selbst morgens eine Benachrichtigung erhalten." +\
				"<br>Halten Sie die Strg-Taste (⌘ für Mac) während des Klickens gedrückt, um mehrere Einträge auszuwählen."

class UserCreateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'email', 'password',]
		widgets = {
			'password': forms.PasswordInput(),
		}
	def clean_email(self):
		cleanedData = self.cleaned_data['email']
		
		#email just once
		user_count = User.objects.filter(email=self.data["email"]).count()
		if user_count > 0:
			raise ValidationError(_('Email address already in use!'), code='emailaddressinuse')
		
		return cleanedData

class TG_createForm(forms.ModelForm):
	class Meta:
		model = Tippgemeinschaft
		fields = ['bezeichner', 'beschreibung', 'spielzeit', 'open',]

class TG_showForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		user = kwargs['user']
		del kwargs['user']
		super(TG_showForm, self).__init__(*args, **kwargs)
		instance = getattr(self, 'instance', None)
		if instance.chef.id == user.id or user.is_staff:
			pass
		else:
			for f in self.fields:
				self.fields[f].widget.attrs['readonly'] = True
				self.fields[f].widget.attrs['disabled'] = True
	class Meta:
		model = Tippgemeinschaft
		fields = ['bezeichner', 'beschreibung', 'open',]

class TG_Einladung_createForm(forms.ModelForm):
	class Meta:
		model = TG_Einladung
		fields = []
	#fuer = forms.ModelChoiceField(queryset=User.objects.filter(is_active = True), label="Einladung für", empty_label="auswählen")
	def __init__(self, *args, **kwargs):
		user = kwargs['user']
		del kwargs['user']
		tg = kwargs['tg']
		del kwargs['tg']
		super(TG_Einladung_createForm, self).__init__(*args, **kwargs)
		users=[]
		users.append(user.id)
		for u in tg.users.all():
			users.append(u.id)
		for tge in TG_Einladung.objects.filter(tg_id=tg.id):
			users.append(tge.fuer.id)
		self.fields["fuer"] = forms.ModelChoiceField(queryset=User.objects.filter(is_active = True).exclude(id__in=users),
								label="Einladung für", empty_label="auswählen",
								required = False,
								widget=autocomplete_light.ChoiceWidget('UserAutocomplete',
													attrs={'data-autocomplete-minimum-characters':3,
														#'placeholder': 'Choose 3 cities ...',
														}))
