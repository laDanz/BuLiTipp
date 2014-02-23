# -*- coding: utf-8	-*-
from __future__ import unicode_literals

from django import forms
from models import User, Tippgemeinschaft

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
		fields = ['bezeichner', 'beschreibung', 'spielzeit', ]

class TG_showForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		user = kwargs['user']
		del kwargs['user']
		super(TG_showForm, self).__init__(*args, **kwargs)
		instance = getattr(self, 'instance', None)
		if instance.chef.id == user.id:
			pass
		else:
			for f in self.fields:
                                self.fields[f].widget.attrs['readonly'] = True
                                self.fields[f].widget.attrs['disabled'] = True
	class Meta:
		model = Tippgemeinschaft
		fields = ['bezeichner', 'beschreibung',]
