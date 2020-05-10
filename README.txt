POUR INSTALLER:

Exécuter le script geoscape_installer.py dans le dossier où vous voulez installer le répertoire de
l'environnement virtuel Geoscape.

Suivez les instructions affichées à la fin du script:

Copiez ou deplacez les répertoires Geoscape et Treetagger ainsi que les fichiers setup.py et praw.ini
dans votre répertoire serveur local.

Assurez-vous d'avoir toutes les permissions nécessaires.

Depuis le répertoire serveur local, activez l'environnement virtuel avec la commande
'. <le chemin absolu écrit dans le fichier GEOSCAPE_VENV_PATH>'

Ensuite, installez le package Geoscape avec la commande 'pip install -e .'

Puis indiquez le chemin à Flask avec la commande
'export FLASK_APP=Geoscape/__init__.py' sous Linux
'set FLASK_APP=Geoscape/__init__.py' sous Windows

Enfin lancez Geoscape avec la commande 'flask run'

La commande 'deactivate' désactive l'environnement virtuel.

#########

Pour les tests GeoNames, exécuter le fichier geonames.py contenu dans le répertoire Geonames_test
depuis le répertoire contenant Geonames_test et Geoscape.
