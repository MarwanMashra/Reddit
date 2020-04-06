#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import Reddit_projet.Geoscape.mongo as mongo 
import pprint
from math import floor, log2

i = 16
var = i.to_bytes(1,'big')
upd = mongo.MongoUpd({'img_url':'https://i.redd.it/q815f4j0r7n41.jpg'},
					 {'$set': {'testers': var}})
upd.singleval_upd('Resultats_RGN')
print('Succès.')
