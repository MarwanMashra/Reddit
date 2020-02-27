#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import dns, pymongo

"""De pymongo: 'An important note about collections (and databases) in MongoDB is
that they are created lazily (...) Collections and databases are created when the
first document is inserted into them.'"""

class MongoSave:
	def __init__(self,dic):
		self.document = dic

	def storeindb(self,coll_tostore):
		client=pymongo.MongoClient('mongodb+srv://scrapelord:dPSw8KCjKgF2fVp@redditscrape-bxkhv.'
								  +'mongodb.net/test?retryWrites=true&w=majority') #Connexion
		reddit=client.RedditScrape #Renvoie la base de données RedditScrape
		coll=reddit[coll_tostore]
		"""De mongoDB manual: ' If you use the unique constraint on a compound index, then MongoDB
		will enforce uniqueness on the combination of the index key values.'"""
		coll.create_index([('search_version',pymongo.DESCENDING),
						   ('img_url',pymongo.ASCENDING)],name='img_and_version',unique=True)
		try:
			coll.insert_one(self.document)
		except pymongo.errors.DuplicateKeyError:
			print('Document déjà présent dans la collection '+coll.name+' de la base de données.')
		else:
			pass
