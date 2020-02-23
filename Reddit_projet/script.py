#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json, more_itertools, os, pprint, praw, re, requests,treetaggerwrapper
from flask import Flask, render_template, request, jsonify

def GeoNamesQuery(location, code_pays, dic_results, dic_tmp,img_url, fuzzy=False) :
	url="http://api.geonames.org/searchJSON"
	#Ici, FR est fixé: il y aura une variable code pays passé à la requête donc il faudra pouvoir trouver le code pays ISO 3166-1 alpha-2
	data="?q="+location+"&country="+code_pays+"&username=scrapelord"
	if fuzzy:
		data+="&fuzzy=0.8" #Recherche fuzzy<1
	search_res=requests.get(url+data,auth=("scrapelord","Blorp86"))
	#print("Status code de la requête GeoNames:",search_res.status_code,"\n") #200:OK, 401:non autorisé
	search_res=search_res.json() #Décodeur JSON appliqué à l'objet Response renvoyé par la requête
	if search_res['totalResultsCount'] != 0:
		dic_results['head']['total']+=1
		print_res="" #Pour affichage test
		for res in search_res['geonames']: #Recherche d'un match exact
			if res['toponymName'] == location:
				dic_tmp['lng']=res['lng']	#Longitude
				dic_tmp['lat']=res['lat']	#Latitude
				print_res=res['toponymName']
				break
		if not dic_tmp: #Sinon premier résultat
			dic_tmp['lng']=search_res['geonames'][0]['lng']	#Longitude
			dic_tmp['lat']=search_res['geonames'][0]['lat']	#Latitude
		dic_tmp['img']=img_url	#Lien direct vers la photo
		dic_results['results'].append(dic_tmp)
		print("Premier résultat Geonames: ",search_res["geonames"][0]["toponymName"])
		print("Meilleur résultat Geonames: ",print_res)
		print("\n###############")
		return True
	else:
		return False


def IterTagList(location_list, p_iter) :
	location=""
	for word,pos,lemma in p_iter:
		if pos == "NP" or  pos == "NP0": #Nom propre #'NP' pour Windows et 'NP0' pour Linux
			location+=word+" "
			if p_iter.peek(("end","end","end"))[1] != "NP" and p_iter.peek(("end","end","end"))[1] != "NP0": #Tuple par défaut passé à peek, retourné en fin d'itération
				location_list.append(location.rstrip()) #Enlève le whitespace potentiel en fin de chaîne
				location=""



app= Flask(__name__)

@app.route('/')
@app.route('/map')
@app.route('/map.html')
def home():
	return render_template('map.html')

@app.route('/scraping',methods=['GET','POST'])
def scraping():          #la fonction qui sera appeler par le JavaScript
	#Configuration du scraper, ne pas modifier
	reddit=praw.Reddit(client_id="v7xiCUUDI3vEmg",client_secret="5Q6FHHJT-SW0YRnEmtWkekWsxHU",
	password="Blorp86",user_agent="PhotoScraper",username="scrapelord")

	#Configuration recherche reddit
	target_sub=reddit.subreddit("EarthPorn") #Subreddit cible
	#récuperer les paramètres envoyés par la JavaScript
	country=request.args.get('country')           #Pays cible
	country_code=request.args.get('country_code')
	query="title:"+country
	print("\033[92m"+target_sub.display_name+"\033[0m","\nRésultats de recherche pour les soumissions reddit avec: ",query,"\n")

	#Configuration TreeTagger
	reddit_tagger=treetaggerwrapper.TreeTagger(TAGLANG="en") #Se placer dans un dossier pour que le chemin TAGDIR fonctionne

	#Résultats de la recherche dans le subreddit
	test_posts=target_sub.search(query,limit=25)
	dic_results={}	#Dico stockant tous les résultats de recherche (results) et les informations nécessaires (head)
	dic_results['head']={}    #head con
	dic_results['head']['total']=0
	dic_results['head']['country']={}                     #pour la génération de la carte (lat,lng)
	dic_results['head']['country']['name']=country


	search_res=requests.get("http://api.geonames.org/searchJSON?q="+country+"&username=scrapelord",auth=("scrapelord","Blorp86"))
	search_res=search_res.json()
	dic_results['head']['country']['lng']=search_res['geonames'][0]['lng']
	dic_results['head']['country']['lat']=search_res['geonames'][0]['lat'] 
	dic_results['results']=[]
	for post in test_posts: #Objets 'submission'
		if re.search(".*"+country+"[.,/[( ]",post.title): #Pays suivi de '.' ',' '/' '[' '(' ou ' '
			res=re.search("^([^[(]+)",post.title) #Match tous les caractères depuis le début de la ligne, excluant [ et (
			if (res):
				print(res.group(1))

				#Tagging
				reddit_tags=treetaggerwrapper.make_tags(reddit_tagger.tag_text(res.group(1)),exclude_nottags=True)
				#Liste de triplets: (word=..., pos=..., lemma=...) Peut être créer une classe pour la manipulation de cette liste
				pprint.pprint(reddit_tags)

				#Recherche des lieux potentiels
				if (country.lower() in (t[2].lower() for t in reddit_tags)):  #pour éviter que le programme plante s'il trouve pas le nom de pays
					title_split=[t[2].lower() for t in reddit_tags].index(country.lower()) #Position du mot 'NomDuPays'
					location_list=[]
					#Recherche prioritaire du lieu: la liste jusqu'au mot 'NomDuPays'
					print(IterTagList(location_list,more_itertools.peekable(reddit_tags[:title_split])))
					IterTagList(location_list,more_itertools.peekable(reddit_tags[:title_split])) #Permet de regarder l'élément suivant de la liste
					location_list.reverse() #Les noms propres les plus proches de 'NomDuPays' sont prioritaires
					#Priorité secondaire: la liste à la suite du mot 'NomDuPays'
					if len(reddit_tags) > title_split+1:
						IterTagList(location_list,more_itertools.peekable(reddit_tags[title_split+1:]))
					#Priorité tertiaire: commentaire(s) du redditor qui a posté la photo
					for comment in post.comments.list(): #Liste du parcours en largeur de l'arborescence de commentaires
						location=""
						if isinstance(comment,praw.models.MoreComments): #On ignore les objets MoreComments (pour le moment?)
							continue
						if comment.is_submitter:
							comment_tags=treetaggerwrapper.make_tags(reddit_tagger.tag_text(comment.body),exclude_nottags=True)
							IterTagList(location_list,more_itertools.peekable(comment_tags))
					print("Lieux trouvés:",end="")
					pprint.pprint(location_list)
					print("")

					#GeoNames
					if location_list:
						for loc in location_list:
							dic_tmp={} #Initialisé en dehors de la fonction GeoNamesQuery pour pouvoir comparer après l'appel
							if GeoNamesQuery(loc,country_code,dic_results,dic_tmp,post.url):
								break
						"""Pas de résultat après avoir parcouru toute la liste: on passe à une fuzzy search pour prendre en compte
						les potentielles erreurs d'orthographe"""
						if not dic_tmp:
							for loc in location_list:
								dic_tmp={}
								if GeoNamesQuery(loc,country_code,dic_results,dic_tmp,post.url,fuzzy=True):
									break
					#A FAIRE
					#Utiliser FeatureClass pour distinguer les types de résultat GeoNames, et hiérarchiser
					else:
						print("")

	#Stockage du JSON dans un fichier
	"""if os.path.exists("GN_Results.json"):	#Pour mettre à jour le fichier à chaque exécution (temporaire)
		os.remove("GN_Results.json")
	with open("GN_Results.json", "a") as file:
		json.dump(dic_results,file)
	"""
	return jsonify(dic_results)                  #renvoyer un objet json

if __name__ == "__main__" :
	app.run(debug=True,port=5000)