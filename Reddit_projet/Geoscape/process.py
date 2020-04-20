#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import Geoscape.mongo as mongo
from itertools import chain, groupby, takewhile
from more_itertools import bucket



def select_results(version, url_list):
	"""Prépare le traitement des résultats de tests des documents dont tous les tests
	ont été effectués. Récupère les résultats dans la collection de résultats et les
	valeurs nécessaires dans les documents issus du scraping.
	Sélection des résultats de test définitifs à partir des choix majoritaires des
	testeurs.
	"""

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



def good_neighbors(bad_vector, all_vectors, is_correct):
	"""Réuni les noms propres voisins du lieu choisi erroné dans la liste de résultats.
	"""

	f_idx = bad_vector[0][0] #Position dans all_vectors
	l_idx = bad_vector[-1][0]
	neighbors = [t[1] for t in bad_vector]
	final_index = 0

	#Ne pas vérifier x[2] == 'NP0' dans la λ-expression: privilégier le choix du testeur
	for vect in takewhile(lambda x: x[0], all_vectors[:f_idx][::-1]):
		neighbors.insert(0,vect)
		final_index += 1

	for vect in takewhile(lambda x: x[0], all_vectors[l_idx+1:]):
		neighbors.append(vect)

	return {'errpos': final_index, 'errlen': len(bad_vector), 'errlist': neighbors,
			'errtype': is_correct}



def create_rule():
	"""Recherche d'erreurs et création de nouvelles règles à partir de celles-ci.
	Récupère dans la base de données les résultats finaux des tests si le champ
	'sufficient' est vrai, c'est-à-dire s'il est possible de récupérer le lieu dans le
	titre.
	La liste des lieux potentiels est converti en liste de mots distincts correctement
	indiciés. Cette liste est ensuite fusionnée avec les listes de résultat du test et
	d'étiquettes TreeTagger.
	Sont extraites de cette liste de comparaison les sous-listes contenant les erreurs
	détectées et les noms propres voisins.
	Les nouvelles règles sont construites à partir de ces sous-listes.
	"""

	dbfinder = mongo.MongoLoad(proj={'search_version': 1, '_id': 0})
	max_version = max(doc['search_version'] for doc in dbfinder.retrieve('Versions_Scrape'))
	next_version = str(float(max_version) + 0.01)

	dbfinder.reinit({'processed': {'$eq': False}, 'sufficient': {'$eq': True}},
					{'search_version': 0, '_id': 0})

	rule_list = []
	for doc in dbfinder.retrieve('Resultats_Final_Expert_1'):
		words = chain(*(
					loc.split(' ') if type(loc) == str else [0 for i in range(loc)]
					for loc in doc['location_list']))

		tags = doc['tag_list']
		comp_list = list(zip(doc['locations_selected'],words,(t[1] for t in tags),
					(t[0] for t in tags)))

		bad_results = []
		# 0-enum 1-(0-booléens test lieux 1-lieux potentiels 2-tags 3-mots)
		for k, g in groupby(enumerate(comp_list), key = lambda x: x[1][0] != bool(x[1][1])):
			if k:
				for kk, gg in groupby(g, key = lambda x: x[1][0]):
					vect = list(gg)
					bad_results.append(good_neighbors(vect,comp_list,vect[0][1][0]))
		
		for result in bad_results:
			errpos = result['errpos']
			errlen = result['errlen']
			rule_vect = result['errlist'][errpos:errpos+errlen]
			take = 0 if result['errtype'] else 'X'

			if len(result['errlist']) - errlen > 0:
				take = 2 if result['errtype'] else 'X'

				if errpos == len(result['errlist']) - 1:
					rule_vect = result['errlist'][:errpos]
					take = 1 if result['errtype'] else 'R'
				elif errpos == 0:
					rule_vect = result['errlist'][errpos+errlen:]
					take = -1 if result['errtype'] else 'L'

			new_rule = {'country': doc['country'], 'expr': ' '.join(i[3] for i in rule_vect),
						'pos': [i[2] for i in rule_vect], 'take': take,
						'search_version': next_version, 'img_url': doc['img_url'],
						'verified': False}
			print(new_rule)
			rule_list.append(new_rule)

	if rule_list:
		db = mongo.MongoSave(rule_list)
		db.nonunique_index('Nouvelles_Regles',country='A',search_version='D')
		db.storeindb('Nouvelles_Regles',country='A',expr='A',pos='A',take='A')

		db.reinit([{'search_version': next_version, 'submissions_scraped': 0, 'accuracy': 0}])
		db.storeindb('Versions_Scrape')

		upd = mongo.MongoUpd({'processed': {'$eq': False}},{'$set': {'processed': True}})
		upd.singleval_upd('Resultats_Final_Expert_1')
