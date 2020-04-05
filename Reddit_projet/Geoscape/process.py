#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import Geoscape.mongo as mongo
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
		result = list(group_results[doc['img_url']]) #Double parcours nécessaire
		doc['locations_selected'] = [
								True if sum(1 if b else -1 for b in comp) > 0 else False
								for comp in zip(*[res['locations_selected'] for res in result])
							]
		doc['sufficient'] = True if sum(1 if b else -1 for b in [res['sufficient']
							for res in result]) > 0 else False
		final_results.append(doc)

	print(final_results)
	return final_results
