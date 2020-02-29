#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import copy, json, mongo, more_itertools, os, pprint, praw, re, requests, sys, treetaggerwrapper
from flask import Flask, render_template, request, jsonify

#This code attempts to conform to PEP8

"""Feature classes ('fcl')
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


"""Recherche de lieux potentiels par création de chaîne à partir des noms propres
voisins (NP0 sous Linux, NP sous Windows). Ces lieux sont stockés dans une liste.
La méthode peek() permet de regarder l'élément suivant de la liste. Elle prend un
tuple par défaut qui sera consulté en fin d'itération pour ne pas causer une erreur
de sortie de liste.
La méthode rstrip() élimine les blancs potentiels en fin de chaîne.
"""
def locationsearch(location_list, p_iter):
	location = ''
	for word,pos,lemma in p_iter:
		if pos in ['NP0','NP'] and word[0].isalpha():
			location += word+' '
			if p_iter.peek(('end','end','end'))[1] not in ['NP0','NP']:
				location_list.append(location.rstrip())
				location = ''



app= Flask(__name__)

@app.route('/')
@app.route('/map')
@app.route('/map.html')
def home():
	return render_template('map.html')

#La fonction appelée par la requête Javascript
@app.route('/scraping',methods=['GET','POST'])
def scraping():
	#Configuration du scraper, ne pas modifier
	reddit=praw.Reddit(client_id='v7xiCUUDI3vEmg',client_secret='5Q6FHHJT-SW0YRnEmtWkekWsxHU',
		   password='Blorp86',user_agent='PhotoScraper',username='scrapelord')

	#Configuration recherche reddit
	rgnversion = '1.00'
	target_sub = reddit.subreddit('EarthPorn')
	#Paramètres de la requête Javascript
	country = request.args.get('country')
	country_code = request.args.get('country_code')
	query = 'title:'+country
	print('\033[92m'+target_sub.display_name+'\033[0m','\nRésultats de recherche pour les soumissions reddit avec: ',query,'\n')

	#Configuration TreeTagger. Le dossier TreeTagger doit être dans le même dossier que ce script
	reddit_tagger=treetaggerwrapper.TreeTagger(TAGLANG='en',TAGDIR=os.getcwd()+'/TreeTagger')

	#Dico stockant tous les résultats de recherche (results) + informations générales (head)
	dic_results = {}
	dic_results['head'] = {}
	dic_results['head']['total'] = 0
	dic_results['head']['country'] = {}
	dic_results['head']['country']['name'] = country

	#Coordonnées pays
	search_res = requests.get('http://api.geonames.org/searchJSON?q='+country+'&username=scrapelord',
				 auth=('scrapelord','Blorp86'))
	search_res = search_res.json()
	dic_results['head']['country']['lng'] = search_res['geonames'][0]['lng']
	dic_results['head']['country']['lat'] = search_res['geonames'][0]['lat'] 
	dic_results['results'] = []

	#Liste de chargement pour la base de données
	database_list = []

	#Résultats de la recherche dans le subreddit
	test_posts = target_sub.search(query,limit=15)
	for post in test_posts:
		if re.search('.*'+country+'[.,/[( ]',post.title): #Pays suivi de '.' ',' '/' '[' '(' ou ' '
			#Match tous les caractères depuis le début de la ligne sauf [OC] et s'arrête au premier [ ou (
			res = re.search('^(?:\[OC\])?([^[(]+)',post.title)
			if (res):
				print(res.group(1))

				#Tagging
				reddit_tags = treetaggerwrapper.make_tags(reddit_tagger.tag_text(res.group(1)),
							  exclude_nottags=True)
				#Liste de triplets: (word=..., pos=..., lemma=...)
				pprint.pprint(reddit_tags)

				#Recherche des lieux potentiels
				if (country.lower() in (t[2].lower() for t in reddit_tags)):  #Garantir la présence du mot 'NomDuPays'
					title_split = [t[2].lower() for t in reddit_tags].index(country.lower())
					location_list = []
					#Recherche prioritaire du lieu: la liste jusqu'au mot 'NomDuPays'
					locationsearch(location_list,more_itertools.peekable(reddit_tags[:title_split]))
					#Priorité secondaire: la liste à la suite du mot 'NomDuPays'
					if len(reddit_tags) > title_split+1:
						locationsearch(location_list,more_itertools.peekable(reddit_tags[title_split+1:]))
					#Priorité tertiaire: commentaire(s) du redditor qui a posté la photo
					for comment in post.comments.list(): #Liste du parcours en largeur de l'arborescence de commentaires
						location = ''
						if isinstance(comment,praw.models.MoreComments): #On ignore les objets MoreComments
							continue
						if comment.is_submitter:
							comment_tags = treetaggerwrapper.make_tags(reddit_tagger.tag_text(comment.body),
										   exclude_nottags=True)
							locationsearch(location_list,more_itertools.peekable(comment_tags))
					print('Lieux trouvés:',end='')
					pprint.pprint(location_list)
					print('')

					#GeoNames
					if location_list:
						dic_mongo = {}
						dic_mongo['link'] = post.permalink
						dic_mongo['img_url'] = post.url #Lien direct vers la photo
						dic_mongo['search_version'] = rgnversion
						dic_mongo['country'] = country
						dic_mongo['title'] = res.group(1).strip()
						dic_mongo['tag_list'] = reddit_tags
						dic_mongo['location_list'] = location_list
						dic_tmp = {} #Initialisé en dehors de la fonction pour pouvoir comparer après l'appel
						dic_tmp['img'] = post.url
						dic_tmp['search_version'] = rgnversion
						for loc in location_list:
							if geonames_query(loc,country_code,dic_results,dic_tmp,dic_mongo,exact=True):
								break
						#Pas de match exact après avoir parcouru toute la liste: on prend le premier résultat
						if 'name' not in dic_tmp:
							for loc in location_list:
								if geonames_query(loc,country_code,dic_results,dic_tmp,dic_mongo):
									break
						#Pas de résultat: on passe à une fuzzy search
						if 'name' not in dic_tmp:
							for loc in location_list:
								if geonames_query(loc,country_code,dic_results,dic_tmp,dic_mongo,fuzzy=True):
									break
						if 'location' in dic_mongo:
							dic_tostore = copy.deepcopy(dic_mongo)
							database_list.append(dic_tostore)
						print('\n###############')
					else:
						print('')
	#Chargement dans la base de données
	documents = mongo.MongoSave(database_list)
	documents.storeindb('Resultats_RGN',img_url='A',search_version='D')
	return jsonify(dic_results)	#Renvoyer directement un objet JSON


@app.route('/expert_init',methods=['GET','POST'])
def expert_init():
	experts = mongo.MongoSave([])
	if not experts.mongocheck('Resultats_Tests'):
		db_list = [{
						'user_id': 'NDebart',
						'code': 1,
						'num_answers': 0
				   }
				   {
				   		'user_id': 'SDjebrouni',
				   		'code': 2,
				   		'num_answers': 0
				   }
				   {
				   		'user_id': 'TFau',
				   		'code': 4,
				   		'num_answers': 0
				   }
				   {
				   		'user_id': 'MMashra',
				   		'code': 8,
				   		'num_answers': 0
				   }]
		experts.reinit(db_list)
		experts.storeindb('Resultats_Tests',user_id='A')


@app.route('/get_badresults',methods=['GET','POST'])
def get_badresults():
	dbfinder = mongo.MongoLoad({'search_version': '1.00', 'test_result': 'NOT_OK'},
						   	   {'search_version': 1, 'country': 1, 'title': 1, 'location_list': 1,
							  	'name': 1, 'location': 1, '_id': 0})
	doc_list = dbfinder.retrieve('Resultats_RGN',limit=5)
	return json.dumps(doc_list)


if __name__ == '__main__' :
	app.run(debug=True,port=5000)
