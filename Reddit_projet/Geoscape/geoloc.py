#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections.abc import Sequence
from urllib.error import HTTPError

from geocoder import geonames

"""GeoNames feature classes ('fcl' dans le JSON de Geonames, champ 'feature_class' de geocoder)
		A   Administrative divisions
		H   Surface waters
		L   Parks/reserves/regions
		P   Populated places
		R   Roads
		S   Structures
		T   Mountains/islands
		U   Undersea
		V   Woodlands
"""



SEARCH_TYPES = ['E', 'EN', 'EH', 'EN EH', 'EH EN', 'RF', 'R']
FEATURE_CLASSES = ['A','H','L','P','R','S','T','U','V']
EH_STANDARD = ['A','P','R','S']
EN_STANDARD = ['H','L','T','U','V']
FUZ_STANDARD = 0.8

typerr_msg = 'country code must be a string'



class LocationList(Sequence):
	def __init__(self, code, loclist, mset=EH_STANDARD, nset=EN_STANDARD, fuzzy=FUZ_STANDARD):
		self.__locations = [loc for loc in loclist if type(loc) == str]
		self.__manmadeset = set(mset)
		self.__naturalset = set(nset)
		self.fuzzy = fuzzy

		self.country_code = code
		if type(self.country_code) != str:
			raise TypeError(typerr_msg)
		self.counter = 0

		if not self.__naturalset.isdisjoint(self.__manmadeset):
			self.__naturalset -= self.__manmadeset
		if len(self.__manmadeset) + len(self.__naturalset) < len(FEATURE_CLASSES):
			for fcl in FEATURE_CLASSES:
				if fcl not in self.__manmadeset | self.__naturalset:
					self.__manmadeset.add(fcl)

		if not self.__manmadeset:
			raise PartitionError('manmade')
		if not self.__naturalset:
			raise PartitionError('natural')

	def __len__(self):
		return len(self.__locations)

	def __getitem__(self, key):
		return self.__locations[key]

	def __repr__(self):
		return ('locations.LocationList('+self.country_code
			   +',['+','.join(str(loc) for loc in self.__locations)+'])')

	def __str__(self):
		return '['+', '.join(self.__locations)+']'

	#Méthodes héritées: __contains__, __iter__, count, index

	#Pas de __setitem__
	#Pas de __delitem__

	def reinit(self, code, loclist):
		self.__locations = [loc for loc in loclist if type(loc) == str]

		self.country_code = code
		if type(self.country_code) != str:
			raise TypeError(typerr_msg)
		self.counter = 0

	def add_natural(self, *f_classes):
		self.__naturalset |= set(f_classes)
		self.__manmadeset -= self.__naturalset
		if not self.__manmadeset:
			raise PartitionError('manmade')

	def add_manmade(self, *f_classes):
		self.__manmadeset |= set(f_classes)
		self.__naturalset -= self.__manmadeset
		if not self.__naturalset:
			raise PartitionError('natural')

	def set_fuzzy(self, fuzzy):
		self.fuzzy = fuzzy

	def geo_search(self, *search_order):
		self.counter = 0

		if not search_order:
			return None
		if not self.__locations:
			dummy = GeoQuery.__new__(GeoQuery)
			setattr(dummy,'location',None)
			setattr(dummy,'result',None)
			return dummy

		for search in search_order:
			if search not in SEARCH_TYPES:
				raise GeoError(search)
			for loc in self.__locations:
				self.counter += 1
				search_res = GeoQuery(loc,self.country_code,search,self.__manmadeset,
									self.__naturalset,self.fuzzy)	#Objet résultat
				if search_res.result is not None:
					return search_res
		return search_res	#avec champ 'result' == None


class GeoQuery:
	def __init__(self, loc, code, searchtype='R', mset=EH_STANDARD, nset=EN_STANDARD, \
			fuzzy=FUZ_STANDARD, max_return=None):
		self.location = loc

		if type(code) != str: 
			raise TypeError(typerr_msg)
		if searchtype not in SEARCH_TYPES:
			raise GeoError(searchtype)
		extra_args = {'fuzzy': fuzzy} if searchtype == 'RF' else {}
		rows = max_return if max_return is not None else 1

		if searchtype in ['E','EH','EN','EH EN','EN EH']:
			extra_args['name_equals'] = loc
			if max_return is None:
				rows = 10

		search_res = geonames(loc,key='scrapelord',auth='Blorp86',country=code,
							maxRows=rows,**extra_args)

		if search_res.status_code == 200:
			if search_res:
				if searchtype in ['R','RF','E']:
					self.result = search_res[0]
					return
				elif searchtype in ['EH EN', 'EH']:
					fcl = mset
				else:
					fcl = nset
				for res in search_res:
					if res.feature_class in fcl:
						self.result = res
						return
				if searchtype in ['EH EN','EN EH']:
					self.result = search_res[0]
				else:
					self.result = None
			else:
				self.result = None
		else:
			raise HTTPError(search_res.url,search_res.status_code,
							'GeoNames request failed',search_res.headers,None)



class GeoError(Exception):
	def __init__(self, string):
		super().__init__('\''+string+'\''+' '+'n\'est pas un type de recherche valide')



class PartitionError(Exception):
	def __init__(self, string):
		super().__init__('l\'ensemble humain est vide' if string=='manmade'
					else 'l\'ensemble naturel est vide')