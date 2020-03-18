#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from pymongo import MongoClient



"""Connexion à la base de données RedditScrape stockée sur MongoDB.
"""
client = MongoClient('mongodb+srv://scrapelord:dPSw8KCjKgF2fVp@redditscrape-bxkhv.'
					+'mongodb.net/test?retryWrites=true&w=majority').RedditScrape