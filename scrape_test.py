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

test_posts=target_sub.search(query,limit=15)
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
				print("Location identified: "+location)

				url="http://api.geonames.org/searchJSON"
				#username inserted into data
				data="?q="+location+"&country=FR&username=scrapelord"
				search_res=requests.get(url+data,auth=("scrapelord","Blorp86"))
				#print(search_res.url)
				print("GeoNames search request status:",search_res.status_code) #200:OK, 401:unauthorized
				search_res=search_res.json() #is a dictionary
				try:
					main_dict=search_res["geonames"][0] #Key referencing a list whose first item is a dictionary
				except IndexError:
					print("\033[91mNo records found in GeoNames database.\033[0m\n")
				else:
					#Inner dictionary keys
					print(main_dict["toponymName"],main_dict["lat"],main_dict["lng"],"\n") #Best (first) result, latitude and longitude