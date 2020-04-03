#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import Geoscape.mongo as mongo



"""Prépare le traitement des résultats de tests des documents dont tous les tests
ont été effectués. Récupère les résultats dans la collection de résultats et les
valeurs nécessaires dans les documents issus du scraping.
Sélection des résultats de test définitifs à partir des choix majoritaires des
testeurs.
"""
def select_results(version, url_list):
	dbfinder = mongo.MongoLoad({'img_url': {'$in': url_list}, 'search_version': version},
							   {'img_url': 1, 'locations_selected': 1, 'sufficient': 1, '_id': 0})

	group_results = {}
	for doc in dbfinder.retrieve('Resultats_Test_Expert_1'):
		if doc['img_url'] in group_results:
			group_results[doc['img_url']].append(doc)
		else:
			group_results[doc['img_url']] = [doc]

	dbfinder.reinit({'img_url': {'$in': url_list}, 'search_version': version},
					{'search_version': 1, 'country': 1, 'img_url': 1, 'tag_list': 1,
					 'location_list': 1, '_id': 0})

	for doc in dbfinder.retrieve('Resultats_RGN'):
		group_results[doc['img_url']].append(doc)

	final_results = []
	for key, value in group_results.items():
		final_doc = {'search_version': value[-1]['search_version'], 'country': value[-1]['country'],
					 'img_url': key, 'tag_list': value[-1]['tag_list'], 'location_list':
					 value[-1]['location_list']}

		result_list = []
		suff_list = []
		for doc in value[:-1]:
			result_list.append(doc['locations_selected'])
			suff_list.append(doc['sufficient'])

		final_loc = []
		for combined_loc in zip(*result_list): #combined_loc est un tuple de booléens
			final_loc.append(True if sum(1 if b else -1 for b in combined_loc) > 0 else False)

		final_doc['locations_selected'] = final_loc
		final_doc['sufficient'] = True if sum(1 if b else -1 for b in suff_list) > 0 else False
		final_results.append(final_doc)

	print(final_results)
	return final_results
