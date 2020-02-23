le dossier Reddit_projet contient le script python (qui utilise flask) ainsi qu'un dossier templates qui contient les fichier html, css et js.

/////// Point importants: ///////
# l'existence du dossier templates est indispensable pour le fonctionnement de flask, merci de ne pas modifier le nom de dossier.
# il faut impérativement télécharger les fichiers nécessiares pour le treetagger et les placer un dossier TreeTagger à côté du script python. 
# il faut posséder un serveur local dans lequel vous placerez tous les ficheirs du projet
# veuillez vous assurez que le chemin vers les fichiers css et js est correct dans le head du fichier html.
# le chemin prévu pour les fichiers est le suivant:

>localhost
>>script.py
>>TreeTagger
>>templates
>>>map.html
>>>map.css
>>>map.js
>>>pays.js


après avoir vérifié les points précédents, vous pouvez tester en allant sur votre navigateur et en écrivant :
localhost:5000
