#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from flask import Flask

#On importe ces fichiers pour enregistrer leurs @....routes()
from Geoscape.scraper import rgn
from Geoscape.database import mdb

app = Flask(__name__)

if __name__ == '__main__' :
	app.run(debug=True,port=5000)

app.register_blueprint(rgn)
app.register_blueprint(mdb)

import Geoscape.script
import Geoscape.scraper
import Geoscape.database