#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
register = template.Library()

@register.filter
def get(d, key):
	try:
		return d.get(key, '')
	except:
		return ""
