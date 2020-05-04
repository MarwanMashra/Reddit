#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from Geoscape import app
import json, sys, bcrypt, urllib
import Geoscape.mongo as mongo
from flask import Flask, render_template, request, jsonify, redirect, session, url_for



def db_tester(username):
	"""A partir de l'inscription d'un utilisateur en tant qu'admin, la fonction crée
	un profil testeur pour cet utilisateur dans la collection 'Testeurs' de la base
	de données. Chaque testeur reçoit un code unique qui sert à identifier les documents
	de 'Resultats_RGN' qu'il/elle doit tester.
	"""

	next_code = 0
	if mongo.Mongo.mongocheck('Testeurs'):
		next_code = mongo.Mongo.mongocount('Testeurs')

	dbloader = mongo.MongoSave([{'user_id': username, 'code': next_code, 'num_answers': 0}])
	dbloader.storeindb('Testeurs',user_id='A')
	print('Profil testeur créé.')



@app.route('/')
@app.route('/map')
@app.route('/map.html')
def map():
	return render_template('map.html')



@app.route('/connexion',methods=['GET','POST'])
@app.route('/connexion.html',methods=['GET','POST'])
def connexion():
	if request.method == 'POST':
		pseudo_email = request.form['pseudo_email']
		password = request.form['password']
		
		#Chercher le compte en supposant que c'est le pseudo
		cmpt = mongo.MongoLoad({'pseudo': pseudo_email})
		compte = list(cmpt.retrieve('users_accounts',limit=1))

		#Si compte pas trouvé, chercher le compte en supposant que c'est le mail
		if not compte:
			cmpt.reinit({'email': pseudo_email})
			compte = list(cmpt.retrieve('users_accounts',limit=1))

		#Si compte trouvé	
		if compte:
			compte = compte[0]
			#Vérifier le mot de passe checkpw(password, hashed)
			if bcrypt.hashpw(password.encode('utf-8'),compte['password']) == compte['password']:

				#Cookies
				session['username'] = compte['pseudo']
				session['admin?'] = ( compte['admin?'] == "YES" )
				return redirect(url_for('map'))
					
		#Pseudo,email ou mot de passe invalide
		error = 'Le pseudo/email ou le mot de passe n\'est pas valide'
		return render_template('connexion.html',error=error)
			
	elif 'username' in session:
		return redirect(url_for('map'))
	
	else:
		return render_template('connexion.html')



@app.route('/inscription.html',methods=['GET','POST'])
@app.route('/inscription',methods=['GET','POST'])
def inscription():	
	if request.method == 'POST':
		pseudo = request.form['pseudo']
		email = request.form['email']
		password = request.form['password']
		password_confirmation = request.form['password_confirmation']
		is_admin = ('admin' in request.form)

		existing_name = list(mongo.MongoLoad({'pseudo': pseudo}).retrieve('users_accounts'))
		existing_mail = list(mongo.MongoLoad({'email': email}).retrieve('users_accounts'))

		if existing_name:
			error = 'Ce pseudo est déjà utilisé, veuillez en choisir un autre.'
		elif existing_mail:
			error = 'Cette adresse mail est déjà utilisée, veuillez vous-connectez.'
		elif password != password_confirmation:
			error = 'Les deux mots de passes sont différents.'

		else:
			#Cookies
			session['username'] = pseudo
			session['admin?'] = is_admin   

			#Cryptage du mot de passe
			hashpass= bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
			
			#Stockage dans mongoDB
			dic = {
					'pseudo': pseudo,
					'email': email,
					'password': hashpass
				  }
			if session['admin?']:
				dic['admin?'] = 'YES'
				db_tester(session['username']) #Création d'un profil testeur
			else:
				dic['admin?'] = 'NO'
			documents = mongo.MongoSave([dic])
			documents.storeindb('users_accounts',pseudo='A',email='A')

			#redirection vers la map
			return redirect(url_for('map'))  

		return render_template('inscription.html',error=error)

	elif 'username' in session:
		return redirect(url_for('map'))

	else:
		return render_template('inscription.html')



@app.route('/deconnexion')
def deconnexion():
	session.clear()
	return redirect(url_for('connexion'))


@app.route('/get_session',methods=['GET'])
def get_session():
	
	dic={}

	if session:
		dic={
			'username':session['username'],
			'admin?':session['admin?']
		}	

	return dic


@app.route('/test')
@app.route('/test.html')
def test():
	return render_template('test-expert.html')



@app.route('/testeur')
@app.route('/testeur.html')
def testeur():
	if ('admin?' in session) and (session['admin?']) :
		return render_template('testeur.html')
	return redirect(url_for('connexion'))

