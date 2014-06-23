#!/usr/bin/python

"""This is a script for fetching and saving information (id, title, flair) about
all posts on /r/isrconspiracyracist and users mentioned in titles and flairs."""

import sys
import os
import cPickle

import IRCR_Info_Bot as ircr
import get_mod_list as gml

multi = len(sys.argv) > 1 and (sys.argv[1]=="-m" or sys.argv[1]=="--multi")
r = ircr.reddit_connect(ircr.config.USERAGENT + " (script-manual mode)", multi)

alltitles = []
for post in r.get_subreddit("isrconspiracyracist").get_new(limit=None):
	alltitles.append((post.id, post.title, post.link_flair_text))

print "\n%d posts" % len(alltitles)

f = open("alltitles.pickle", "w")
cPickle.dump(alltitles, f)
f.close()

users = {}

for post in alltitles:
	title = " %s %s " % (post[1], post[2])
	names = [n.lower() for n in ircr.scan_title(title)]
	for name in names:
		if name in users:
			users[name] += 1
		else:
			users[name] = 1

f = open("usercounts.pickle",  "w")
cPickle.dump(users, f)
f.close()

for u in users:
	print "%s %d" % (u, users[u])

print "%d users" % len(users)
