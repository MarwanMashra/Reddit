#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import copy, json, mongo, more_itertools, os, pprint, praw, re, requests,treetaggerwrapper
from flask import Flask, render_template, request, jsonify


'''Feature classes ('fcl')
	A   Administrative divisions
	H   Surface waters
	L   Parks/reserves
	P   Populated places
	R   Roads
	S   Structures
	T   Mountains/Islands
	U   Undersea
	V   Woodlands
'''

def dicLoad(res_dic, dic_mongo, location) :
	dic_mongo['name']=res_dic['name']
	dic_mongo['lng']=res_dic['lng']
	dic_mongo['lat']=res_dic['lat']
	dic_mongo['featureclass']=res_dic['fcl']
	dic_mongo['location']=location


def GeoNamesQuery(location, code_pays, dic_results, dic_tmp, dic_mongo, img_url, fuzzy=False) :
	url='http://api.geonames.org/searchJSON'
	data='?q='+location+'&country='+code_pays+'&username=scrapelord'
	if fuzzy:
		data+='&fuzzy=0.8' #Recherche fuzzy<1
	search_res=requests.get(url+data,auth=('scrapelord','Blorp86'))
	#print('Status code de la requête GeoNames:',search_res.status_code,'\n') #200:OK, 401:non autorisé
	search_res=search_res.json() #Décodeur JSON appliqué à l'objet Response renvoyé par la requête
	if search_res['totalResultsCount'] != 0:
		dic_results['head']['total']+=1
		print_res='' #Pour affichage test
		prio_list=[]
		for res in search_res['geonames']: #Recherche d'un match exact
			if res['name'].lower() == location.lower():
				if res['fcl'] in ['A','P','R','S'] and not prio_list:
					prio_list.append(res)
				elif res['fcl'] in ['H','L','T','U','V']:
					prio_list.insert(0,res)
					break
		if prio_list:
			dic_tmp['name']=prio_list[0]['name']
			dic_tmp['lng']=prio_list[0]['lng']
			dic_tmp['lat']=prio_list[0]['lat']
			dicLoad(prio_list[0],dic_mongo,location)
			print_res=prio_list[0]['name']
		else: #Sinon premier résultat
			dic_tmp['name']=search_res['geonames'][0]['name']
			dic_tmp['lng']=search_res['geonames'][0]['lng']
			dic_tmp['lat']=search_res['geonames'][0]['lat']
			dicLoad(search_res['geonames'][0],dic_mongo,location)
		dic_tmp['img']=img_url	#Lien direct vers la photo
		dic_results['results'].append(dic_tmp)
		print('Premier résultat Geonames: ',search_res['geonames'][0]['name'])
		print('Meilleur résultat Geonames: ',print_res)
		return True
	else:
		return False


def IterTagList(location_list, p_iter) :
	location=''
	for word,pos,lemma in p_iter:
		if pos == 'NP' or  pos == 'NP0' and word[0].isalpha(): #Nom propre 'NP' pour Windows et 'NP0' pour Linux
			location+=word+' '
			if p_iter.peek(('end','end','end'))[1] != 'NP' and \
			p_iter.peek(('end','end','end'))[1] != 'NP0': #Tuple par défaut passé à peek, retourné en fin d'itération
				location_list.append(location.rstrip())
				location=''



app= Flask(__name__)

@app.route('/')
@app.route('/map')
@app.route('/map.html')
def home():
	return render_template('map.html')

@app.route('/scraping',methods=['GET','POST'])
def scraping(): #La fonction appelée par la requête Javascript
	#Configuration du scraper, ne pas modifier
	reddit=praw.Reddit(client_id='v7xiCUUDI3vEmg',client_secret='5Q6FHHJT-SW0YRnEmtWkekWsxHU',
	password='Blorp86',user_agent='PhotoScraper',username='scrapelord')

	#Configuration recherche reddit
	rgnversion='1.00'
	target_sub=reddit.subreddit('EarthPorn') #Subreddit cible
	#Paramètres de la requête Javascript
	country=request.args.get('country')
	country_code=request.args.get('country_code')
	query='title:'+country
	print('\033[92m'+target_sub.display_name+'\033[0m','\nRésultats de recherche pour les soumissions reddit avec: ',query,'\n')

	#Configuration TreeTagger
	reddit_tagger=treetaggerwrapper.TreeTagger(TAGLANG='en',TAGDIR=os.getcwd()+'/TreeTagger')
	#Se placer dans un dossier pour que le chemin TAGDIR fonctionne

	#Résultats de la recherche dans le subreddit
	test_posts=target_sub.search(query,limit=25)
	dic_results={}	#Dico stockant tous les résultats de recherche (results) et les informations nécessaires (head)
	dic_results['head']={}
	dic_results['head']['total']=0
	dic_results['head']['country']={}	#Pour la génération de la carte (lat,lng)
	dic_results['head']['country']['name']=country

	#Coordonnées pays
	search_res=requests.get('http://api.geonames.org/searchJSON?q='+country+'&username=scrapelord',auth=('scrapelord','Blorp86'))
	search_res=search_res.json()
	dic_results['head']['country']['lng']=search_res['geonames'][0]['lng']
	dic_results['head']['country']['lat']=search_res['geonames'][0]['lat'] 
	dic_results['results']=[]

	#Objets 'submission' renvoyés par la recherche
	for post in test_posts:
		if re.search('.*'+country+'[.,/[( ]',post.title): #Pays suivi de '.' ',' '/' '[' '(' ou ' '
			#Match tous les caractères depuis le début de la ligne sauf [OC] et s'arrête au premier [ ou (
			res=re.search('^(?:\[OC\])?([^[(]+)',post.title)
			if (res):
				print(res.group(1))

				#Tagging
				reddit_tags=treetaggerwrapper.make_tags(reddit_tagger.tag_text(res.group(1)),exclude_nottags=True)
				#Liste de triplets: (word=..., pos=..., lemma=...) Peut être créer une classe pour la manipulation de cette liste
				pprint.pprint(reddit_tags)

				#Recherche des lieux potentiels
				if (country.lower() in (t[2].lower() for t in reddit_tags)):  #Garantir la présence du mot 'NomDuPays'
					title_split=[t[2].lower() for t in reddit_tags].index(country.lower()) #Position du mot 'NomDuPays'
					location_list=[]
					#Recherche prioritaire du lieu: la liste jusqu'au mot 'NomDuPays'
					IterTagList(location_list,more_itertools.peekable(reddit_tags[:title_split])) #Permet de regarder l'élément suivant de la liste
					#location_list.reverse() #Les noms propres les plus proches de 'NomDuPays' sont prioritaires
					#Priorité secondaire: la liste à la suite du mot 'NomDuPays'
					if len(reddit_tags) > title_split+1:
						IterTagList(location_list,more_itertools.peekable(reddit_tags[title_split+1:]))
					#Priorité tertiaire: commentaire(s) du redditor qui a posté la photo
					for comment in post.comments.list(): #Liste du parcours en largeur de l'arborescence de commentaires
						location=''
						if isinstance(comment,praw.models.MoreComments): #On ignore les objets MoreComments
							continue
						if comment.is_submitter:
							comment_tags=treetaggerwrapper.make_tags(reddit_tagger.tag_text(comment.body),exclude_nottags=True)
							IterTagList(location_list,more_itertools.peekable(comment_tags))
					print('Lieux trouvés:',end='')
					pprint.pprint(location_list)
					print('')

					#GeoNames
					if location_list:
						dic_mongo={}
						dic_mongo['img_url']=post.url
						dic_mongo['search_version']=rgnversion
						dic_mongo['title']=res.group(1).strip()
						dic_mongo['taglist']=reddit_tags
						dic_mongo['location_list']=location_list
						for loc in location_list:
							dic_tmp={} #Initialisé en dehors de la fonction GeoNamesQuery pour pouvoir comparer après l'appel
							if GeoNamesQuery(loc,country_code,dic_results,dic_tmp,dic_mongo,post.url):
								break
						'''Pas de résultat après avoir parcouru toute la liste: on passe à une fuzzy search pour prendre en compte
						les potentielles erreurs d'orthographe'''
						if not dic_tmp:
							for loc in location_list:
								dic_tmp={}
								if GeoNamesQuery(loc,country_code,dic_results,dic_tmp,dic_mongo,post.url,fuzzy=True):
									break
						#Chargement dans la base de données
						if 'location' in dic_mongo:
							dic_tostore=copy.deepcopy(dic_mongo)
							document=mongo.MongoSave(dic_tostore)
							document.storeindb('Resultats_RGN')
						print('\n###############')
					else:
						print('')

	return jsonify(dic_results)	#Renvoyer directement un objet JSON

if __name__ == '__main__' :
	app.run(debug=True,port=5000)
