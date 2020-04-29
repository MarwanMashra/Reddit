#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""IMPORTANT: GeoNames limite le nombre de requêtes à 1000 r/heure maximum. 
Pour n lieux à tester et k types de recherche dans le cycle, il y aura dans le pire des
cas n*k requêtes.

En terme du nombre de requêtes il serait plus efficace de faire une seule recherche
standard, puis chercher les matchs exacts dans les résultats si l'on veut la recherche
exacte, avant de prendre le premier si l'on ne trouve pas de match. Mais la recherche
'exacte' prend en compte les noms alternatifs des lieux et donne de meilleurs résultats
que du simple string matching.

175 noms dans le fichier de test (donc 175*k requêtes).
En général, 60 à 100 secondes pour un cycle.

NB: les résultats de ces tests doivent être analysés à la main.
"""

from os import getcwd
from re import finditer
from time import time

import Geoscape.geoloc as geo
#Lancer depuis le dossier contenant le dossier Geonames_test et Reddit_projet



print('########################################')
print('\033[5m###\033[0m Interface de tests pour GEONAMES \033[5m###\033[0m')
print('########################################')

###SAISIE

print("""\nEntrez un cycle de recherche en une saisie -- séparez les termes par un espace.
	R: recherche standard
	RF: recherche fuzzy
	E: recherche exacte
	EN: recherche exacte sur ensembles naturels
	EH: recherche exacte sur ensembles humains
Q pour quitter.
""")

search_patterns = []

while True:
	pattern = input()
	good_to_go = True

	res = [match.start() for match in finditer('EN EH|EH EN',pattern)]
	for idx in res:
		pattern = pattern[:idx+2] + '-' + pattern[idx+3:]
	
	pattern = (' '.join(substr.split('-')) if substr in ['EN-EH','EH-EN']
			   else substr for substr in pattern.split())

	for searchtype in pattern:
		if searchtype in geo.SEARCH_TYPES:
			search_patterns.append(searchtype)

		elif searchtype == 'Q':
			exit()

		else:
			print('Type de recherche non reconnu. Recommencez.')
			search_patterns.clear()
			good_to_go = False
			break

	if good_to_go:
		break

###TESTS
print('########################################\n')

print('CYCLE DE RECHERCHE ',search_patterns)

newfile = open('Geonames_test/geonames_results.txt','a')
newfile.write('### '+', '.join(search_patterns)+' ###\n')

with open('Geonames_test/geonames_test.txt','r') as file:
	timer_start = time()
	total_count = 0

	for line in file:
		split_line = line.split(',')
		location = geo.LocationList(split_line[2].lstrip(),[split_line[1].lstrip()])
		geo_res = location.geo_search(*search_patterns)

		if geo_res.result:
			newfile.write(split_line[1]+':\t'+geo_res.result.address+'\t'+geo_res.result.feature_class+'\n')
		else:
			newfile.write(split_line[1]+':\t'+'Aucun résultat.\n')

		total_count += location.counter

timer_stop = time()
newfile.write('\n')
newfile.close()

print('Nombre de requêtes:',total_count)
print('Durée:',timer_stop - timer_start,'secondes (temps absolu).') #Très peu indicatif

