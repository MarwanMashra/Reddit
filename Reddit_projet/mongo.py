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

	"""Vérifie l'existence d'une collection.
	"""
	def mongocheck(self,coll_exists):
		reddit = self.mongo_connect()
		if coll_exists in reddit.list_collection_names():
			return True
		else:
			return False

	"""Vérifie l'existence d'un index et renvoie son nom. Les champs
	indexés à rechercher sont passés dans un tuple.
	Retour de index_information(): dictionnaire de dictionnaires:
	{
		<nom index>: { 'key': [(<champs indexé>, <0 ou 1>),...],
						<autres informations>
					 }
		<nom index>: ...
	}
	"""
	def indexcheck(self,coll_tocheck,*index):
		reddit = self.mongo_connect()
		coll = reddit[coll_tocheck]
		indexes = coll.index_information()
		field_list = []
		this_index = ''
		for key in indexes:
			for field in index:
				for pair in indexes[key]['key']:
					if field == pair[0]:
						field_list.append(field)
						break
			if len(field_list) == len(index):
				this_index = key
				break
			else:
				field_list = []
		return this_index


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
		if len(self.document) == 0: #Une liste vide passée à insert_many provoque un bug
			return
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


"""Mises à jour: syntaxe du dico de chargement:
{
	update: <champs à mettre à jour>
	newvalue: <nouvelle valeur>
	id_field: {
		name: <nom du champ> #par exemple img_url
		values: [<valeur du champs>,...]
	#Optionnel
	other_field: {
		name: <nom du champs unique> #par exemple search_version
		value: <valeur du champs unique>
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
	query so that the query selects the documents in the collection that match all the conditions.'
	Paramètre operator: '$set', '$unset', '$inc' fonctionnent
	"""
	def updatedb(self,coll_toupd,operator):
		reddit = self.mongo_connect()
		coll = reddit[coll_toupd]
		if 'other_field' in self.filter:
			coll.update_many({
								self.filter['id_field']['name']: {'$in': self.filter['id_field']['values']},
								self.filter['other_field']['name']: self.filter['other_field']['value']
							 },
							 {operator: {self.filter['update']: self.filter['newvalue']}})
		else:
			coll.update_many({self.filter['id_field']['name']: {'$in': self.filter['id_field']['values']}},
							 {operator: {self.filter['update']: self.filter['newvalue']}})


"""Recherche et extraction d'un document: format paramètres:
La requête:
{
	<champs>: <valeur>,
	...
	<champs>: { <opérateur>: <valeur> }
	...
	<opérateur logique>: [ <champs>: <valeur>
						   ...
						   <champs>: <valeur>
						 ]
}
La projection par inclusion:
{
	<champs>: 1
	...
	<champs>: 1
	(optionnel) '_id': 0 (seul exclusion qui marche avec l'inclusion)
}
OU par exclusion
{
	<champs>: 0
	...
	<champs>: 0
}
Si on veut retourner tous les champs passer un dictionnaire vide en deuxième paramètre.
"""
class MongoLoad(Mongo):
	def __init__(self,dic_q,dic_p={'_id': 0}):
		self.query = dic_q
		self.projection = dic_p

	def reinit(self,dic_q,dic_p={'_id': 0}):
		self.query = dic_q
		self.projection = dic_p

	def mongo_connect(self):
		return super().mongo_connect()

	def retrieve(self,coll_tosearch,limit=0):
		reddit = self.mongo_connect()
		coll = reddit[coll_tosearch]
		if not self.projection and limit == 0:
			return list(coll.find(self.query))
		elif not self.projection:
			return list(coll.find(self.query,limit=limit))
		elif limit == 0:
			return list(coll.find(self.query,self.projection))
		else:
			return list(coll.find(self.query,self.projection,limit=limit))



