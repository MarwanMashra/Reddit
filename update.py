#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import Reddit_projet.Geoscape.mongo as mongo 
import pprint
from math import floor, log2


#Script de recharge du champs 'testers' des documents NOT_OK pour les tests

"""Classe de mise à jour simplifiée et plus générique.
On fait une mise à jour seulement sur un champs, avec une nouvelle valeur.
"""
# update_dic = {}
# update_dic['update'] = 'test_result'
# update_dic['newvalue'] = 'OK'
# update_dic['id_field'] = {
# 							'name': 'img_url',
# 							'values': ['https://i.redd.it/7h95m06db2w31.png']
# 						 }
# update_dic['other_field'] = {
# 								'name': 'search_version',
# 								'value': '1.00'
# 							}
# updater = mongo.MongoUpd(update_dic)
# updater.updatedb('Resultats_RGN','$set') #Rajout du champs 'test_result'
# print('Succès.')
# updater.reinit({
# 					'update': 'test_result',
# 					'newvalue': 'NOT_OK',
# 					'id_field': {
# 									'name': 'img_url',
# 									'values': ['https://i.imgur.com/3LDmMr7.jpg',
# 											   'https://i.redd.it/ldo1mxojjug41.jpg',
# 											   'https://i.redd.it/lnckwb6v4ee41.jpg',
# 											   'https://i.redd.it/6wbjlunbdlc41.jpg',
# 											   'https://i.redd.it/2qhzpuf77se41.jpg',
# 											   'https://i.redd.it/ldo1mxojjug41.jpg']
# 								},
# 					'other_field': {
# 									'name': 'search_version',
# 									'value': '1.00'
# 									}
# 				})
# updater.updatedb('Resultats_RGN','$set')
# print('Succès.')
test_code = 2**4 + 2**5 + 2**7
bytesize = floor(log2(test_code)/8) + 1
test_code = test_code.to_bytes(bytesize,byteorder='big')
updater = mongo.MongoUpd({
					'update': 'testers',
					'newvalue': test_code,
					'id_field': {
									'name': 'img_url',
									'values': [
										'https://farm6.staticflickr.com/5694/22094095775_025473a5de_b.jpg',
										'https://i.redd.it/q815f4j0r7n41.jpg'
											]
								},
					'other_field': {
									'name': 'search_version',
									'value': '1.00'
									}
				})
updater.updatedb('Resultats_RGN','$set')
print('Succès.')
