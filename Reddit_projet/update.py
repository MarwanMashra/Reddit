#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import mongo, pprint


#SCRIPT TEST

update_dic = {}
#Les deux clés doivent être présentes
update_dic['search_version'] = '1.00'
update_dic['updates'] = [] #Si liste vide, pas d'erreurs
update_dic['updates'] = [{
							'field': 'test_result',
							'newvalue': 'OK',
							'url': ['https://i.redd.it/7h95m06db2w31.png']
							},
							{
							'field': 'test_result',
							'newvalue': 'NOT_OK',
							'url': ['https://i.redd.it/6wbjlunbdlc41.jpg']
							},
							{
							'field': 'testers',
							'newvalue': 15,
							'url': ['https://i.redd.it/6wbjlunbdlc41.jpg']
							}]

updater = mongo.MongoUpd(update_dic)
updater.updatedb('Resultats_RGN') #Rajout du champs 'test_result'

#Extraction de documents
document = mongo.MongoLoad({'search_version': '1.00', 'test_result': 'NOT_OK'},
						   {'search_version': 1, 'country': 1, 'title': 1,
							'name': 1, 'location': 1, 'testers': 1, '_id': 0},
						   {'op': '$gte', 'field': 'testers', 'value': 8})
test_case = document.retrieve('Resultats_RGN',limit=5)
pprint.pprint(test_case)

update_dic['updates'] = [{
							'field': 'test_result',
							'newvalue': '',
							'url': ['https://i.redd.it/7h95m06db2w31.png','https://i.redd.it/6wbjlunbdlc41.jpg']
						},
						{
							'field': 'testers',
							'newvalue': '',
							'url': ['https://i.redd.it/6wbjlunbdlc41.jpg'] 
						}]
# updater.reinit(update_dic)
# updater.updatedb('Resultats_RGN',unset=True) #Suppression du champs 'test_result'