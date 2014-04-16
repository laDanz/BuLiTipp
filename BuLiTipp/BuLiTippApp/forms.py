# -*- coding: utf-8	-*-
from __future__ import unicode_literals

from django import forms
from models import User, Tippgemeinschaft, TG_Einladung
import autocomplete_light

class UserModelForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'email', 'theme', 'input_type', 'id',]
		# django version >= 1.5
		#labels = {'first_name': 'Anzeigename',
		#		'input_type' : 'Eingabefeld'}
		#help_texts = {'first_name': 'Wird den ',}

class UserCreateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'email', 'password',]
		widgets = {
			'password': forms.PasswordInput(),
		}

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
		fields = ['fuer', ]
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
								widget=autocomplete_light.ChoiceWidget('UserAutocomplete',
													attrs={'data-autocomplete-minimum-characters':3,
														#'placeholder': 'Choose 3 cities ...',
														}))
