#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from models	import Verein, Spielzeit, Spieltag,	Spiel, News, BootstrapThemes
from django.contrib	import admin

admin.site.register(Verein)
admin.site.register(News)
admin.site.register(BootstrapThemes)

class SpielInline(admin.TabularInline):
	model =	Spiel
	extra =	8

class SpieltagAdmin(admin.ModelAdmin):
	list_filter	= ["spielzeit"]
	inlines	= [SpielInline]
	fieldsets =	[
		(None,				{'fields':	['spielzeit']}),
		('Datum', {'fields': ['datum'],	'classes': ['collapse']}),
		('Anzeige',	{'fields': ['nummer', 'bezeichner'], 'classes':	['collapse']}),
	]

admin.site.register(Spieltag, SpieltagAdmin)

class SpieltagInline(admin.TabularInline):
	fields = ["nummer",	"datum"]
	model =	Spieltag
	extra =	0

class SpielzeitAdmin(admin.ModelAdmin):
	inlines	= [SpieltagInline]
	pass

admin.site.register(Spielzeit, SpielzeitAdmin)
