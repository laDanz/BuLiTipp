'''
Created on 18.12.2013

@author: ladanz

Contains transfer objects for front end visualization.
'''

class NewsTO(object):

	def __init__(self, news):
		self.news = news
		self.anzahl_insg = news.count()
		# TODO: implement for real
		self.anzahl_ungelesen = self.anzahl_insg