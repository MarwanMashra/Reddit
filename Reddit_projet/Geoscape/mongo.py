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
		if coll_exists in client.list_collection_names():
			return True
		else:
			return False

	"""Vérifie l'existence d'un index et renvoie son nom. Les champs
	indexés à rechercher sont passés dans un tuple.
	Retour de index_information(): dictionnaire de dictionnaires:
	{
		<nom index>: { 'key': [(<champ indexé>, <0 ou 1>),...],
						<autres informations>
					 }
		<nom index>: ...
	}
	"""
	@classmethod
	def indexcheck(cls,coll_tocheck,*index):
		coll = client[coll_tocheck]
		indexes = coll.index_information()
		field_list = []
		this_index = ''
		for key in indexes:
			for field in index:
				for i_field, order in indexes[key]['key']:
					if field == i_field:
						field_list.append(field)
						break
			if len(field_list) == len(index):
				this_index = key
				break
			else:
				field_list = []
		return this_index

	"""Compte et renvoit le nombre de documents dans une collection.
	'query' est une requête pour filtrer les documents devant être comptés.
	"""
	@classmethod
	def mongocount(cls,coll_tocount,query={}):
		coll = client[coll_tocount]
		return coll.count_documents(query)


"""Insertion de documents: création de la collection si elle n'existe pas, et création
de l'index à partir des arguments nommés passé à la méthode d'insertion. L'index n'est
pas obligatoire.
Syntaxe pour l'index en paramètre: <nom champ du document>=<'A' ou 'D'>,... Sera transformé
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

	def storeindb(self,coll_tostore,**index):
		if len(self.document) == 0: #Une liste vide passée à insert_many provoque un bug
			return
		coll = client[coll_tostore]
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
	update: <champ à mettre à jour>
	newvalue: <nouvelle valeur> OU [<nouvelle valeur>,...] #liste de même taille que la liste id_field['values']
	id_field: {
		name: <nom du champ> #par exemple img_url
		values: [<valeur du champs>,...]
	#Optionnel
	other_field: {
		name: <nom du champ unique> #par exemple search_version
		value: <valeur du champ unique>
}
"""
class MongoUpd(Mongo):
	def __init__(self,dic):
		self.filter = dic

	def reinit(self,dic):
		self.filter = dic

	"""De mongoDB manual: 'Implicitly, a logical AND conjunction connects the clauses of a compound
	query so that the query selects the documents in the collection that match all the conditions.'
	Paramètre operator: '$set', '$unset', '$inc' fonctionnent
	"""
	def updatedb(self,coll_toupd,operator):
		coll = client[coll_toupd]
		if type(self.filter['newvalue']) == list:
			id_and_val = list(zip(self.filter['id_field']['values'],self.filter['newvalue']))
			for ident, value in id_and_val:
				if 'other_field' in self.filter:
					coll.update_one({
									  self.filter['id_field']['name']: ident,
									  self.filter['other_field']['name']: self.filter['other_field']['value']
									},
									{operator: {self.filter['update']: value}})
				else:
					coll.update_one({self.filter['id_field']['name']: ident},
									{operator: {self.filter['update']: value}})
		elif 'other_field' in self.filter:
			coll.update_many({
								self.filter['id_field']['name']: {'$in': self.filter['id_field']['values']},
								self.filter['other_field']['name']: self.filter['other_field']['value']
							 },
							 {operator: {self.filter['update']: self.filter['newvalue']}})
		else:
			coll.update_many({self.filter['id_field']['name']: {'$in': self.filter['id_field']['values']}},
							 {operator: {self.filter['update']: self.filter['newvalue']}})



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

	def reinit(self,query,proj={'_id': 0}):
		self.query = query
		self.projection = proj

	def retrieve(self,coll_tosearch,limit=0):
		coll = client[coll_tosearch]
		if not self.projection and limit == 0:
			return list(coll.find(self.query))
		elif not self.projection:
			return list(coll.find(self.query,limit=limit))
		elif limit == 0:
			return list(coll.find(self.query,self.projection))
		else:
			return list(coll.find(self.query,self.projection,limit=limit))

	def dltdocument(self,coll_toupd):
		coll = client[coll_toupd]
		coll.find_one_and_delete(self.query,projection={'_id': 0})



