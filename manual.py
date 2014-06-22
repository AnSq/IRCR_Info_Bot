#!/usr/bin/python

import sys
import os
import cPickle

import IRCR_Info_Bot as ircr
import get_mod_list as gml

multi = len(sys.argv) > 1 and (sys.argv[1]=="-m" or sys.argv[1]=="--multi")
r = ircr.reddit_connect(ircr.config.USERAGENT + " (script-manual mode)", multi)

if not os.path.exists(gml.fname):
    gml.main(r)

f = open(gml.fname, "r")
mod_list = cPickle.load(f)
f.close()

title = ""
for name in sys.argv[2 if multi else 1:]:
    title += "/u/%s " % name

num, comment = ircr.title_to_comment(title, mod_list, r, False)

print "-------------------------------\n\n\n"
print comment
print
