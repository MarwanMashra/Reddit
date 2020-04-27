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



SEARCH_TYPES = ['E', 'EN', 'EH', 'EN EH', 'EH EN', 'RF', 'R']

typerr_msg = 'country code must be a string'



class LocationList(Sequence):
	def __init__(self, code, loclist):
		self.__locations = loclist

		self.country_code = code
		if type(self.country_code) != str:
			raise TypeError(typerr_msg)
		self.counter = 0

	def __len__(self):
		return len(self.__locations)

	def __getitem__(self, key):
		return self.__locations[key]

	def __repr__(self):
		return ('locations.LocationList('+self.country_code
			   +',['+','.join(str(loc) for loc in self.__locations)+'])')

	def __str__(self):
		return '['+', '.join(loc for loc in self.__locations if type(loc) == str)+']'

	#Méthodes héritées: __contains__, __iter__, count, index

	#Pas de __setitem__
	#Pas de __delitem__

	def reinit(self, code, loclist):
		self.__locations = loclist

		self.country_code = code
		if type(self.country_code) != str:
			raise TypeError(typerr_msg)
		self.counter = 0

	def tostore(self):
		return self.__locations

	def geo_search(self, *search_order):
		self.counter = 0
		if not any(False if type(loc) == int else True for loc in self.__locations):
			dummy = GeoQuery.__new__(GeoQuery)
			setattr(dummy,'location',None)
			setattr(dummy,'result',None)
			return dummy

		for search in search_order:
			if search not in SEARCH_TYPES:
				raise GeoError(search)
			for loc in self.__locations:
				if type(loc) == str:
					self.counter += 1
					search_res = GeoQuery(loc,self.country_code,search)	#Objet résultat
					if search_res.result is not None:
						return search_res
		return search_res	#avec champ 'result' == None


class GeoQuery:
	def __init__(self, loc, code, searchtype='R', max_return=None):
		self.location = loc

		if type(code) != str: 
			raise TypeError(typerr_msg)
		if searchtype not in SEARCH_TYPES:
			raise GeoError(searchtype)
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
							'GeoNames request failed',search_res.headers,None)



class GeoError(Exception):
	def __init__(self, string):
		super().__init__('\''+string+'\''+' '+'n\'est pas un type de recherche valide')