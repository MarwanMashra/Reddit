#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import copy, geocoder, json, os, pprint, praw, re, sys, time
import treetaggerwrapper as ttagger
import Geoscape.mongo as mongo
import Geoscape.process as proc
from flask import Blueprint, jsonify, request
from prawcore import NotFound
from itertools import groupby
from more_itertools import windowed

rgn = Blueprint('rgn',__name__)



def geonames_query(location, country_code, dic_results, dic_mongo, exact=True, fuzzy=False):
	"""Recherche du lieu sur geonames à partir d'un lieu potentiel de la liste produite par
	la fonction location_finder. D'abord recherche d'un match exact (exact=True), en
	privilégiant les lieux naturels plutôt qu'humains; sinon choix du premier résultat de
	recherche.
	Stockage des informations dans un dico temporaire qui sera ensuite rajouté au dico de
	tous les résultats, et dans un dico qui sera enregistré dans la base de données.
	Par défaut, fuzzy=False et la recherche se fait avec fuzzy=1. Avec le paramètre à True,
	la recherche est élargie est permet de compenser les potentielles fautes d'orthographe.
	"""

	ex_arg = {'name_equals': location} if exact else {}
	fuz_arg = {'fuzzy': 0.8} if fuzzy else {}

	res = geocoder.geonames(location,key='scrapelord',auth='Blorp86',
							country=country_code,maxRows=10,**ex_arg,**fuz_arg)

	if res.status_code == 200:
		if res:
			search_res = res[0]

			if exact:
				for r in res:
					if r.feature_class in ['H','L','T','U','V']:
						search_res = r
						break

			dic_results['head']['total'] += 1

			dic_mongo['name'] = search_res.address	#Nom
			dic_mongo['lng'] = search_res.lng
			dic_mongo['lat'] = search_res.lat
			dic_mongo['feature_class'] = search_res.feature_class
			dic_mongo['location'] = location

			dic_results['results'].append(dic_mongo)
			if exact:
				print('Meilleur résultat Geonames: ',dic_mongo['name'])
			else:
				print('Premier résultat Geonames: ',dic_mongo['name'])

			return True

		else:
			return False

	else:
		sys.exit("Erreur dans la recherche Geonames: code "+search_res.status_code+". Arrêt du programme.")



def location_finder(country, version, tags):
	"""Recherche des lieux potentiels dans le titre de la soumission Reddit. La recherche de base
	considère que les noms propres voisins forment un lieu. Par-dessus cette recherche, les règles
	générées par l'analyse des résultats des tests utilisateurs fournissent des mots particuliers
	à prendre en compte (dotés de l'étiquette 'TAR') ou à ignorer (l'étiquette 'IGN').
	En plus des lieux potentiels, la liste résultat stocke le nombre de mots non sélectionnés
	séparant les lieux retenus.
	"""

	db = mongo.MongoLoad({'country': country, 'search_version': {'$lte': version}},
						 {'expr': 1, 'pos': 1, 'take': 1, '_id': 0})

	for rule in db.retrieve('Nouvelles_Regles'):
		expr_len = len(rule['pos'])
		expr_str = ''
		expr_tags = []

		for i in range(len(tags)):
			if i - expr_len + 1 >= 0:
				expr_str = ' '.join(tags[i][0] for i in range(i-expr_len+1,i+1))
				expr_tags = [tags[i][1] for i in range(i-expr_len+1,i+1)]

			if expr_str == rule['expr']:
				if all(expr_tags[i] == rule['pos'][i] for i in range(expr_len)):
					left = i - expr_len

					if rule['take'] == 0:
						for j in range(i-expr_len,i+1):
							if tags[j][1] != 'NP0':
								tags[j] = (tags[j][0],'TAR',tags[j][2])

					elif rule['take'] == 'X':
						for j in range(i-expr_len,i+1):
							tags[j] = (tags[j][0],'IGN',tags[j][2])

					elif rule['take'] == 1:
						if i+1 < len(tags) and tags[i+1][1] != 'NP0':
							tags[i+1] = (tags[i+1][0],'TAR',tags[i+1][2])

					elif rule['take'] == 'R':
						if i+1 < len(tags):
							tags[i+1] = (tags[i+1][0],'IGN',tags[i+1][2])		

					elif rule['take'] == -1:
						if left >= 0 and tags[left][1] != 'NP0':
							tags[left] = (tags[left][0],'TAR',tags[left][2])

					elif rule['take'] == 'L':
						if left >= 0:
							tags[left] = (tags[left][0],'IGN',tags[left][2])
							
					else:
						if i+1 < len(tags) and tags[i+1][1] == 'NP0' \
						and left >= 0 and tags[left][1] == 'NP0':
							tags[i] = (tags[i][0],'TAR',tags[i][2])

	loc_list = [' '.join(t[0] for t in g) if k else len(list(g)) for k, g
				in groupby(tags, key = lambda x: x[1] == 'NP0' or x[1] == 'TAR')]

	return loc_list



@rgn.route('/scraping',methods=['GET'])
def scraping():
	"""Si l'utilisateur n'a pas demandé un scraping, recherche de documents du pays sélectionné
	dans la base de données; ces documents et leurs liens vers les photos seront renvoyés.
	Si l'utilisateur a demandé un scraping, ou s'il n'y a pas ou pas assez de documents du pays
	sélectionné dans la base de données, configuration et lancement du scrape sur Reddit, puis
	étiquetage des titres des soumissions résultats par TreeTagger, et analyse des étiquettes
	pour obtenir une liste de lieux potentiels.
	Ces lieux sont recherchés sur geonames. Les résultats de cette dernière recherche sont chargés
	dans deux dictionnaires, l'un pour l'affichage des photos sur le site et l'autre pour stocker
	les résultats dans la base de données sur mongoDB.
	NB: le scraping tente toujours d'obtenir de nouvelles photos (absentes de mongoDB).
	"""

	#Paramètres de la requête Javascript
	rgnversion = request.args.get('search_version')
	country = request.args.get('country')
	country_code = request.args.get('country_code')
	limit = int(request.args.get('nombre_image'))
	scrape_requested = True if request.args.get('scraping') == 'true' else False

	#Dico de résultats pour l'affichage sur le site
	search_res = geocoder.geonames(country,key='scrapelord',auth='Blorp86',maxRows=1)
	dic_results = {'head': {'total': 0,
							'country': {'name': country, 'lng': search_res[0].lng,
										'lat': search_res[0].lat}},
				   'results': []}
	#Liste de chargement pour la base de données
	database_list = []

	if scrape_requested: #On ne charge que les img_url
		load_arg = {'img_url': 1, '_id': 0}
	else: #On charge le document pour l'affichage
		load_arg = {'scraped_title': 0, 'location_list': 0,
					'feature_class': 0, '_id': 0}

	existing_urls = []
	check_db = mongo.Mongo.mongocheck('Resultats_RGN')

	#Initialisation de la collection des résultats si elle n'existe pas
	if not check_db:
		dbstart = mongo.MongoSave([{'key': 'Initialisation de la collection Resultats_RGN.'}])
		dbstart.storeindb('Resultats_RGN',img_url='A',search_version='D')
		dbstart.nonunique_index('Resultats_RGN',country='A',search_version='D')

	#Les documents pris dans la base de données sont chargés dans le dictionnaire de résultats
	else:
		dbfinder = mongo.MongoLoad({'search_version': rgnversion, 'country': country},load_arg)
		for doc in dbfinder.retrieve('Resultats_RGN'):
			if not scrape_requested:
				dic_results['head']['total'] += 1
				dic_results['results'].append(doc)
			existing_urls.append('-url:'+doc['img_url'])

	if scrape_requested or dic_results['head']['total'] < limit:
		#Configuration recherche reddit
		reddit = praw.Reddit(client_id='v7xiCUUDI3vEmg',client_secret='5Q6FHHJT-SW0YRnEmtWkekWsxHU',
			     password='Blorp86',user_agent='PhotoScraper',username='scrapelord')

		target_sub = reddit.subreddit('EarthPorn')
		query = 'title:'+country
		print('\033[92m'+target_sub.display_name+'\033[0m'
			  '\nRésultats de recherche pour les soumissions reddit avec: ',query,'\n')

		#Exclure les documents déjà récupérés
		user_limit = limit

		if len(query) + len(existing_urls) + sum(len(url) for url in existing_urls) <= 512:
			query += (' ' + ' '.join(existing_urls)).rstrip()
			limit -= dic_results['head']['total']
		else: #512 caractères max dans une requête Reddit
			limit = 1000 #Max permis par Reddit
			existing_urls = [url[5:] for url in existing_urls]

		#Config TreeTagger. Le dossier TreeTagger doit être dans le même dossier que ce script
		reddit_tagger = ttagger.TreeTagger(TAGLANG='en',TAGDIR=os.getcwd()+'/TreeTagger')

		#Résultats de la recherche dans le subreddit
		test_posts = target_sub.search(query,limit=limit)

		for post in test_posts:
			try:
				 attempt = post.url
			except NotFound:
				continue #Problème avec la photo; éliminé

			if post.url in existing_urls:
				continue #Déjà stocké dans la base de données; éliminé

			if re.search(country+'[.,/[( ]',post.title): #Pays suivi de '.' ',' '/' '[' '(' ou ' '
				#Saute aux plus une fois des caractères entre [] ou () au début du texte et s'arrête au premier [ ou (
				res = re.search('^(?:[\[(].*[\])])?([^[(]+)',post.title)
				if (res):
					print(res.group(1))

					#Tagging: génère une liste de triplets: (word=..., pos=..., lemma=...)
					reddit_tags = ttagger.make_tags(reddit_tagger.tag_text(res.group(1)),
								  exclude_nottags=True)

					#Le nom du pays est exclu des lieux potentiels; rajouté seulement en dernier recours
					country_split = country.casefold().split(' ')
					size = len(country_split)
					indexes = []
					if size > 1:
						name_tags = [t[0].casefold() for t in reddit_tags]
						for window in enumerate(windowed(name_tags,size)):
							if all(window[1][i] == country_split[i] for i in range(size)):
								indexes.extend([i for i in range(window[0],window[0]+size)])

					for index, tag in enumerate(reddit_tags):
						if tag[1] == 'NP': #Tag nom propre sous Windows
							reddit_tags[index] = (tag[0],'NP0',tag[2])
						if tag[0].casefold() == country.casefold() or index in indexes:
							reddit_tags[index] = (tag[0],'CTY',tag[2])
					pprint.pprint(reddit_tags)

					#Recherche des lieux potentiels, avec stocké entre les lieux le nombre de mots non choisis
					location_list = location_finder(country,rgnversion,reddit_tags)

					print('Lieux trouvés:',end='')
					print(location_list,'\n')

					#Geonames
					date = time.gmtime(post.created_utc)
					dic_mongo = {'link': 'https://www.reddit.com'+post.permalink,
								 'img_url': post.url, 'search_version': rgnversion,
								 'country': country, 'country_code': country_code,
								 'scraped_title': res.group(1).strip(), 'text': post.title,
								 'tag_list': reddit_tags, 'location_list': location_list,

								 'date': {'year': date.tm_year, 'month': date.tm_mon,
										  'day': date.tm_mday, 'hour': date.tm_hour,
										  'min': date.tm_min, 'sec': date.tm_sec}}

					try:
						attempt = post.author.icon_img
					except NotFound:
						pass
					else:
						dic_mongo['author'] = {'name': post.author.name, 'icon': post.author.icon_img,
										       'profile': 'https://www.reddit.com/user/'+post.author.name}

					"""Recherche de match exact pour tous les lieux de la liste.
					Si aucun résultat, nouveau parcours de la liste et on prend le premier résultat.
					Si aucun résultat, on passe à une fuzzy search.
					"""
					this_search = [True,False,False,False,False,True]

					while 'name' not in dic_mongo and this_search:
						for loc in location_list:
							if type(loc) == str:
								if geonames_query(loc,country_code,dic_results,dic_mongo,
										exact=this_search[0],fuzzy=this_search[1]):
									break
						this_search = this_search[2:]

					#En dernier recours, le pays lui-même s'il est dans le titre
					if 'name' not in dic_mongo and country in res.group(1):
						location_list.append(country)
						dic_mongo['location_list'] = location_list
						geonames_query(country,country_code,dic_results,dic_mongo,exact=True)

					if 'location' in dic_mongo:
						dic_tostore = copy.deepcopy(dic_mongo)
						database_list.append(dic_tostore)

					user_limit -= 1
					if not user_limit:
						break

					print('\n###############')
				else:
					print('')

		#Chargement dans la base de données des documents générés par le scrape
		documents = mongo.MongoSave(database_list)
		documents.storeindb('Resultats_RGN')

	return jsonify(dic_results)
