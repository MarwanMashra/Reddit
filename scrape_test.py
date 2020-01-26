#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import praw, re

reddit=praw.Reddit(client_id="v7xiCUUDI3vEmg",client_secret="5Q6FHHJT-SW0YRnEmtWkekWsxHU",
password="Blorp86",user_agent="PhotoScraper",username="scrapelord")

target_sub=reddit.subreddit("EarthPorn")
#print(target_sub.description)
print(target_sub.display_name+"\n")

test_posts=reddit.subreddit("EarthPorn").search("title:France",limit=10)
for post in test_posts:
	if re.search(".*France[.,/ ]",post.title): #France followed by '.' ',' '/' or ' '
		res=re.search("^([^[(]+)",post.title) #Matches all characters from start, excluding [ and (
		if res:
			print(res.group(1))
			print(post.url+"\n")