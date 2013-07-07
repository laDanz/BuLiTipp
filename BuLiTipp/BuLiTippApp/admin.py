from BuLiTippApp.models import Verein, Spielzeit, Spieltag, Spiel
from django.contrib import admin

admin.site.register(Verein)

class SpielInline(admin.TabularInline):
	model = Spiel
	extra = 8

class SpieltagAdmin(admin.ModelAdmin):
	list_filter = ["spielzeit"]
	inlines = [SpielInline]
	fieldsets = [
        (None,               {'fields': ['spielzeit']}),
        ('Datum', {'fields': ['datum'], 'classes': ['collapse']}),
		('Nummer', {'fields': ['nummer'], 'classes': ['collapse']}),
    ]

admin.site.register(Spieltag, SpieltagAdmin)

class SpieltagInline(admin.TabularInline):
	fields = ["nummer", "datum"]
	model = Spieltag
	extra = 0

class SpielzeitAdmin(admin.ModelAdmin):
	inlines = [SpieltagInline]
	pass

admin.site.register(Spielzeit, SpielzeitAdmin)
