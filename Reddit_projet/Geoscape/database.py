#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json, random
import Geoscape.mongo as mongo
import Geoscape.process as proc
from flask import Blueprint, jsonify, request, session
from math import floor, log2

mdb = Blueprint('mdb',__name__)



@mdb.route('/get_list_version',methods=['GET'])
def get_list_version():
	"""Crée la collection de stockage des versions du scraper si elle n'existe pas.
	Récupère les résultats de tests finaux et les traite pour générer de nouvelles
	règles. Une nouvelle version du scraper est alors créée pour utiliser ces règles. 
	Toutes les versions sont envoyées à la page de lancement du scrape et sont
	proposées à l'utilisateur.
	"""

	dbfinder = mongo.MongoLoad(proj={'search_version': 1, '_id': 0})

	if not dbfinder.mongocheck('Versions_Scrape'):
		version_doc = mongo.MongoSave([{'search_version': '1.00', 'submissions_scraped': 0,
									   'accuracy': 0}])
		version_doc.storeindb('Versions_Scrape',search_version='D')

	proc.create_rule()
 
	version_list = []
	for doc in dbfinder.retrieve('Versions_Scrape'):
		version_list.append(doc['search_version'])

	return jsonify(version_list)



@mdb.route('/report',methods=['POST'])
def report():
	"""Déclenchée par le signalement d'une image mal affichée sur la carte (mauvais
	lieu choisi). L'information est rajoutée au document dans la base de données, ce
	qui le rend disponible pour le test avancé.
	Sélection aléatoire de 3 testeurs à partir de la collection 'Testeurs', et stockage
	de leurs codes comme champ du document signalé.
	Ce champ 'testers' est de type BSON BinData: une chaîne en base 64 représentant un
	champ de bits de taille quelconque, ce qui permet de stocker des valeurs supérieures
	à 2^63-1.
	Le module pymongo convertit automatiquement un objet de type bytes en BinData.
	"""

	#La méthode POST renvoie des bytes: convertir en string JSON puis en dico python
	response = json.loads(request.data.decode('utf-8'))

	dbfinder = mongo.MongoLoad({'search_version': response['search_version'],
								'img_url': response['img_url'], 'test_result': 'NOT_OK'},
							   {'img_url': 1, '_id': 0})

	try:
		next(dbfinder.retrieve('Resultats_RGN'))
	except StopIteration: #L'image n'a pas été signalée auparavant
		update = mongo.MongoUpd({'img_url': response['img_url'],
								 'search_version': response['search_version']},
								{'$set': {'test_result': 'NOT_OK'}})
		update.singleval_upd('Resultats_RGN')

		dbfinder.reinit(proj={'code': 1, '_id': 0})
		tester_list = list(dbfinder.retrieve('Testeurs'))
		random.seed()
		tester_sum = sum(2**t['code'] for t in random.sample(tester_list,3)) #Sélection aléatoire dans la liste
		bytesize = floor(log2(tester_sum)/8 if tester_sum else 0) + 1 #log2(0) non défini
		tester_sum = tester_sum.to_bytes(bytesize,byteorder='big')
		
		update.reinit(update={'$set': {'testers': tester_sum}})
		update.singleval_upd('Resultats_RGN')

	return jsonify(status='OK')



@mdb.route('/get_count',methods=['GET'])
def get_count():
	"""Renvoie le nombre total de documents que le testeur en session doit tester, et
	les versions du scraper disponibles.
	"""

	dbcounter = mongo.MongoLoad({'user_id': session['username']},
								{'code': 1, '_id': 0})
	test_code = next(dbcounter.retrieve('Testeurs'))['code']
	doc_number = dbcounter.mongocount('Resultats_RGN',{'testers': {'$bitsAllSet': 2**test_code}})

	dbcounter.reinit(proj={'search_version': 1, '_id': 0})
	version_list = []
	for doc in dbcounter.retrieve('Versions_Scrape'):
		version_list.append(doc['search_version'])

	return jsonify(nbtest=doc_number,pseudo=session['username'],versions=version_list)



@mdb.route('/get_results',methods=['GET'])
def get_results():
	"""Extraction de documents à tester de la collection 'Résultats_RGN' (résultats du
	scraping) de la base de données, en fonction du testeur qui a lancé la requête, et
	renvoie en format JSON des résultats à la page de tests.
	"""

	result_value = request.args.get('value')
	version = request.args.get('version')
	limit = int(request.args.get('limit'))

	dbfinder = mongo.MongoLoad({'user_id': session['username']},
							   {'code': 1, '_id': 0})
	test_code = next(dbfinder.retrieve('Testeurs'))['code']

	dbfinder.reinit({'search_version': version, 'test_result': result_value,
					 'testers': {'$bitsAllSet': 2**test_code}}, #Opérateur binaire
					{'search_version': 1, 'img_url': 1, 'tag_list': 1,
					 'location_list': 1, 'location': 1, 'name': 1, '_id': 0})
	doc_list = list(dbfinder.retrieve('Resultats_RGN',limit=limit))

	return jsonify(results=doc_list)



@mdb.route('/send_results',methods=['POST'])
def send_results():
	"""Réception des résultats du test-expert et stockage dans la base de données;
	décrémentation de la champ 'testers' des documents qui viennent d'être testés
	de la collection 'Resultats_RGN', et incrémentation du champ 'num_answers' du
	testeur dans la collection 'Testeurs'.
	Si tous les tests sur un document ont été réalisés, lance la sélection des
	résultats finaux à partir des choix des testeurs, puis stocke ce résultat final
	dans la collection 'Resultats_Final_Expert_1'.
	"""

	response = json.loads(request.data.decode('utf-8'))
	tester = session['username']
	version = response['search_version']
	test_results = response['results']
	url_list = response['img_url']

	result_docs = []
	for url, test_item in zip(url_list,test_results):
		if test_item['lieux_choisis']: #Si la liste est vide, le testeur n'a pas su répondre
			result_docs.append({'tester': tester, 'search_version': version, 'img_url': url,
								'locations_selected': test_item['lieux_choisis'],
								'sufficient': test_item['suffisant']})

	documents = mongo.MongoSave(result_docs)
	documents.storeindb('Resultats_Test_Expert_1',tester='A',img_url='A',search_version='D')

	update = mongo.MongoUpd({'user_id': tester},{'$inc': {'num_answers': 1}})
	update.singleval_upd('Testeurs')

	dbfinder = mongo.MongoLoad({'user_id': tester},{'code': 1, '_id': 0})
	test_code = next(dbfinder.retrieve('Testeurs'))['code']

	dbfinder.reinit({'img_url': {'$in': url_list}, 'search_version': version},
					{'testers': 1, '_id': 0})
	sum_list = []
	done_list = []
	for url, doc in zip(url_list,dbfinder.retrieve('Resultats_RGN')):
		tester_sum = int.from_bytes(doc['testers'],byteorder='big') #classmethod, appelée sans instance
		tester_sum &= (~ (1<<test_code))

		if tester_sum == 0:
			done_list.append(url)
			bytesize = 1
		else:
			bytesize = floor(log2(tester_sum)/8) + 1
		tester_sum = tester_sum.to_bytes(bytesize,byteorder='big')
		sum_list.append(tester_sum)

	update.reinit({'img_url': '', 'search_version': version},
				  {'$set': {'testers': ''}},
				  url_list,sum_list)
	update.multval_upd('Resultats_RGN','img_url')

	if done_list:
		final_list = proc.select_results(version,done_list)
		documents.reinit(final_list)
		documents.nonunique_index('Resultats_Final_Expert_1',processed='A')
		documents.storeindb('Resultats_Final_Expert_1',img_url='A',search_version='D')

	return jsonify(status='OK')
