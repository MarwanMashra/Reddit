#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json, os, pprint, praw, re, requests, treetaggerwrapper



def GeoNamesQuery(location,dic_results) :
	url="http://api.geonames.org/searchJSON"
	data="?q="+location+"&country=FR&username=scrapelord" #username inséré dans data
	search_res=requests.get(url+data,auth=("scrapelord","Blorp86"))
	#print(search_res.encoding) #UTF-8
	print("Status code de la requête GeoNames:",search_res.status_code,"\n") #200:OK, 401:non autorisé
	search_res=search_res.json() #Décodeur JSON appliqué à l'objet Response renvoyé par la requête
	if search_res['totalResultsCount'] != 0:
		dic_results['TotalResults']+=1
		dic_tmp={}
		dic_tmp['lng']=search_res['geonames'][0]['lng']	#Longitude
		dic_tmp['lat']=search_res['geonames'][0]['lat']	#Latitude
		dic_tmp['img']=post.url	#Lien direct vers la photo
		dic_results['Results'].append(dic_tmp)
		print("Premier résultat Geonames: ",search_res["geonames"][0]["toponymName"])
		pprint.pprint(dic_tmp)
		print("\n###############")
		return True
	else:
		return False



reddit=praw.Reddit(client_id="v7xiCUUDI3vEmg",client_secret="5Q6FHHJT-SW0YRnEmtWkekWsxHU",
password="Blorp86",user_agent="PhotoScraper",username="scrapelord")

#Configuration recherche reddit
target_sub=reddit.subreddit("EarthPorn") #Subreddit cible
country="France" #Pays cible
query="title:"+country
#print(target_sub.description)
print("\033[92m"+target_sub.display_name+"\033[0m"+"\nRésultats de recherche pour les soumissions reddit avec: "+query+"\n")

#Configuration TreeTagger
reddit_tagger=treetaggerwrapper.TreeTagger(TAGLANG="en",TAGDIR=os.getcwd()+"/TreeTagger")

#Résultats de la recherche dans le subreddit
test_posts=target_sub.search(query,limit=15)
dic_results={}	#Dico stockant tous les résultats de recherche
dic_results['TotalResults']=0
dic_results['Results']=[]
for post in test_posts: #Objets 'submission'
	if re.search(".*"+country+"[.,/[( ]",post.title): #Pays suivi de '.' ',' '/' '[' '(' ou ' '
		res=re.search("^([^[(]+)",post.title) #Match tous les caractères depuis le début de la ligne, excluant [ et (
		if res:
			print(res.group(1))

			#Tagging
			reddit_tags=treetaggerwrapper.make_tags(reddit_tagger.tag_text(res.group(1)))
			#Liste de triplets: (word=..., pos=..., lemma=...)
			pprint.pprint(reddit_tags)

			idx_upper_range=0
			while reddit_tags[idx_upper_range][2] not in [country, country.lower()]:
				idx_upper_range+=1
			#En sortie de boucle, idx_upper_range est l'indice du tuple taggant le mot 'NomDuPays'
			location=""
			#Recherche du lieu en partant du mot 'NomDuPays' et en remontant la liste de mots taggés
			for i in range(idx_upper_range-1,-1,-1):
				if reddit_tags[i][1] == "NP0": #Nom propre
					location=reddit_tags[i][0]+" "+location
					if i != 0 and reddit_tags[i-1][1] != "NP0":
						break
			#Si le lieu n'a pas été trouvé, on parcourt la liste à la suite du mot 'NomDuPays'
			if location == "":
				if len(reddit_tags) > idx_upper_range+1: #La liste contient au moins un élément après 'NomDuPays'
					for i in range(idx_upper_range+1,len(reddit_tags)):
						if reddit_tags[i][1] == "NP0":
							location+=reddit_tags[i][0]+" "
							if i != len(reddit_tags)-1 and reddit_tags[i+1][1] != "NP0":
								break
			#Si le lieu n'a toujours pas été trouvé, on explore les commentaires
			if location == "":
				all_comments=post.comments.list() #Liste du parcours en largeur de l'arborescence de commentaires
				for comment in all_comments:
					if isinstance(comment,praw.models.MoreComments): #On ignore les objets MoreComments (pour le moment?)
						continue
					comment_tags=treetaggerwrapper.make_tags(reddit_tagger.tag_text(comment.body))
					pprint.pprint(comment_tags)
					for i in range(0,len(comment_tags)):
						if comment_tags[i][0].isalpha() and comment_tags[i][1] == "NP0" and (i == len(comment_tags)-1 or comment_tags[i+1][0] != "?"):
							location+=comment_tags[i][0]+" "
							if i != len(comment_tags)-1 and comment_tags[i+1][1] != "NP0":
								break
						#Si le nom propre est suivi d'un '?', on cherche la réponse
						if i != len(comment_tags)-1 and comment_tags[i+1][0] == "?":
							for reply in all_comments:
								if reply.parent_id == comment.id:
									reply_tags=treetaggerwrapper.make_tags(reddit_tagger.tag_text(reply.body))
									for j in range(0,len(reply_tags)):
										if reply_tags[j][0] in ["yes", "Yes", "yeah", "Yeah"]:
											location+=comment_tags[i][0]
											break
						if location != "":
							break
			print("Lieu trouvé: ",location)

			#GeoNames
			if location != "":
				GeoNamesQuery(location,dic_results)
			else:
				print("")

#Stockage du JSON dans un fichier
if os.path.exists("GN_Results.json"):	#Pour mettre à jour le fichier à chaque exécution (temporaire)
	os.remove("GN_Results.json")
with open("GN_Results.json", "a") as file:
	json.dump(dic_results,file)
