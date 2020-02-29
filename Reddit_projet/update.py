#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import mongo, pprint

#SCRIPT TEST

update_dic = {}
#Les deux clés doivent être présentes
update_dic['search_version'] = '1.00'
update_dic['updates'] = [] #Si liste vide, pas d'erreurs
"""update_dic['updates'] = [{
							'field': 'test_result',
							'newvalue': 'OK',
							'url': ['https://i.redd.it/7h95m06db2w31.png']
							}]
"""
"""update_dic['updates'] = [{
							'field': 'test_result',
							'newvalue': 'NOT_OK',
							'url': ['https://i.redd.it/6wbjlunbdlc41.jpg']
						}]
"""
updater = mongo.MongoUpd(update_dic)
updater.updatedb('Resultats_RGN')

document = mongo.MongoLoad({'search_version': '1.00', 'test_result': 'OK'},
						   {'search_version': 1, 'country': 1, 'title': 1, 'location_list': 1,
							'name': 1, 'location': 1, '_id': 0})
test_case = document.retrieve('Resultats_RGN',limit=5)
pprint.pprint(test_case)