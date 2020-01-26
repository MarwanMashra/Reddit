#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json, praw, re, requests

reddit=praw.Reddit(client_id="v7xiCUUDI3vEmg",client_secret="5Q6FHHJT-SW0YRnEmtWkekWsxHU",
password="Blorp86",user_agent="PhotoScraper",username="scrapelord")

target_sub=reddit.subreddit("EarthPorn")
country="France"
query="title:"+country
#print(target_sub.description)
print("\033[92m"+target_sub.display_name+"\033[0m"+"\nSearch results for submissions with: "+query+"\n")

test_posts=target_sub.search(query,limit=10)
for post in test_posts:
	if re.search(".*"+country+"[.,/[( ]",post.title): #Country followed by '.' ',' '/' '[' '(' or ' '
		res=re.search("^([^[(]+)",post.title) #Matches all characters from start, excluding [ and (
		if res:
			print(res.group(1))
			print(post.url) #Direct link to the submission picture!
			loc=re.search("(\S+)[, ]*"+country+"|(\S+) in "+country,res.group(1))
			if loc:
				if loc.group(1):
					location=loc.group(1)
				elif loc.group(2): #The second regex option will be placed in group(2)
					location=loc.group(2)
				if location[-1] in (',','"'):
					location=location[:-1]
				print(location)

				url="http://api.geonames.org/searchJSON"
				#username inserted into data
				data="?q="+location+"&country=FR&username=scrapelord"
				t=requests.get(url+data,auth=("scrapelord","Blorp86"))
				#'user account not enabled to use the free webservice. Please enable it on your account page: https://www.geonames.org/manageaccount'
				print(t.url)
				print(t.status_code) #200:OK, 401:unauthorized
				json_t=t.json()
				print(json_t,"\n") #json_t is a dictionary