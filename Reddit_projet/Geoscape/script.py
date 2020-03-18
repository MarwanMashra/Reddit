#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from Geoscape import app
import Geoscape.mongo as mongo
import json, sys, bcrypt, urllib
from flask import Flask, render_template, request, jsonify, redirect, session, url_for



"""A partir de l'inscription d'un utilisateur en tant qu'admin, la fonction crée
un profil testeur pour cet utilisateur dans la collection 'Testeurs' de la base
de données. Chaque testeur reçoit un code unique qui sert à identifier les documents
de 'Resultats_RGN' qu'il/elle doit tester.
"""
def db_tester(username):
	dbloader = mongo.MongoSave([])
	next_code = 0

	if dbloader.mongocheck('Testeurs'):
		next_code = dbloader.mongocount('Testeurs')
	dbloader.reinit([{'user_id': username, 'code': next_code, 'num_answers': 0}])
	dbloader.storeindb('Testeurs',user_id='A')
	print('Profil testeur créé.')



app.secret_key='mysecret'

@app.route('/')
@app.route('/map')
@app.route('/map.html')
def map():
	if 'username' in session:
		return render_template('map.html',username=session['username'])
	return render_template('map.html')



@app.route('/connexion',methods=['GET','POST'])
@app.route('/connexion.html',methods=['GET','POST'])
def connexion():
	if request.method == 'POST':
		pseudo_email = request.form['pseudo_email']
		password = request.form['password']
		
		#Chercher le compte en supposant que c'est le pseudo
		compte = mongo.MongoLoad({'pseudo': pseudo_email}).retrieve('users_accounts',limit=1)

		#Si compte pas trouvé, chercher le compte en supposant que c'est le mail
		if not compte:
			compte = mongo.MongoLoad({'email': pseudo_email}).retrieve('users_accounts',limit=1)

		#Si compte trouvé	
		if compte:
			compte = compte[0]
			#Vérifier le mot de passe checkpw(password, hashed)
			if bcrypt.hashpw(password.encode('utf-8'),compte['password']) == compte['password']:

				#Cookies
				session['username'] = compte['pseudo']
				session['admin?'] = ( compte['admin?'] == "YES" )
				if (session['admin?']):
					return redirect(url_for('testeur'))  
				else:
					return redirect(url_for('map'))
					
		#Pseudo,email ou mot de passe invalide
		error = 'Le pseudo/email ou le mot de passe n\'est pas valide'
		return render_template('connexion.html',error=error)
			
	elif 'username' in session:
		if session['admin?']:
			return redirect(url_for('testeur'))  
		else:
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

		existing_name = mongo.MongoLoad({'pseudo': pseudo}).retrieve('users_accounts',limit=1)
		existing_mail = mongo.MongoLoad({'email': email}).retrieve('users_accounts',limit=1)

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

			if (session['admin?']):
				#Appel de la fonction qui crée le compte admin
				return redirect(url_for('testeur')) 
			else:
				return redirect(url_for('map'))  

		return render_template('inscription.html',error=error)

	elif 'username' in session:
		if session['admin?']:
			return redirect(url_for('testeur'))  
		else:
			return redirect(url_for('map'))

	else:
		return render_template('inscription.html')



@app.route('/deconnexion')
def deconnexion():
	session.clear()
	return redirect(url_for('connexion'))



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

