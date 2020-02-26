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
		client=pymongo.MongoClient("mongodb+srv://scrapelord:dPSw8KCjKgF2fVp@redditscrape-bxkhv."
								  +"mongodb.net/test?retryWrites=true&w=majority") #Connexion
		reddit=client.RedditScrape #Renvoie la base de données RedditScrape
		coll=reddit[coll_tostore]
		cursors=coll.find()
		nostore = False
		for res in cursors:
			if res["img_url"] == self.document["img_url"] and \
			res["search_version"] == self.document["search_version"]:
				nostore = True
				break
		if not nostore:
			coll.insert_one(self.document)
		else:
			print("Document déjà présent dans la collection "+coll.name+" de la base de données.")
