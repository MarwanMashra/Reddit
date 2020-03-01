#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import abc, dns, pymongo, sys


"""De https://docs.python.org/3/library/abc.html: 'Unlike Java abstract methods, these abstract
methods may have an implementation. This implementation can be called via the super() mechanism
from the class that overrides it.'
"""
class Mongo(abc.ABC):
	@abc.abstractmethod #Pas d'instantiation de cette classe
	def mongo_connect(self):
		client = pymongo.MongoClient('mongodb+srv://scrapelord:dPSw8KCjKgF2fVp@redditscrape-bxkhv.'
								    +'mongodb.net/test?retryWrites=true&w=majority')
		return client.RedditScrape

	def mongocheck(self,coll_exists):
		reddit = self.mongo_connect()
		if coll_exists in reddit.list_collection_names():
			return True
		else:
			return False

"""Insertion de documents: création de la collection si elle n'existe pas, et création
de l'index à partir des arguments nommés passé à la méthode d'insertion. L'index n'est
pas obligatoire.
Syntaxe pour l'index en paramètre: <nom champs du document>=<'A' ou 'D'>,... Sera transformé
en liste de tuples pour le passage à la méthode de pymongo.collections.
De pymongo: 'An important note about collections (and databases) in MongoDB is that they
are created lazily (...) Collections and databases are created when the first document is
inserted into them.'
"""
class MongoSave(Mongo):
	def __init__(self,dblist):
		self.document = dblist

	def reinit(self,dblist):
		self.document = dblist

	def mongo_connect(self):
		return super().mongo_connect()

	def storeindb(self,coll_tostore,**index):
		reddit = self.mongo_connect()
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
			coll.insert_many(self.document,ordered=False)
		except pymongo.errors.BulkWriteError as error:
			for e in error.details['writeErrors']:
				if e['code'] == 11000: #DuplicateKeyError
					print('Document '+str(e['op']['_id'])+' déjà présent dans la collection '
						+coll.name+' de la base de données.')
				else:
					sys.exit('Erreur lors de l\'écriture: '+e['errmsg'])
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
class MongoUpd(Mongo):
	def __init__(self,dic):
		self.filter = dic

	def reinit(self,dic):
		self.filter = dic

	def mongo_connect(self):
		return super().mongo_connect()

	"""De mongoDB manual: 'Implicitly, a logical AND conjunction connects the clauses of a compound
	query so that the query selects the documents in the collection that match all the conditions.'"""
	def updatedb(self,coll_toupd,unset=False):
		reddit = self.mongo_connect()
		coll = reddit[coll_toupd]
		if not unset:
			op = '$set' #Mise à jour de champs
		else:
			op = '$unset' #Suppression de champs
		for dico in self.filter['updates']:
			coll.update_many({
								'img_url': {'$in': dico['url']},
								'search_version': self.filter['search_version']
							 },
							 {op: {dico['field']: dico['newvalue']}})


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
class MongoLoad(Mongo):
	def __init__(self,dic_q,dic_p):
		self.query = dic_q
		self.projection = dic_p

	def reinit(self,dic_q,dic_p):
		self.query = dic_q
		self.projection = dic_p

	def mongo_connect(self):
		return super().mongo_connect()

	def retrieve(self,coll_tosearch,limit=0):
		reddit = self.mongo_connect()
		coll = reddit[coll_tosearch]
		if limit == 0:
			return list(coll.find(self.query,self.projection))
		else:
			return list(coll.find(self.query,self.projection,limit=limit))



