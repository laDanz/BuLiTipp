# -*- coding: utf-8	-*-
from __future__ import unicode_literals

from django import forms
from models import User

class UserModelForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'email', 'theme', 'id',]		
		labels = {'first_name': 'Anzeigename',}
		help_texts = {'first_name': 'Wird den ',}

class UserCreateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'email', 'password',]		
		widgets = {
			'password': forms.PasswordInput(),
		}