# -*- coding: utf-8	-*-
from __future__ import unicode_literals

from django import forms
from models import User
from django.utils.translation import ugettext_lazy as _ 

class UserModelForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'email', 'theme', 'id',]		
		labels = {'first_name': 'Anzeigename',}
		help_texts = {'first_name': 'Wird den ',}

class LoginForm(forms.Form):
	Login = forms.CharField()
	Passwort = forms.CharField( widget=forms.PasswordInput)
	