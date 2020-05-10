#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import Geoscape.server.mongo as mongo
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
		good_neighbors = []
		err = []
		i = 0

		while i < len(comp_list):
			if comp_list[i][0] and comp_list[i][0] == bool(comp_list[i][1]):
				good_neighbors.append(list(takewhile(lambda x: x[0], comp_list[i:])))
				i += len(good_neighbors)

			if i < len(comp_list) and comp_list[i][0] != bool(comp_list[i][1]):
				errpos = len(good_neighbors)
				errtype = comp_list[i][0]
				err = list(takewhile(lambda x:
							x[0] != bool(x[1]) and x[0] == errtype, comp_list[i:]))
				badlen = len(err)

				err.extend(list(takewhile(lambda x: x[0], comp_list[i+badlen:])))
				good_neighbors.extend(err)

				bad_results.append({ 'errpos': errpos, 'errlen': badlen,
									 'errlist': good_neighbors, 'errtype': errtype})
				good_neighbors = []
				err = []
				i += badlen

			else:
				good_neighbors.clear()
				i += 1

		for res in bad_results:
			errpos = res['errpos']
			errlen = res['errlen']
			errlist = res['errlist']
			errtype = res['errtype']
			rule_vect = errlist[errpos:errpos+errlen]
			take = 0 if errtype else 'X'

			if len(errlist) - errlen > 0:
				take = 2 if errtype else 'X'

				if errpos == len(errlist) - 1:
					rule_vect = errlist[:errpos]
					take = 1 if errtype else 'R'

				elif errpos == 0:
					rule_vect = errlist[errpos+errlen:]
					take = -1 if errtype else 'L'

			new_rule = {'country': doc['country'], 'expr': ' '.join(i[3] for i in rule_vect),
						'pos': [i[2] for i in rule_vect], 'take': take,
						'search_version': next_version, 'img_url': doc['img_url'],
						'verified': False}
			rule_list.append(new_rule)

	if rule_list:
		db = mongo.MongoSave(rule_list)
		db.nonunique_index('Nouvelles_Regles',country='A',search_version='D')
		db.storeindb('Nouvelles_Regles',country='A',expr='A',pos='A',take='A')

		db.reinit([{'search_version': next_version, 'submissions_scraped': 0, 'accuracy': 0}])
		db.storeindb('Versions_Scrape')

		upd = mongo.MongoUpd({'processed': {'$eq': False}},{'$set': {'processed': True}})
		upd.singleval_upd('Resultats_Final_Expert_1')
