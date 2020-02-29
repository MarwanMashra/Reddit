#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import dns, pymongo


"""Insertion d'un document: création de la collection si elle n'existe pas, et création
de l'index à partir des arguments nommés passé à la méthode d'insertion. L'index n'est
pas obligatoire.
Syntaxe pour l'index en paramètre: <nom champs du document>=<'A' ou 'D'>,... Sera transformé
en liste de tuples pour le passage à la méthode de pymongo.collections.
De pymongo: 'An important note about collections (and databases) in MongoDB is that they
are created lazily (...) Collections and databases are created when the first document is
inserted into them.'
"""
class MongoSave:
	def __init__(self,dic):
		self.document = dic

	def reinit(self,dic):
		self.document = dic

	def storeindb(self,coll_tostore,**index):
		client = pymongo.MongoClient('mongodb+srv://scrapelord:dPSw8KCjKgF2fVp@redditscrape-bxkhv.'
								    +'mongodb.net/test?retryWrites=true&w=majority') #Connexion
		reddit = client.RedditScrape #Renvoie la base de données RedditScrape
		coll = reddit[coll_tostore]
		index_list = []
		for key,value in index.items():
			if value == 'A':
				index_list.append((key,pymongo.ASCENDING))
			else:
				index_list.append((key,pymongo.DESCENDING))
		"""De mongoDB manual: 'If you use the unique constraint on a compound index, then MongoDB
		will enforce uniqueness on the combination of the index key values.'"""
		if index_list:
			index_name = ''
			for i in index_list:
				ishort = i[0].split('_')
				index_name += ishort[0] + '_'
			coll.create_index(index_list,name=index_name.rstrip('_'),unique=True)
		try:
			coll.insert_one(self.document)
		except pymongo.errors.DuplicateKeyError:
			print('Document déjà présent dans la collection '+coll.name+' de la base de données.')
		else:
			pass


"""Mises à jour: un dictionnaire contenant une clé 'search_version' dont la valeur est la version
du scraper utilisée, et une clé 'updates' dont la valeur est une liste dont les éléments sont des
dicos. Ces dicos ont comme clés: field, dont la valeur est le nom du champs à ajouter/modifier;
newvalue, qui contient la nouvelle valeur du champs, et url, une liste des 'img_url' des documents
à modifier. Les dicos de la liste updates peuvent affecter le même champs (même valeur pour les
différentes clés 'field'), si on veut mettre à jour un champs avec des valeurs différentes selon
le document.
{
	search_version: <string>
	updates:
	[
		{
			field: <champs à modifier>
			newvalue: <nouvelle valeur du champs>
			url: [img_url du doc A1,...,img_url du doc An]
		}
		{
			...
		}
		...
	]
}
"""
class MongoUpd:
	def __init__(self,dic):
		self.filter = dic

	def reinit(self,dic):
		self.filter = dic

	def updatedb(self,coll_toupd):
		client = pymongo.MongoClient('mongodb+srv://scrapelord:dPSw8KCjKgF2fVp@redditscrape-bxkhv.'
								    +'mongodb.net/test?retryWrites=true&w=majority')
		reddit = client.RedditScrape
		coll = reddit[coll_toupd]
		"""De mongoDB manual: 'Implicitly, a logical AND conjunction connects the clauses of a compound
		query so that the query selects the documents in the collection that match all the conditions.'"""
		for dico in self.filter['updates']:
			coll.update_many({
								'img_url': {'$in': dico['url']},
								'search_version': self.filter['search_version']
							 },
							 {'$set': {dico['field']: dico['newvalue']}})


"""Recherche et extraction d'un document: format paramètres:
La requête, simple pour le moment:
{
	<champs>: <valeur>,
	...
	<champs>: <valeur>
}
La projection (par inclusion):
{
	<champs>: 1
	...
	<champs>: 1
	(optionnel) '_id': 0
}
OU (par exclusion)
{
	<champs>: 0
	...
	<champs>: 0
}
Si on veut retourner tous les champs, passer un dictionnaire vide.
"""
class MongoLoad:
	def __init__(self,dic_q,dic_p):
		self.query = dic_q
		self.projection = dic_p

	def reinit(self,dic_q,dic_p):
		self.query = dic_q
		self.projection = dic_p

	def retrieve(self,coll_tosearch,limit=0):
		client = pymongo.MongoClient('mongodb+srv://scrapelord:dPSw8KCjKgF2fVp@redditscrape-bxkhv.'
								    +'mongodb.net/test?retryWrites=true&w=majority')
		reddit = client.RedditScrape
		coll = reddit[coll_tosearch]
		if limit == 0:
			return list(coll.find(self.query,self.projection))
		else:
			return list(coll.find(self.query,self.projection,limit=limit))



