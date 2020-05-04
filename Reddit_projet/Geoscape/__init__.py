#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
from os import getcwd

from flask import Flask

#On importe ces fichiers pour enregistrer leurs @....routes()
from Geoscape.scraper import rgn
from Geoscape.database import mdb



app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='mysecret')

with open(getcwd()+'/Geoscape/geoscape.ini','r') as initfile:
	f = initfile.readlines()

for line in f:
	if line.startswith('key='):
		app.config['GEOKEY'] = line[4:].strip() #Majuscules requises pour app.config
	if line.startswith('auth='):
		app.config['GEOAUTH'] = line[5:].strip()

if not all(key in app.config for key in ['GEOKEY','GEOAUTH']):
	sys.exit('Erreur à l\'initialisation: les codes d\'accès pour geonames ne sont '
			 'pas présents. Complétez votre fichier de configuration.')

app.register_blueprint(rgn)
app.register_blueprint(mdb)

if __name__ == '__main__' :
	app.run(debug=True,port=5000)

import Geoscape.script