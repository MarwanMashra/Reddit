#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import geocoder
from collections.abc import Sequence
from urllib.error import HTTPError

"""GeoNames feature classes ('fcl' dans le JSON de Geonames, champ 'feature_class' de geocoder)
		A   Administrative divisions
		H   Surface waters
		L   Parks/reserves
		P   Populated places
		R   Roads
		S   Structures
		T   Mountains/Islands
		U   Undersea
		V   Woodlands
"""



class LocationList(Sequence):
	def __init__(self, code, loclist):
		self.country_code = code
		if type(self.country_code) != str:
			raise TypeError('country code must be a string')

		self.__locations = loclist
		if len(self) == 0:
			raise ValueError('LocationList object cannot be initialized empty')

		self.counter = 0

	def __len__(self):
		return len(self.__locations)

	def __getitem__(self, key):
		return self.__locations[key]

	def __repr__(self):
		return ('locations.LocationList('+self.country_code
			   +',['+','.join(str(loc) for loc in self.__locations)+'])')

	def __str__(self):
		return ', '.join(loc for loc in self.__locations if type(loc) == str)

	#Méthodes cadeaux: __contains__, __iter__, count, index

	#Pas de __setitem__
	#Pas de __delitem__

	def reinit(self, code, loclist):
		self.country_code = code
		if type(self.country_code) != str:
			raise TypeError('country code must be a string')
		self.__locations = loclist
		if len(self) == 0:
			raise ValueError('LocationList object cannot be initialized empty')
		self.counter = 0

	def tostore(self):
		return self.__locations

	def geo_search(self, *search_order):
		self.counter = 0
		for search in search_order:
			for loc in self.__locations:
				if type(loc) == str:
					self.counter += 1
					search_res = GeoQuery(loc,self.country_code,search)	#Objet résultat
					if search_res.result is not None:
						return search_res
		return search_res



class GeoQuery:
	def __init__(self, loc, code, searchtype='R', max_return=None):
		self.location = loc

		extra_args = {'fuzzy': 0.8} if searchtype == 'RF' else {}
		rows = max_return if max_return is not None else 1

		if searchtype in ['E','EH','EN','EH EN','EN EH']:
			extra_args['name_equals'] = loc
			if max_return is None:
				rows = 10

		search_res = geocoder.geonames(loc,key='scrapelord',auth='Blorp86',
						country=code,maxRows=rows,**extra_args)

		if search_res.status_code == 200:
			if search_res:
				if searchtype in ['R','RF','E']:
					self.result = search_res[0]
				else:
					if searchtype in ['EH EN', 'EH']:
						fcl = ['A','P','R','S']
					else:
						fcl = ['H','L','T','U','V']
					for res in search_res:
						if res.feature_class in fcl:
							self.result = res
							return
					if searchtype in ['EH EN','EN EH']:
						self.result = search_res[0]
			else:
				self.result = None
		else:
			raise HTTPError(search_res.url,search_res.status_code,
							'GeoNames request failed',test.headers,None)
