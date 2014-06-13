#!/usr/bin/python


import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import string
import sys
import os
import urlparse
import traceback


# load settings
from config import *


# startup info
print USERAGENT


# bot does not comment in testing mode
TESTMODE = False


# load database lib
PG = False
if "--postgres" in sys.argv or "-p" in sys.argv:
    try:
        import psycopg2
        PG = True
    except:
        import sqlite3
        PG = False
else:
    import sqlite3

if PG:
    print "Using PostgreSQL"
else:
    print "Using SQLite"


#This is the list of characters which are allowed in usernames. Don't change this.
CHARS = string.digits + string.ascii_letters + '-_'


# connect to database
sql = None
if PG:
    # https://devcenter.heroku.com/articles/heroku-postgresql#connecting-in-python
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    sql = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
else:
    sql = sqlite3.connect('sql.db')

print 'Loaded SQL Database'
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
sql.commit()


# connect to reddit
handler = None
if "--multi" in sys.argv or "-m" in sys.argv:
    handler = praw.handlers.MultiprocessHandler()
    print "Connecting to praw-multiprocess"
else:
    handler = praw.handlers.DefaultHandler()
r = praw.Reddit(USERAGENT, handler=handler)


# login
if not "--nologin" in sys.argv and not "-n" in sys.argv:
    # attempt to load uname/pass from environment
    try:
        USERNAME = os.environ["IRCR_USERNAME"]
        PASSWORD = os.environ["IRCR_PASSWORD"]
    except:
        print "No username/password defined."
        sys.exit()

    try:
        r.login(USERNAME, PASSWORD)
        print "Logged in as /u/" + USERNAME
    except praw.errors.InvalidUserPass as e:
        print "Wrong password. Continuing in testing mode."
        TESTMODE = True
else:
    print "Not logging in."
    TESTMODE = True


if "--test" in sys.argv or "-t" in sys.argv:
    TESTMODE = True


if TESTMODE:
    print "Running in testing mode. Bot will not post comments."
else:
    print "Running in live mode. Bot will post comments."


def query(q):
    # Stupid hack to get it to work with Postgres with minimal effort.
    # It only works because there's no non-text columns in the database.
    if PG:
        return q.replace("?", "%s")
    else:
        return q


def scanSub():
    #print 'Searching '+ SUBREDDIT + '.'
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_new(limit=MAXPOSTS)
    for post in posts:
        ptitle = post.title
        try:
            pauthor = post.author.name
        except AttributeError:
            pauthor = '[DELETED]'
        pid = post.id
        cur.execute(query('SELECT * FROM oldposts WHERE ID = ?'), (pid,))
        if not cur.fetchone():
            cur.execute(query('INSERT INTO oldposts VALUES (?)'), (pid,))
            print "\n\n| Found post \"%s\" (http://redd.it/%s) by /u/%s" % (ptitle, pid, pauthor)
            result = []
            if TRIGGERSTRING in ptitle:
                ptitlesplit = ptitle.split(' ')
                for word in ptitlesplit:
                    if TRIGGERSTRING in word:
                        word = word.replace(TRIGGERSTRING, '')
                        word = ''.join(c for c in word if c in CHARS)
                        finalword = TRIGGERSTRING + word
                        print "|\t" + finalword

                        try:
                            user = r.get_redditor(word, fetch=True)
                            finalword = finalword.replace(word, user.name)
                            finalword += NORMALSTRING.replace('_username_', word)
                        except Exception:
                            finalword += DEADUSER.replace('_username_', word)
                            print '|\t\tDead'

                        for name in SPECIALS.keys():
                            if name.lower() == word.lower():
                                print '|\t\tSpecial'
                                finalword += SPECIALS[name].replace('_username_', word)

                        result.append(finalword)
            if len(result) > 0:
                final = HEADER + '\n\n- '.join(result) + FOOTER
                if not TESTMODE:
                    print '| Creating comment.'
                    newcomment = post.add_comment(final)
                    if DISTINGUISHCOMMENT == True:
                        print '| Distinguishing Comment.'
                        newcomment.distinguish()
                else:
                    print "| Comment not created (bot is running in testing mode)."
            else:
                print '| \tNo users mentioned in post title.'
        sql.commit()


while True:
    try:
        scanSub()
    except Exception as e:
        print 'An error has occured:', str(e)
        traceback.print_exc()
    #print 'Running again in %d seconds' % WAIT
    sql.commit()
    time.sleep(WAIT)
