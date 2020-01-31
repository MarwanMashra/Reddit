#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json, os, praw, re, requests

reddit=praw.Reddit(client_id="v7xiCUUDI3vEmg",client_secret="5Q6FHHJT-SW0YRnEmtWkekWsxHU",
password="Blorp86",user_agent="PhotoScraper",username="scrapelord")

target_sub=reddit.subreddit("EarthPorn") #Subreddit cible
country="France" #Pays cible
query="title:"+country
#print(target_sub.description)
print("\033[92m"+target_sub.display_name+"\033[0m"+"\nRésultats de recherche pour les soumissions reddit avec: "+query+"\n")

#Création du dossier contenant les fichiers .json stockant les résultats de recherche GeoNames
if not os.path.exists("GNSearch_Results"):
	os.mkdir("GNSearch_Results")

#Résultats de la recherche dans le subreddit
test_posts=target_sub.search(query,limit=15)
for post in test_posts:
	if re.search(".*"+country+"[.,/[( ]",post.title): #Pays suivi de '.' ',' '/' '[' '(' ou ' '
		res=re.search("^([^[(]+)",post.title) #Match tous les caractères depuis le début de la ligne, excluant [ et (
		if res:
			print(res.group(1))
			print(post.url) #Lien direct vers la photo!
			loc=re.search("(\S+)[, ]*"+country+"|(\S+) in "+country,res.group(1))
			if loc:
				if loc.group(1):
					location=loc.group(1)
				elif loc.group(2): #La deuxième option de la regex sera placée dans le group(2)
					location=loc.group(2)
				if location[-1] in (',','"'):
					location=location[:-1]
				print("Lieu identifié: "+location)

				#GeoNames
				url="http://api.geonames.org/searchJSON"
				data="?q="+location+"&country=FR&username=scrapelord" #username inséré dans data
				search_res=requests.get(url+data,auth=("scrapelord","Blorp86"))
				#print(search_res.encoding) #UTF-8
				print("Status code de la requête GeoNames:",search_res.status_code) #200:OK, 401:non autorisé
				search_res=search_res.json() #Décodeur JSON appliqué à l'objet Response renvoyé par la requête
				#Ecriture du contenu de l'objet dans un fichier dédié sous forme d'une string au format JSON
				with open("GNSearch_Results/GN_"+location+".json", "a") as file:
					file.write(str(json.dump(search_res,file,ensure_ascii=False)))

				#Affichage
				try:
					main_dict=search_res["geonames"][0] #Clé référençant une liste dont le premier élément est un dictionnaire
				except IndexError:
					print("\033[91mAucun résultat dans la base de données GeoNames.\033[0m\n")
				else:
					#Clés du dictionnaire interne
					print(main_dict["toponymName"],main_dict["lat"],main_dict["lng"],"\n") #Meilleur (premier) résultat, latitude et longitude