#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json, random
import Geoscape.mongo as mongo
from flask import Blueprint, jsonify, request, session
from math import floor, log2
from functools import reduce

mdb = Blueprint('mdb',__name__)



"""Crée la collection de stockage des versions du scraper si elle n'existe pas.
Récupère ensuite toutes les versions et envoie la liste résultat à la page de
lancement du scrape.
"""
@mdb.route('/get_list_version',methods=['GET'])
def get_list_version():
	dbfinder = mongo.MongoLoad(proj={'search_version': 1, '_id': 0})

	if not dbfinder.mongocheck('Versions_Scrape'):
		version_doc = mongo.MongoSave([{'search_version': '1.00', 'submissions_scraped': 0,
									   'accuracy': 0}])
		version_doc.storeindb('Versions_Scrape',search_version='D')

	versions = dbfinder.retrieve('Versions_Scrape')
	version_list = []
	for doc in versions:
		version_list.append(doc['search_version'])

	return jsonify(version_list)



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
@mdb.route('/report',methods=['POST'])
def report():
	response = json.loads(request.data.decode('utf-8'))
	update = mongo.MongoUpd({
								'update': 'test_result',
								'newvalue': 'NOT_OK',
								'id_field': {'name': 'img_url', 'values': [response['img']]},
								'other_field': {'name': 'search_version',
								                'value': response['search_version']}
							})
	update.updatedb('Resultats_RGN','$set')

	dbfinder = mongo.MongoLoad(proj={'code': 1, '_id': 0})
	tester_list = dbfinder.retrieve('Testeurs')
	random.seed()
	testers = random.sample(tester_list,3)
	tester_sum = reduce(lambda x,y: x + 2**y['code'],testers,0)
	bytesize = floor(log2(tester_sum)/8) + 1
	tester_sum = tester_sum.to_bytes(bytesize,byteorder='big')
	
	update.reinit({
					'update': 'testers',
					'newvalue': tester_sum,
					'id_field': {'name': 'img_url', 'values': [response['img']]},
					'other_field': {'name': 'search_version', 'value': response['search_version']}
				  })
	update.updatedb('Resultats_RGN','$set')

	return jsonify(status='OK')



"""Renvoit le nombre total de documents que le testeur en session doit tester.
"""
@mdb.route('/get_count',methods=['GET'])
def get_count():
	dbcounter = mongo.MongoLoad({'user_id': session['username']},
								{'code': 1, '_id': 0})
	test_code = dbcounter.retrieve('Testeurs',limit=1)[0]['code']
	doc_number = dbcounter.mongocount('Resultats_RGN',{'testers': {'$bitsAllSet': 2**test_code}})
	
	return jsonify(nbtest=doc_number,pseudo=session['username'])



"""Extraction de documents à tester de la collection 'Résultats_RGN' (résultats du
scraping) de la base de données, en fonction du testeur qui a lancé la requête, et
renvoie en format JSON des résultats à la page de tests.
"""
@mdb.route('/get_results',methods=['GET'])
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
					{'search_version': 1, 'img_url': 1, 'tag_list': 1,
					 'location_list': 1, 'location': 1, 'name': 1, '_id': 0})
	doc_list = dbfinder.retrieve('Resultats_RGN',limit=limit)

	return jsonify({'results': doc_list})


"""Réception des résultats du test-expert et stockage dans la base de données;
décrémentation de la champ 'testers' des documents qui viennent d'être testés
de la collection 'Resultats_RGN', et incrémentation du champ 'num_answers' du
testeur dans la collection 'Testeurs'.
"""
@mdb.route('/send_results',methods=['POST'])
def send_results():
	#La méthode POST renvoie des bytes: convertir en string JSON puis en dico python
	response = json.loads(request.data.decode('utf-8'))
	tester = session['username']
	version = response['search_version']
	test_results = response['results']
	url_list = response['img_url']
	doc_results = list(zip(url_list,test_results))

	new_document = {}
	for url, test_item in doc_results:
		if test_item['lieux_choisis']: #Si la liste est vide, le testeur n'a pas su répondre
			new_document = {
								'tester': tester,
								'search_version': version,
								'img_url': url,
								'locations_selected': test_item['lieux_choisis'],
								'sufficient': test_item['suffisant']
						}
	documents = mongo.MongoSave([new_document])
	documents.storeindb('Resultats_Test_Expert_1',img_url='A',search_version='D')

	update = mongo.MongoUpd({
								'update': 'num_answers',
								'newvalue': 1,
								'id_field': {'name': 'user_id', 'values': [tester]}
							})
	update.updatedb('Testeurs','$inc')

	dbfinder = mongo.MongoLoad({'user_id': tester},
							   {'code': 1, '_id': 0})
	test_code = dbfinder.retrieve('Testeurs',limit=1)[0]['code']

	dbfinder.reinit({'img_url': {'$in': url_list}, 'search_version': version},
					{'testers': 1, '_id': 0})
	all_testers = dbfinder.retrieve('Resultats_RGN')
	sum_list = []
	for doc in all_testers:
		tester_sum = int.from_bytes(doc['testers'],byteorder='big') #classmethod, appelée sans instance
		tester_sum &= (~ (1<<test_code))
		bytesize = floor(log2(tester_sum)/8) + 1
		tester_sum = tester_sum.to_bytes(bytesize,byteorder='big')
		sum_list.append(tester_sum)

	update.reinit({
					'update': 'testers',
					'newvalue': sum_list,
					'id_field': {'name': 'img_url', 'values': url_list},
					'other_field': {'name': 'search_version', 'value': version} 
				 })
	update.updatedb('Resultats_RGN','$set')

	return jsonify(status='OK')
