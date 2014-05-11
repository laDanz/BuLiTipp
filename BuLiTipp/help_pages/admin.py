from django.contrib import admin
from help_pages.models import *


class HelpCategoryAdmin(admin.ModelAdmin):
    """
    Admin niceties for help categories
    """

    fieldsets = (
        ( 'Category setup', {
            'fields': ('title', 'parent', 'published', 'slug', 'order')
        }),
    )

    prepopulated_fields = {"slug": ("title",)}

    raw_id_fields = ('parent',)

    list_filter = ('parent', 'published')
    list_display = ('title', 'parent', 'order', 'published')

admin.site.register(HelpCategory, HelpCategoryAdmin)


class HelpItemAdmin(admin.ModelAdmin):
    """
    Admin niceties for individual help items
    """

    fieldsets = (
        ('Item setup', {
            'fields': ('heading', 'category', 'body', 'tags', 'published', 'slug', 'order')
        }),
    )

    prepopulated_fields = {"slug": ("heading",)}

    raw_id_fields = ('category',)

    list_filter = ('category',)
    list_display = ('heading', 'category', 'order', )

    ordering = ("category",)

admin.site.register(HelpItem, HelpItemAdmin)
