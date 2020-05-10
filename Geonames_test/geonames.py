#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""IMPORTANT: GeoNames limite le nombre de requêtes à 1000 r/heure maximum. 
Pour n lieux à tester et k types de recherche dans le cycle, il y aura dans le pire des
cas n*k requêtes.

175 noms dans le fichier de test (donc 175*k requêtes).
La durée d'un cycle dépend surtout des serveurs GeoNames. En général, 30 à 100 secondes.
"""

import sys
from os import getcwd
from re import finditer
from time import time

import Geoscape.server.geoloc as geo
#Lancer depuis le dossier contenant le dossier Geonames_test et Geoscape



def test(searchlist):
	print('########################################\n')

	print('CYCLE DE RECHERCHE ',searchlist)

	with open('Geonames_test/geonames_test.txt','r') as file:
		timer_start = time()
		score = 0
		total_count = 0

		for line in file:
			pre_score = score
			split_line = line.split(',')
			location = geo.LocationList(split_line[2].lstrip(),[split_line[1].lstrip()])
			geo_res = location.geo_search(geokey,geoauth,*searchlist)

			split_line = line.split(':') #Bon résultats [1], acceptables [2]

			good_res = split_line[1].split(',') #Parmi les bons
			if geo_res.result:
				for res in good_res[:-1]: #Les résultats sans le 'Accep'
					if res[:-1].strip() == geo_res.result.address and res[-1] == geo_res.result.feature_class:
						score += 1
						break

				if score == pre_score and split_line[2]:
						ok_res = split_line[2].split(',') #Parmi les acceptables
						ok_res[-1] = ok_res[-1].rstrip() #Supprime le \n
						for res in ok_res:
							if res[:-1].strip() == geo_res.result.address and res[-1] == geo_res.result.feature_class:
								score += 0.5
								break

			elif good_res[0].strip() == 'aucun résultat':
				score += 1

			total_count += location.counter

	timer_stop = time()

	print('Score:',score,'points sur 175',f'({score/175*100:.2f}%).')
	print(f'Nombre de requêtes: {total_count}.')
	print(f'Durée: {timer_stop - timer_start:.2f} secondes (temps absolu).\n') #Très peu indicatif

	while True:
		select = input('Souhaitez vous procéder à un autre test? y/n')

		if select in ['y','Y']:
			break
		elif select in ['n','N']:
			exit()
		else:
			print('Entrez \'y\' pour retourner sur l\'écran de lancement ou \'n\' pour quitter.')



print('########################################')
print('\033[5m###\033[0m Interface de tests pour GEONAMES \033[5m###\033[0m')
print('########################################')

###SAISIE

with open('Geoscape/geoscape.ini','r') as initfile:
	f = initfile.readlines()

for line in f:
	if line.startswith('key='):
		geokey = line[4:].strip()
	if line.startswith('auth='):
		geoauth = line[5:].strip()

if 'geokey' not in locals() or 'geoauth' not in locals():
	sys.exit('Erreur à l\'initialisation: les codes d\'accès pour geonames ne sont '
			 'pas présents. Complétez votre fichier de configuration.')

while True:
	print("""\nEntrez un cycle de recherche en une saisie -- séparez les termes par un espace.
		R: recherche standard
		RF: recherche fuzzy
		E: recherche exacte
		EN: recherche exacte sur ensembles naturels
		EH: recherche exacte sur ensembles humains
	Q pour quitter.
	""")

	search_patterns = []

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

	if good_to_go and search_patterns:
		test(search_patterns)
