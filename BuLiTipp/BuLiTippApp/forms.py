# -*- coding: utf-8	-*-
from __future__ import unicode_literals

from django import forms
from django.forms.util import ErrorList
from models import User, ReminderOffsets


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