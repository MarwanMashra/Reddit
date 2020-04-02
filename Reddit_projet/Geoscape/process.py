#!/usr/bin/env python3
#-*- coding: utf-8 -*-



"""Sélection des résultats de test définitifs à partir des choix des testeurs.
Results_dic est un dictionnaire dont les clés sont des url qui correspondent aux
documents scrapés. A chaque clé est associé une liste stockant les dictionnaires
de résultats correspondant à chaque testeur, et en dernier élément un dictionnaire
correspondant au document scrapé.
"""
def select_results(results_dic):
	final_results = []
	for key, value in results_dic.items():
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

	return final_results
