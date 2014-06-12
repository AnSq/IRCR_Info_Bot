#!/usr/bin/python

import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import sqlite3
import string
import sys

# bot does not comment in testing mode
TESTMODE = False

# load settings
from config import *

#This is the list of characters which are allowed in usernames. Don't change this.
CHARS = string.digits + string.ascii_letters + '-_'

sql = sqlite3.connect('sql.db')
print('Loaded SQL Database')
cur = sql.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
print('Loaded Completed table')

sql.commit()

# connect to reddit
handler = None
if "--multi" in sys.argv or "-m" in sys.argv:
    handler = praw.handlers.MultiprocessHandler()
    print("Connecting to praw-multiprocess")
else:
    handler = praw.handlers.DefaultHandler()
r = praw.Reddit(USERAGENT, handler=handler)

# login
try:
    r.login(USERNAME, PASSWORD)
except praw.errors.InvalidUserPass as e:
    print("Wrong password.")
    cont = "..."
    while len(cont) != 0 and cont[0].lower() not in "yn":
        cont = raw_input("Continue in testing mode? [Y/n]: ")
    if cont == "n":
        sys.exit()
    else:
        TESTMODE = True

if "--test" in sys.argv or "-t" in sys.argv:
    TESTMODE = True

if TESTMODE:
    print("Running in testing mode. Bot will not post comments.")

def scanSub():
    print('Searching '+ SUBREDDIT + '.')
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_new(limit=MAXPOSTS)
    for post in posts:
        ptitle = post.title
        try:
            pauthor = post.author.name
        except AttributeError:
            pauthor = '[DELETED]'
        pid = post.id
        cur.execute('SELECT * FROM oldposts WHERE ID == ?', (pid,))
        if not cur.fetchone():
            cur.execute('INSERT INTO oldposts VALUES (?)', (pid,))
            print(pid)
            result = []
            if TRIGGERSTRING in ptitle:
                ptitlesplit = ptitle.split(' ')
                for word in ptitlesplit:
                    if TRIGGERSTRING in word:
                        print(word)
                        word = word.replace(TRIGGERSTRING, '')
                        word = ''.join(c for c in word if c in CHARS)
                        finalword = TRIGGERSTRING + word

                        try:
                            user = r.get_redditor(word, fetch=True)
                            finalword = finalword.replace(word, user.name)
                            finalword += NORMALSTRING.replace('_username_', word)
                        except Exception:
                            finalword += DEADUSER.replace('_username_', word)
                            print('\tDead')

                        for name in SPECIALS.keys():
                            if name.lower() == word.lower():
                                print('\tSpecial')
                                finalword += SPECIALS[name].replace('_username_', word)

                        result.append(finalword)
            if len(result) > 0:
                final = HEADER + '\n\n- '.join(result) + FOOTER
                if not TESTMODE:
                    print('Creating comment.')
                    newcomment = post.add_comment(final)
                    if DISTINGUISHCOMMENT == True:
                        print('Distinguishing Comment.')
                        newcomment.distinguish()
                else:
                    print("Comment not created (bot is running in testing mode).")
            else:
                print('\tNone!')
        sql.commit()


while True:
    try:
        scanSub()
    except Exception as e:
        print('An error has occured:', str(e))
    print('Running again in %d seconds \n' % WAIT)
    sql.commit()
    time.sleep(WAIT)
