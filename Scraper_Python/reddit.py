#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import collections, copy, json, mongo, more_itertools, os, pprint, praw, re, requests, sys, treetaggerwrapper



"""Feature classes ("fcl")
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


def geonames_query(location, dic_results, dic_tmp, fuzzy=False):
	url = "http://api.geonames.org/searchJSON"
	#Ici, FR est fixé: il faudra insérer le code ISO 3166-1 alpha-2 du pays
	data = "?q="+location+"&country=FR&maxRows=200&username=scrapelord"
	if fuzzy:
		data += "&fuzzy=0.8"
	search_res = requests.get(url+data,auth=("scrapelord","Blorp86"))
	if search_res.status_code == 200:
		#Décodeur JSON appliqué à l'objet Response renvoyé par la requête
		search_res = search_res.json()
		if search_res['totalResultsCount'] != 0:
			dic_results['TotalResults'] += 1
			#Recherche des matchs exacts
			prio_que = collections.deque() #Meilleure complexité à l'insertion que list
			for res in search_res['geonames']:
				if res["name"].lower() == location.lower():
					if res["fcl"] in ["A","P","R","S"]:
						prio_que.append(res)
					else:
						prio_que.appendleft(res)
			if prio_que:
				dic_tmp["name"] = prio_que[0]["name"]
				dic_tmp["lng"] = prio_que[0]["lng"]
				dic_tmp["lat"] = prio_que[0]["lat"]
				dic_tmp["featureclass"] = prio_que[0]["fcl"]
			#Si pas de matchs exacts
			else:
				dic_tmp["name"] = search_res["geonames"][0]["name"]
				dic_tmp['lng'] = search_res['geonames'][0]['lng']
				dic_tmp['lat'] = search_res['geonames'][0]['lat']
				dic_tmp["featureclass"] = search_res["geonames"][0]["fcl"]
			dic_tmp["location"] = location
			dic_results['Results'].append(dic_tmp)
			print("Premier résultat Geonames: ",search_res["geonames"][0]["name"])
			print("Meilleur résultat Geonames: ",dic_tmp["name"]+"\t"+dic_tmp["featureclass"])
			return True
		else:
			return False
	else:
		sys.exit("Code HTTP "+search_res.status_code+": abandon de la recherche.")


##Le paramètre passé à peek est retourné en fin d'itération pour éviter une erreur
#rstrip() enlève le whitespace potentiel en fin de chaîne
def locationfinder(location_list, peekable_iter):
	location = ""
	for word,pos,lemma in peekable_iter:
		if pos == "NP0" and word[0].isalpha(): #Nom propre
			location += word+" "
			if peekable_iter.peek(("end","end","end"))[1] != "NP0":
				location_list.append(location.rstrip())
				location = ""



#Configuration du scraper, ne pas modifier
reddit=praw.Reddit(client_id="v7xiCUUDI3vEmg",client_secret="5Q6FHHJT-SW0YRnEmtWkekWsxHU",
password="Blorp86",user_agent="PhotoScraper",username="scrapelord")

#Configuration recherche reddit
rgnversion = sys.argv[1] #Initialement 1.00
target_sub = reddit.subreddit("EarthPorn")
country = "France"
query = "title:"+country
print("\033[92m"+target_sub.display_name+"\033[0m",
	"\nRésultats de recherche pour les soumissions reddit avec: ",query,"\n")

#Configuration TreeTagger
reddit_tagger = treetaggerwrapper.TreeTagger(TAGLANG="en",TAGDIR=os.getcwd()+"/TreeTagger")
#Se placer dans un dossier pour que le chemin TAGDIR fonctionne

#Résultats de la recherche dans le subreddit
test_posts = target_sub.search(query,limit=25)
dic_results = {}
dic_results['TotalResults'] = 0
dic_results['Results'] = []
for post in test_posts: #Objets 'submission'
	if re.search(".*"+country+"[.,/[( ]",post.title): #Pays suivi de '.' ',' '/' '[' '(' ou ' '
		#Match tous les caractères depuis le début de la ligne sauf [OC] et s'arrête au premier [ ou (
		res = re.search("^(?:\[OC\])?([^[(]+)",post.title)
		print(res.group(1))

		#Tagging
		reddit_tags = treetaggerwrapper.make_tags(reddit_tagger.tag_text(res.group(1)),exclude_nottags=True)
		#Liste de triplets: (word=..., pos=..., lemma=...)
		pprint.pprint(reddit_tags)

		#Recherche des lieux potentiels
		title_split = [t[2] for t in reddit_tags].index(country.lower()) #Position du mot 'NomDuPays'
		location_list = []
		#Recherche prioritaire du lieu: la liste jusqu'au mot 'NomDuPays'
		locationfinder(location_list,more_itertools.peekable(reddit_tags[:title_split]))
		#location_list.reverse()
		#Priorité secondaire: la liste à la suite du mot 'NomDuPays'
		if len(reddit_tags) > title_split+1:
			locationfinder(location_list,more_itertools.peekable(reddit_tags[title_split+1:]))
		#Priorité tertiaire: commentaire(s) du redditor qui a posté la photo
		for comment in post.comments.list(): #Liste du parcours en largeur de l'arborescence de commentaires
			location = ""
			if isinstance(comment,praw.models.MoreComments): #On ignore les objets MoreComments
				continue
			if comment.is_submitter:
				comment_tags = treetaggerwrapper.make_tags(reddit_tagger.tag_text(comment.body),exclude_nottags=True)
				locationfinder(location_list,more_itertools.peekable(comment_tags))
		print("Lieux trouvés:",end="")
		pprint.pprint(location_list)
		print("")

		#GeoNames
		if location_list:
			dic_tmp = {}
			dic_tmp["img_url"] = post.url
			dic_tmp["search_version"] = rgnversion
			dic_tmp["title"] = res.group(1).strip()
			dic_tmp["taglist"] = reddit_tags
			dic_tmp["location_list"] = location_list
			for loc in location_list:
				if geonames_query(loc,dic_results,dic_tmp):
					break
			"""Pas de résultat après avoir parcouru toute la liste: on passe à une fuzzy search pour
			prendre en compte les potentielles erreurs d'orthographe"""
			if "location" not in dic_tmp:
				for loc in location_list:
					if geonames_query(loc,dic_results,dic_tmp,fuzzy=True):
						break
			if "location" in dic_tmp:
				dic_tostore = copy.deepcopy(dic_tmp) #Pour ne pas passer dic_tmp lui-même à MongoSave
				document = mongo.MongoSave(dic_tostore)
				document.storeindb("Resultats_RGN")
			print("\n###############")
		else:
			print("")

#Stockage du JSON dans un fichier
if os.path.exists("GN_Results.json"):	#Pour mettre à jour le fichier à chaque exécution (temporaire)
	os.remove("GN_Results.json")
with open("GN_Results.json", "a") as file:
	json.dump(dic_results,file)
