#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import dns, pymongo, sys
from Geoscape.db_init import client



"""Classe de base dont héritent les autres. Permet d'obtenir des informations sur la
base de données, mais pas d'opérer dessus. La connexion elle-même se fait dans le
fichier db_init.py.
"""
class Mongo:
	"""Vérifie l'existence d'une collection.
	"""
	@classmethod
	def mongocheck(cls,coll_exists):
		return coll_exists in client.list_collection_names()

	"""Vérifie l'existence d'un index. Renvoie vrai s'il existe, faux sinon. L'index
	en paramètre doit être une liste de champs à indexer.
	Retour de list_indexes(): itérateur sur des documents au format SON (dictionnaire
	ordonné). Convertir en dico Python avant utilisation.
	"""
	@classmethod
	def indexcheck(cls,coll_tocheck,index):
		coll = client[coll_tocheck]
		for idx in coll.list_indexes():
			idx = idx.to_dict()	#SON->dictionnaire
			arg_compare = sum(1 if name in index else -1
							for name in idx['key'].keys())
			if arg_compare == len(index):
		 		return True
		return False

	"""Création d'un index n'imposant pas une contrainte d'unicité.
	Syntaxe pour l'index en paramètre: <nom champ du document>=<'A' ou 'D'>,... Sera passé
	à la fonction comme dictionnaire, puis converti en liste de tuples pour le passage à la
	méthode de pymongo.collections.
	"""
	@classmethod
	def nonunique_index(cls,coll_toindex,**index):
		coll = client[coll_toindex]
		if len(index) > 0 and cls.indexcheck(coll_toindex,list(index.keys())):
			return
		index_list = []
		for key, value in index.items():
			if value == 'A':
				index_list.append((key,pymongo.ASCENDING))
			else:
				index_list.append((key,pymongo.DESCENDING))
		if index_list:
			index_name = '_'.join([i[0].split('_')[0] for i in index_list])
			coll.create_index(index_list,name=index_name)

	"""Compte et renvoit le nombre de documents dans une collection.
	'query' est une requête pour filtrer les documents devant être comptés.
	"""
	@classmethod
	def mongocount(cls,coll_tocount,query={}):
		coll = client[coll_tocount]
		return coll.count_documents(query)



"""Insertion de documents: création de la collection si elle n'existe pas, et création
optionnelle d'un index sur les champs passés en paramètre. Syntaxe pour l'index en
paramètre: <nom champ du document>=<'A' ou 'D'>,... L'index impose une contrainte
d'unicité sur ces champs.
De pymongo: 'An important note about collections (and databases) in MongoDB is that
they are created lazily (...) Collections and databases are created when the first
document is inserted into them.'
"""
class MongoSave(Mongo):
	def __init__(self,dblist):
		self.document = dblist

	def reinit(self,dblist):
		self.document = dblist

	def storeindb(self,coll_tostore,**index):
		if len(self.document) == 0: #Une liste vide passée à insert_many provoque un bug
			return
		coll = client[coll_tostore]
		if not self.indexcheck(coll_tostore,list(index.keys())):
			index_list = []
			for key, value in index.items():
				if value == 'A':
					index_list.append((key,pymongo.ASCENDING))
				else:
					index_list.append((key,pymongo.DESCENDING))
			"""De mongoDB manual: 'If you use the unique constraint on a compound index, then MongoDB
			will enforce uniqueness on the combination of the index key values.'"""
			if index_list:
				index_name = '_'.join([i[0].split('_')[0] for i in index_list])
				coll.create_index(index_list,name=index_name,unique=True)
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



"""Recherche et extraction d'un document sous forme de liste de document(s).
Format paramètres:
La requête:
{
	<champs>: <valeur>,
	...
	<champs>: { <opérateur>: <valeur> }
	...
	<opérateur logique>: [ <champ>: <valeur>
						   ...
						   <champ>: <valeur>
						 ]
}
La projection par inclusion:
{
	<champ>: 1
	...
	<champ>: 1
	(optionnel) '_id': 0 (seul exclusion qui marche avec l'inclusion)
}
OU par exclusion
{
	<champ>: 0
	...
	<champ>: 0
}
Si on veut retourner tous les champ passer un dictionnaire vide en deuxième paramètre.
"""
class MongoLoad(Mongo):
	def __init__(self,query=None,proj={'_id': 0}):
		self.query = query
		self.projection = proj

	def reinit(self,query=None,proj={'_id': 0}):
		self.query = query
		self.projection = proj

	def retrieve(self,coll_tosearch,limit=0):
		coll = client[coll_tosearch]
		if not self.projection and limit == 0:
			return coll.find(self.query)
		elif not self.projection:
			return coll.find(self.query,limit=limit)
		elif limit == 0:
			return coll.find(self.query,self.projection)
		else:
			return coll.find(self.query,self.projection,limit=limit)

	def dltdocument(self,coll_toupd):
		coll = client[coll_toupd]
		return coll.delete_many(self.query).deleted_count



"""Mises à jour.
Format paramètres:
La requête: voir classe précédente.
La mise à jour, pour un document ou un ensemble de documents:
{
	<opérateur>:
				{
					<champ>: <nouvelle_valeur>
					...
				}
	...
}
"""
class MongoUpd(Mongo):
	def __init__(self,query,update,list_id=[],list_val=[]):
		self.query = query
		self.update = update
		self.list_id = list_id
		self.list_val = list_val

	def reinit(self,query=None,update=None,list_id=[],list_val=[]):
		if query is not None:
			self.query = query
		if update is not None:
			self.update = update
		self.list_id = list_id
		self.list_val = list_val

	"""Mise à jour groupée: plusieurs documents reçoivent la même mise à jour,
	c'est-à-dire un même champ est mis à jour avec la même valeur pour tous.
	"""
	def singleval_upd(self,coll_toupd):
		coll = client[coll_toupd]
		coll.update_many(self.query,self.update)

	"""Mise à jour individualisée: pour le même champ, chaque document reçoit
	une valeur propre. Le paramètre multfield désigne ce champ individualisé.
	"""
	def multval_upd(self,coll_toupd,multfield):
		coll = client[coll_toupd]
		assert self.list_id and self.list_val,'Listes manquantes pour la méthode de mise à jour.'
		for ident, value in zip(self.list_id,self.list_val):
			self.query[multfield] = ident
			for operator in self.update.keys():
				for key in self.update[operator].keys():
					self.update[operator][key] = value
			coll.update_one(self.query,self.update)