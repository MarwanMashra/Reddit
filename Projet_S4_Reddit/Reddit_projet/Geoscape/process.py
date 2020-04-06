#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import Geoscape.mongo as mongo
from itertools import chain, groupby, takewhile
from more_itertools import bucket



"""Prépare le traitement des résultats de tests des documents dont tous les tests
ont été effectués. Récupère les résultats dans la collection de résultats et les
valeurs nécessaires dans les documents issus du scraping.
Sélection des résultats de test définitifs à partir des choix majoritaires des
testeurs.
"""
def select_results(version, url_list):
	dbfinder = mongo.MongoLoad({'img_url': {'$in': url_list}, 'search_version': version},
							   {'img_url': 1, 'locations_selected': 1, 'sufficient': 1, '_id': 0})

	group_results = bucket(dbfinder.retrieve('Resultats_Test_Expert_1'),
					key = lambda x: x['img_url'])

	dbfinder.reinit({'img_url': {'$in': url_list}, 'search_version': version},
					{'search_version': 1, 'country': 1, 'img_url': 1, 'tag_list': 1,
					 'location_list': 1, '_id': 0})

	final_results = []
	for doc in dbfinder.retrieve('Resultats_RGN'):
		result = list(group_results[doc['img_url']]) #Conversion de l'itérateur car double parcours nécessaire
		doc['locations_selected'] = [True if comp.count(True) > len(comp)/2 else False
									 for comp in zip(*[res['locations_selected'] for res in result])]									 

		doc['sufficient'] = True if sum(1 if b else -1 for b in
							[res['sufficient'] for res in result]) > 0 else False
		doc['processed'] = False

		final_results.append(doc)

	return final_results



"""Réuni les noms propres voisins du lieu choisi erroné dans la liste de résultats.
"""
def good_neighbors(bad_vector, all_vectors):
	f_idx = bad_vector[0][0] #Position dans all_vectors
	l_idx = bad_vector[-1][0]
	neighbors = [t[1:] for t in bad_vector]
	final_index = 0

	for vect in takewhile(lambda x: x[0] and x[2] == 'NP0', all_vectors[:f_idx][::-1]):
		neighbors.insert(0,vect)
		final_index += 1

	for vect in takewhile(lambda x: x[0] and x[2] == 'NP0', all_vectors[l_idx+1:]):
		neighbors.append(vect)

	return {'errpos': final_index, 'errlist': neighbors}



"""Recherche d'erreurs et création de nouvelles règles à partir de celles-ci. La
liste des lieux potentiels est converti en liste de mots distincts correctement
indiciés. Cette liste est ensuite fusionnée avec les listes de résultat du test et
d'étiquettes TreeTagger.
Sont extraites de cette liste de comparaison les sous-listes contenant les erreurs
détectées et les noms propres voisins.
"""
def create_rule():
	dbfinder = mongo.MongoLoad(proj={'search_version': 1, '_id': 0})
	max_version = max(doc['search_version'] for doc in dbfinder.retrieve('Versions_Scrape'))
	next_version = str(float(max_version) + 0.01)

	dbfinder.reinit({'processed': {'$eq': False}},{'search_version': 0, '_id': 0})

	rule_list = []
	for doc in dbfinder.retrieve('Resultats_Final_Expert_1'):
		words = chain(*(
					loc.split(' ') if type(loc) == str else [0 for i in range(loc)]
					for loc in doc['location_list']))

		tags = doc['tag_list']
		comp_list = list(zip(doc['locations_selected'],words,(t[1] for t in tags),
					(t[0] for t in tags)))

		bad_results = []
		for k, g in groupby(enumerate(comp_list), key = lambda x: x[1][0] != bool(x[1][1])):
			if k:
				bad_results.append(good_neighbors(list(g),comp_list))
		
		for result in bad_results:
			index = result['errpos']
			lvect = len(result['errlist'][index])
			rule_vect = result['errlist'][index:index+lvect]
			take = 0

			if len(result['errlist']) > 1:
				take = 2
				if index == len(result['errlist']) - 1:
					rule_vect = result['errlist'][:index]
					take = 1
				elif index == 0:
					rule_vect = result['errlist'][index+lvect:]
					take = -1

			new_rule = {'country': doc['country'], 'expr': ' '.join(i[3] for i in rule_vect),
						'pos': [i[2] for i in rule_vect], 'take': take,
						'search_version': next_version, 'img_url': doc['img_url']}

			rule_list.append(new_rule)

	if rule_list:
		db = mongo.MongoSave(rule_list)
		db.nonunique_index('Nouvelles_Regles',country='A',search_version='D')
		db.storeindb('Nouvelles_Regles',country='A',expr='A',pos='A',take='A')

		db.reinit([{'search_version': next_version, 'submissions_scraped': 0, 'accuracy': 0}])
		db.storeindb('Versions_Scrape')

		upd = mongo.MongoUpd({'processed': {'$eq': False}},{'$set': {'processed': True}})
		upd.singleval_upd('Resultats_Final_Expert_1')
