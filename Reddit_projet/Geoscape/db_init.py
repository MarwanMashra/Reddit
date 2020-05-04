#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
from os import getcwd

from pymongo import MongoClient



class mongo_access:
	"""Permet d'initialiser le code d'accès mongoDB au moment de l'import dans
	le module mongo: les variables statiques d'une classe sont initialisées à
	l'import.
	"""
	with open(getcwd()+'/Geoscape/geoscape.ini','r') as initfile:
		f = initfile.readlines()

	for line in f:
		if line.startswith('client='):
			client = MongoClient(line[7:].strip()).RedditScrape

	if 'client' not in locals():
		sys.exit('Erreur à l\'initialisation: le code serveur pour l\'accès à mongoDB '
				 'n\'est pas présent. Complétez votre fichier de configuration.')


