#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import mongo

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
updater = mongo.MongoUpd(update_dic)
updater.updatedb('Resultats_RGN')