# -*- coding: utf-8 -*-
'''
Created on 14.01.2014

@author: ladanz
'''
from django.db import models

class BootstrapThemes(models.Model):
	class Meta:
		app_label = 'BuLiTippApp'
	bezeichner = models.CharField(max_length=50)
	location = models.CharField(max_length=50)
	def __unicode__(self):
		return "%s" % (self.bezeichner,)