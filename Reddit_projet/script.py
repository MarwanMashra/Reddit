#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import copy, json, mongo, more_itertools, os, pprint, praw, re, requests, sys, treetaggerwrapper, time, bcrypt, urllib
from flask import Flask, render_template, request, jsonify, redirect, session, url_for

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


"""A partir de l'inscription d'un utilisateur en tant qu'admin, la fonction crée
un profil testeur pour cet utilisateur dans la collection 'Testeurs' de la base
de données. Chaque testeur reçoit un code unique qui sert à identifier les documents
de 'Resultats_RGN' qu'il/elle doit tester.
"""
def db_tester(username):
	dbloader = mongo.MongoSave([])
	next_code = 0
	if dbloader.mongocheck('Testeurs'):
		next_code = dbloader.mongocount('Testeurs')
	dbloader.reinit([{'user_id': username, 'code': next_code, 'num_answers': 0}])
	dbloader.storeindb('Testeurs',user_id='A')
	print('Profil testeur créé.')



app = Flask(__name__)
app.secret_key='mysecret'

@app.route('/')
@app.route('/map')
@app.route('/map.html')
def map():
	if 'username' in session:
		return render_template('map.html',username=session['username'])
	return render_template('map.html')



@app.route('/connexion',methods=['GET','POST'])
@app.route('/connexion.html',methods=['GET','POST'])
def connexion():
	if request.method == 'POST':
		pseudo_email = request.form['pseudo_email']
		password = request.form['password']
		
		#Chercher le compte en supposant que c'est le pseudo
		compte = mongo.MongoLoad({'pseudo': pseudo_email}).retrieve('users_accounts',limit=1)

		#Si compte pas trouvé, chercher le compte en supposant que c'est le mail
		if not compte:
			compte = mongo.MongoLoad({'email': pseudo_email}).retrieve('users_accounts',limit=1)

		#Si compte trouvé	
		if compte:
			compte = compte[0]
			#Vérifier le mot de passe checkpw(password, hashed)
			if bcrypt.hashpw(password.encode('utf-8'),compte['password']) == compte['password']:

				#Cookies
				session['username'] = compte['pseudo']
				session['admin?'] = ( compte['admin?'] == "YES" )
				if (session['admin?']):
					return redirect(url_for('testeur'))  
				else:
					return redirect(url_for('map'))
					
		#Pseudo,email ou mot de passe invalide
		error = 'Le pseudo/email ou le mot de passe n\'est pas valide'
		return render_template('connexion.html',error=error)
			
	elif 'username' in session:
		if session['admin?']:
			return redirect(url_for('testeur'))  
		else:
			return redirect(url_for('map'))

	else:
		return render_template('connexion.html')




@app.route('/inscription.html',methods=['GET','POST'])
@app.route('/inscription',methods=['GET','POST'])
def inscription():	
	if request.method == 'POST':
		pseudo = request.form['pseudo']
		email = request.form['email']
		password = request.form['password']
		password_confirmation = request.form['password_confirmation']
		is_admin = ('admin' in request.form)

		existing_name = mongo.MongoLoad({'pseudo': pseudo}).retrieve('users_accounts',limit=1)
		existing_mail = mongo.MongoLoad({'email': email}).retrieve('users_accounts',limit=1)

		if existing_name:
			error = 'Ce pseudo est déjà utilisé, veuillez en choisir un autre.'
		elif existing_mail:
			error = 'Cette adresse mail est déjà utilisée, veuillez vous-connectez.'
		elif password != password_confirmation:
			error = 'Les deux mots de passes sont différents.'

		else:
			#Cookies
			session['username'] = pseudo
			session['admin?'] = is_admin   

			#Cryptage du mot de passe
			hashpass= bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
			
			#Stockage dans mongoDB
			dic = {
					'pseudo': pseudo,
					'email': email,
					'password': hashpass
				  }
			if session['admin?']:
				dic['admin?'] = 'YES'
				db_tester(session['username']) #Création d'un profil testeur
			else:
				dic['admin?'] = 'NO'
			documents = mongo.MongoSave([dic])
			documents.storeindb('users_accounts',pseudo='A',email='A')

			if (session['admin?']):
				#Appel de la fonction qui crée le compte admin
				return redirect(url_for('testeur')) 
			else:
				return redirect(url_for('map'))  

		return render_template('inscription.html',error=error)

	elif 'username' in session:
		if session['admin?']:
			return redirect(url_for('testeur'))  
		else:
			return redirect(url_for('map'))

	else:
		return render_template('inscription.html')


@app.route('/deconnexion')
def deconnexion():
	session.clear()
	return redirect(url_for('connexion'))		

		


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

	#Coordonnées pays
	search_res = requests.get('http://api.geonames.org/searchJSON?q='+country+'&username=scrapelord',
				 auth=('scrapelord','Blorp86'))
	search_res = search_res.json()
	#Dico stockant tous les résultats de recherche (results) + informations générales (head)
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
				location_list = []
				if country.lower() in [t[2].lower() for t in reddit_tags]:  #Si le mot 'NomDuPays' est présent
					title_split = [t[2].lower() for t in reddit_tags].index(country.lower())
					#Recherche prioritaire du lieu: la liste jusqu'au mot 'NomDuPays'
					locationsearch(location_list,more_itertools.peekable(reddit_tags[:title_split]))
					#Priorité secondaire: la liste à la suite du mot 'NomDuPays'
					if len(reddit_tags) > title_split+1:
						locationsearch(location_list,more_itertools.peekable(reddit_tags[title_split+1:]))
				else:
					locationsearch(location_list,more_itertools.peekable(reddit_tags))
				#Priorité tertiaire: commentaire(s) du redditor qui a posté la photo
				"""
				for comment in post.comments.list(): #Liste du parcours en largeur de l'arborescence de commentaires
					if isinstance(comment,praw.models.MoreComments): #On ignore les objets MoreComments
						continue
					if comment.is_submitter:
						comment_tags = treetaggerwrapper.make_tags(reddit_tagger.tag_text(comment.body),
									   exclude_nottags=True)
						locationsearch(location_list,more_itertools.peekable(comment_tags))
				"""
				print('Lieux trouvés:',end='')
				pprint.pprint(location_list)
				print('')

				#GeoNames
				if location_list:
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
								'text':post.title,
								'search_version': rgnversion,
								'url': 'https://www.reddit.com'+post.permalink, #Passer l'url du post
								#Stocker la date
								'date': {
											'year': date.tm_year,
											'month': date.tm_mon,
											'day': date.tm_mday,
											'hour': date.tm_hour,
											'min': date.tm_min,
											'sec': date.tm_sec
										},
								#Stocker l'auteur
								'author': {
											'name': post.author.name,
											'icon': post.author.icon_img,
											'profile': 'https://www.reddit.com/user/'+post.author.name
										  }
							  }

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



@app.route('/test')
@app.route('/test.html')
def test():
	return render_template('test-expert.html')


@app.route('/testeur')
@app.route('/testeur.html')
def testeur():
	if ('admin?' in session) and (session['admin?']) :
		return render_template('testeur.html')
	return redirect(url_for('connexion'))

"""Renvoit le nombre total de documents que le testeur en session doit tester.
"""
@app.route('/get_count',methods=['GET'])
def get_count():
	dbcounter = mongo.MongoLoad({'user_id': session['username']},
								{'code': 1, '_id': 0})
	test_code = dbcounter.retrieve('Testeurs',limit=1)[0]['code']
	doc_number = dbcounter.mongocount('Resultats_RGN',{'testers': {'$bitsAllSet': 2**test_code}})
	return jsonify(nbtest=doc_number,pseudo=session['username'])

"""Extraction de documents à tester de la collection 'Résultats_RGN' (résultats du scraping)
de la base de données, en fonction du testeur qui a lancé la requête, et renvoie en format
JSON des résultats à la page de tests.
"""
@app.route('/get_results',methods=['GET'])
def get_results():
	result_value = request.args.get('value')
	version = request.args.get('version')
	limit = int(request.args.get('limit'))
	tester = session['username']
	dbfinder = mongo.MongoLoad({'user_id': tester},
							   {'code': 1, '_id': 0})
	test_code = dbfinder.retrieve('Testeurs',limit=1)[0]['code']
	dbfinder.reinit({'search_version': version, 'test_result': result_value,
					 'testers': {'$bitsAllSet': 2**test_code}}, #Opérateur binaire
					{'search_version': 1, 'img_url': 1, 'tag_list': 1, 'location_list': 1,
					 'location': 1, 'name': 1, '_id': 0})
	doc_list = dbfinder.retrieve('Resultats_RGN',limit=limit)
	return jsonify({'results': doc_list})


"""Réception des résultats du test-expert et stockage dans la base de données;
décrémentation de la champ 'testers' des documents qui viennent d'être testés
de la collection 'Resultats_RGN', et incrémentation du champ 'num_answers' du
testeur dans la collection 'Testeurs'.
"""
@app.route('/send_results',methods=['POST'])
def send_results():
	#La méthode POST renvoie des bytes: convertir en string puis en JSON
	response = json.loads(request.data.decode('utf-8'))
	#pprint.pprint(response)
	tester = session['username']
	test_results = response['results']
	doc_results = list(zip(response['img_url'],test_results))
	for url, test_item in doc_results:
		new_document = {
							'tester': tester,
							'search_version': response['search_version'],
							'img_url': url,
							'locations_selected': test_item['lieux_choisis'],
							'sufficient': test_item['suffisant']
					}
	documents = mongo.MongoSave(new_document)
	documents.storeindb('Resultats_Test_Expert_1',img_url='A',search_version='D')
	update = mongo.MongoUpd({
								'update': 'num_answers',
								'newvalue': 1,
								'id_field': {'name': 'user_id','values': [tester]}
							})
	update.updatedb('Testeurs','$inc')
	dbfinder = mongo.MongoLoad({'user_id': tester},
							   {'code': 1, '_id': 0})
	test_code = dbfinder.retrieve('Testeurs',limit=1)[0]['code']
	version = response['results'][0]['search_version']
	url_list = []
	for dic in response['results']:
		url_list.append(dic['img_url'])
	update.reinit({
					'update': 'testers',
					'newvalue': (-1)*(2**test_code),
					'id_field': {'name': 'img_url', 'values': url_list},
					'other_field': {'name': 'search_version', 'value': version} 
				 })
	update.updatedb('Resultats_RGN','$inc')
	return jsonify(status='OK')




if __name__ == '__main__' :
	app.run(debug=True,port=5000)
