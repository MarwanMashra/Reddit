#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from setuptools import setup

setup(
	name='Geoscape',
	version='1.00',
	author='redditScrape Team',
	packages=['Geoscape'],
	include_package_data=True,
	install_requires=['flask','pymongo','praw','geocoder']
	)