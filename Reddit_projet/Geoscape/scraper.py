#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import copy, json, os, pprint, praw, re, requests, sys, time, treetaggerwrapper
import Geoscape.mongo as mongo
from flask import Blueprint, jsonify, request
from itertools import groupby
from more_itertools import windowed

rgn = Blueprint('rgn',__name__)



"""Stockage dans un dictionnaire des informations sur le résultat geonames."""
def dicload(res_dic, store_dic, opt_loc=None):
	store_dic['name'] = res_dic['name']
	store_dic['lng'] = res_dic['lng']
	store_dic['lat'] = res_dic['lat']

	if opt_loc is not None:
		store_dic['featureclass'] = res_dic['fcl']
		store_dic['location'] = opt_loc



"""Recherche du lieu sur geonames à partir d'un lieu potentiel de la liste produite par
la fonction locationsearch. D'abord recherche d'un match exact, en privilégiant les lieux
naturels plutôt qu'humains; sinon choix du premier résultat de recherche.
Stockage des informations dans un dico temporaire qui sera ensuite rajouté au dico de
tous les résultats, et dans un dico qui sera enregistré dans la base de données.
Par défaut, fuzzy=False et la recherche se fait avec fuzzy=1. Avec le paramètre à True,
la recherche est élargie est permet de compenser les potentielles fautes d'orthographe.
"""
"""Geonames feature classes ('fcl')
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
def geonames_query(location, country_code, dic_results, dic_tmp, dic_mongo, exact=False, fuzzy=False):
	url = 'http://api.geonames.org/searchJSON'
	data = '?q='+location+'&country='+country_code+'&username=scrapelord'
	if fuzzy:
		data += '&fuzzy=0.8'
	search_res = requests.get(url+data,auth=('scrapelord','Blorp86'))

	if search_res.status_code == 200:
		search_res = search_res.json() #Décodeur JSON appliqué à l'objet Response renvoyé par la requête
		if search_res['totalResultsCount'] != 0:
			dic_results['head']['total'] += 1
			print_res = '' #Pour affichage test
			
			if exact:
				prio_list = []
				for res in search_res['geonames']:
					if res['name'].lower() == location.lower():
						if res['fcl'] in ['A','P','R','S'] and not prio_list:
							prio_list.append(res)
						elif res['fcl'] in ['H','L','T','U','V']:
							prio_list.insert(0,res)
							break
				if prio_list:
					dicload(prio_list[0],dic_tmp)
					dicload(prio_list[0],dic_mongo,location)
					print_res = prio_list[0]['name']

				else:
					return False

			else:
				dicload(search_res['geonames'][0],dic_tmp)
				dicload(search_res['geonames'][0],dic_mongo,location)
			dic_results['results'].append(dic_tmp)
			print('Premier résultat Geonames: ',search_res['geonames'][0]['name'])
			print('Meilleur résultat Geonames: ',print_res)
			
			return True

		else:
			return False
	else:
		sys.exit("Erreur dans la recherche Geonames: code "+search_res.status_code+". Arrêt du programme.")



"""Configuration et lancement du reddit scrape, puis tagging des titres des soumissions reddit
résultats par TreeTagger et analyse des tags pour obtenir une liste de lieux potentiels. Ces
lieux sont recherchés sur geonames. Les résultats de cette dernière recherche sont chargés dans
deux dictionnaires, l'un pour l'affichage des photos sur le site et l'autre pour stocker les
résultats dans la base de données sur mongoDB.
"""
@rgn.route('/scraping',methods=['GET'])
def scraping():

	#Paramètres de la requête Javascript
	rgnversion = request.args.get('search_version')
	country = request.args.get('country')
	country_code = request.args.get('country_code')
	scrape_requested = True if request.args.get('scraping') == 'true' else False

	#L'utilisateur souhaite consulter les images déjà stockées plutôt que de scraper
	stored_docs = []
	check_db = mongo.Mongo.mongocheck('Resultats_RGN')

	if not scrape_requested and check_db:
		dbfinder = mongo.MongoLoad({'search_version': rgnversion, 'country': country},
							   	   {'title': 1, 'img_url': 1, 'name': 1, 'lng': 1,
							   	    'lat': 1, '_id': 0})
		stored_docs = list(dbfinder.retrieve('Resultats_RGN',limit=20))

	#Initialisation de la collection des résultats sur la base de données si elle n'existe pas
	if not check_db:
		dbstart = mongo.MongoSave([{'key': 'Initialisation de la collection Resultats_RGN.',
									'count': 0}])
		dbstart.storeindb('Resultats_RGN',img_url='A',search_version='D')
		dbstart.nonunique_index('Resultats_RGN',country='A',search_version='D')

	#Dico de résultats pour l'affichage sur le site
	search_res = requests.get('http://api.geonames.org/searchJSON?q='+country+'&username=scrapelord',
				 auth=('scrapelord','Blorp86'))
	search_res = search_res.json()
	
	dic_results = {
					'head': {
								'total': 0,
								'country': {
											'name': country,
											'lng': search_res['geonames'][0]['lng'],
											'lat': search_res['geonames'][0]['lat'] 
										   }
							},
					'results': []
				  }
	#Liste de chargement pour la base de données
	database_list = []

	if not scrape_requested and stored_docs:
		for doc in stored_docs:
			dic_results['head']['total'] += 1
			dic_results['results'].append({
											'img': doc['img_url'],
											'text': doc['title'],
											'search_version': rgnversion,
											'name': doc['name'],
											'lng': doc['lng'],
											'lat': doc['lat']
										})

	else:
		#Configuration recherche reddit
		reddit=praw.Reddit(client_id='v7xiCUUDI3vEmg',client_secret='5Q6FHHJT-SW0YRnEmtWkekWsxHU',
			   password='Blorp86',user_agent='PhotoScraper',username='scrapelord')

		target_sub = reddit.subreddit('EarthPorn')                     
		query = 'title:'+country
		print('\033[92m'+target_sub.display_name+'\033[0m'
			  '\nRésultats de recherche pour les soumissions reddit avec: ',query,'\n')

		#Configuration TreeTagger. Le dossier TreeTagger doit être dans le même dossier que ce script
		reddit_tagger = treetaggerwrapper.TreeTagger(TAGLANG='en',TAGDIR=os.getcwd()+'/TreeTagger')

		#Résultats de la recherche dans le subreddit
		test_posts = target_sub.search(query,limit=20)
		for post in test_posts:
			try:
				 attempt = post.url
			except praw.exceptions.APIException as e:
				print(e.message())
				continue

			if re.search('.*'+country+'[.,/[( ]',post.title): #Pays suivi de '.' ',' '/' '[' '(' ou ' '
				#Match tous les caractères depuis le début de la ligne sauf [OC] et s'arrête au premier [ ou (
				res = re.search('^(?:\[OC\])?([^[(]+)',post.title)
				if (res):
					print(res.group(1))

					#Tagging: génère une liste de triplets: (word=..., pos=..., lemma=...)
					reddit_tags = treetaggerwrapper.make_tags(reddit_tagger.tag_text(res.group(1)),
								  exclude_nottags=True)

					#Le nom du pays est exclu des lieux potentiels; rajouté seulement en dernier recours
					country_split = country.casefold().split(' ')
					size = len(country_split)
					indexes = []
					if size > 1:
						name_tags = [t[0].casefold() for t in reddit_tags]
						for window in enumerate(list(windowed(name_tags,size))):
							if all(window[1][i] == country_split[i] for i in range(size)):
								indexes.extend([i for i in range(window[0],window[0]+size)])

					for index, tag in enumerate(reddit_tags):
						if tag[1] == 'NP': #Tag nom propre sous Windows
							reddit_tags[index] = (tag[0],'NP0',tag[2])
						if tag[0].casefold() == country.casefold() or index in indexes:
							reddit_tags[index] = (tag[0],'CTY',tag[2])
					pprint.pprint(reddit_tags)

					#Recherche des lieux potentiels, avec stocké entre les lieux le nombre de mots non choisis
					location_list = [
										' '.join([t[0] for t in g]) if k
										else len(list(g))
										for k, g in groupby(reddit_tags, key = lambda x: x[1] == 'NP0')
									]

					print('Lieux trouvés:',end='')
					print(location_list,'\n')

					#Geonames
					dic_mongo = {
									'link': post.permalink,
									'img_url': post.url, #Lien direct vers la photo
									'search_version': rgnversion,
									'country': country,
									'title': res.group(1).strip(),
									'tag_list': reddit_tags,
									'location_list': location_list
								}

					#Dico initialisé en dehors de la fonction pour pouvoir comparer après l'appel
					date = time.gmtime(post.created_utc)
					dic_tmp = {
								'img': post.url,
								'text': post.title,
								'search_version': rgnversion,
								'url': 'https://www.reddit.com'+post.permalink,
								'date': {
											'year': date.tm_year,
											'month': date.tm_mon,
											'day': date.tm_mday,
											'hour': date.tm_hour,
											'min': date.tm_min,
											'sec': date.tm_sec
										},
								'author': {
											'name': post.author.name,
											#'icon': post.author.icon_img,
											'profile': 'https://www.reddit.com/user/'
													   +post.author.name
										  }
							  }

					"""Recherche de match exact pour tous les lieux de la liste.
					Si aucun résultat, nouveau parcours de la liste et on prend le premier résultat.
					Si aucun résultat, on passe à une fuzzy search.
					"""
					this_search = [True,False,False,False,False,True]

					while 'name' not in dic_tmp and this_search:
						for loc in location_list:
							if type(loc) == str:
								if geonames_query(loc,country_code,dic_results,dic_tmp,
										dic_mongo,exact=this_search[0],fuzzy=this_search[1]):
									break
						this_search = this_search[2:]

					#En dernier recours, le pays lui-même s'il est dans le titre
					if 'name' not in dic_tmp and country in res.group(1):
						location_list.append(country)
						dic_mongo['location_list'] = location_list
						geonames_query(country,country_code,dic_results,dic_tmp,
							dic_mongo,exact=True)

					if 'location' in dic_mongo:
						dic_tostore = copy.deepcopy(dic_mongo)
						database_list.append(dic_tostore)
					print('\n###############')
				else:
					print('')

		#Chargement dans la base de données des documents générés par le scrape
		documents = mongo.MongoSave(database_list)
		documents.storeindb('Resultats_RGN')

	return jsonify(dic_results)

