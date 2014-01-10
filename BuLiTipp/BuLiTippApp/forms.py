# -*- coding: utf-8	-*-
from __future__ import unicode_literals

from django import forms
from models import User

#not used
class UserForm(forms.Form):
	anzeige_name = forms.CharField(max_length=10, help_text='Maximum 10 chars.')
	voller_name= forms.CharField(max_length=25, help_text='Maximum 15 chars.')
	email= forms.EmailField()
	Altes_Passwort = forms.CharField(initial=42, widget=forms.PasswordInput,help_text='Nur zum Ändern eingeben.',)
	Neues_Passwort = forms.CharField(initial=42, widget=forms.PasswordInput)
	Neues_Passwort_Wiederholen = forms.CharField(initial=42, widget=forms.PasswordInput)
	spam = forms.BooleanField(required=False, help_text='Benachrichtige mich über Änderungen.')
	def clean(self):
		cleaned_data = super(UserForm, self).clean()
		raise forms.ValidationError("This error was added to show the non field errors styling.")
		return cleaned_data
	
class UserModelForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'username', 'email', 'id',]		

class PasswordForm(forms.Form):
	AltesPasswort = forms.CharField(initial=42, widget=forms.PasswordInput)
	NeuesPasswort = forms.CharField(initial=42, widget=forms.PasswordInput)
	NeuesPasswortWiederholen = forms.CharField(initial=42, widget=forms.PasswordInput)
	cc_myself = forms.BooleanField(required=False, help_text='Benachrichtige mich..')
	def clean(self):
		cleaned_data = super(UserForm, self).clean()
		raise forms.ValidationError("This error was added to show the non field errors styling.")
		return cleaned_data

class LoginForm(forms.Form):
	Login = forms.CharField()
	Passwort = forms.CharField( widget=forms.PasswordInput)
	
	def clean(self):
		cleaned_data = super(UserForm, self).clean()
		raise forms.ValidationError("This error was added to show the non field errors styling.")
		return cleaned_data
