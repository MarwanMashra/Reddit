#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#UTILISER DES MODULES DE LA BIBLIOTHEQUE STANDARD
from os import chdir, getcwd
from os.path import join
from subprocess import run, CalledProcessError
from sys import exit, platform, version_info
from venv import create



class context:
	"""Classe pour gérer le changement de répertoire et l'installation de Treetagger.
	"""
	def __init__(self,newpath):
		self.newpath = join(getcwd(),newpath)

	def __enter__(self):
		self.oldpath = getcwd()
		chdir(self.newpath)

	def __exit__(self,errtype,value,traceback):
		chdir(self.oldpath)



if not platform.startswith('linux') and not platform.startswith('win'):
	exit('Système d\'exploitation non compatible avec Geoscape.')
if version_info < (3,6):
	raise ValueError('This script does not work with Python versions older than 3.6')

print('Création de l\'environnement virtuel de Geoscape.')

env = 'Geoscape_venv'

create(env,with_pip=True,prompt='Geoscape')

#Pas d'activation extérieur de l'env virtuel: exécution de l'interpréteur de l'env virtuel
env_python = join(getcwd(),env,'bin','python3')

try:
	run([env_python,'-m','pip','install','-r','requirements.txt','--no-cache-dir'],check=True)
except CalledProcessError:
	exit('Erreur à l\'installation des dépendances. Veuillez manuellement installer les' 
		 'dépendances de Geoscape en activant l\'environnement virtuel Geoscape_venv et'
		 'en exécutant ensuite la commande \'pip install -r requirements.txt\'.')
else:
	print('Installation des dépendances de Geoscape réussie.')

with open('GEOSCAPE_VENV_PATH','w') as file:
	file.write(join(getcwd(),env,'bin','activate'))
print('Le chemin absolu pour activer l\'environnement virtuel a été exporté dans le'
	  'fichier GEOSCAPE_VENV_PATH.')

if not platform.startswith('linux'):
	print('Pour l\'installation manuelle de TreeTagger sous Windows: allez dans le dossier'
		  'Treetagger, puis dans dans le dossier correspondant à votre version de Windows;'
		  'suivez les instructions du fichier INSTALL.')
	exit()
else:
	with context(join('Treetagger','TreeTagger_unix')):
		run(['./install-tagger.sh'],check=True)
	print('Installation de l\'étiqueteur TreeTagger réussie.')

print("""Installation de l'environnement virtuel pour Geoscape réussie. Veuillez placer le
répertoire Geoscape, Treetagger et les fichiers setup.py et praw.ini dans votre
répertoire serveur local. Assurez-vous d'avoir toutes les permissions nécessaires.
Depuis le répertoire serveur local, activez l'environnement virtuel avec la
commande '. <le chemin dans GEOSCAPE_VENV_PATH>'
Ensuite, installez le package avec la commande 'pip install -e .'
Puis indiquez le chemin à Flask avec la commande 
'export FLASK_APP=Geoscape/__init__.py'
Enfin lancez Geoscape avec la commande 'flask run'
La commande 'deactivate' désactive l'environnement virtuel.
""")
