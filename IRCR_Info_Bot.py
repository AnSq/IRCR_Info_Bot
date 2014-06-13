#!/usr/bin/python


import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import string
import sys
import os
import urlparse
import traceback


# load settings
import config


def load_db_lib(pg):
    # load database lib
    if pg:
        try:
            global psycopg2
            import psycopg2
        except:
            print "Failed to load psycopg2 (Postgres library). Exiting."
            sys.exit()
    else:
        global sqlite3
        import sqlite3

    if pg:
        print "Using PostgreSQL"
    else:
        print "Using SQLite"


def db_connect(pg):
    # connect to database
    sql = None
    if pg:
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

    print "Connected to database"
    return sql


def load_db(sql):
    cur = sql.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
    sql.commit()
    return cur


def reddit_connect(useragent, multi):
    # connect to reddit
    handler = None
    if multi:
        handler = praw.handlers.MultiprocessHandler()
        print "Connecting to praw-multiprocess"
    else:
        handler = praw.handlers.DefaultHandler()
    r = praw.Reddit(useragent, handler=handler)
    return r


def login(r):
    testmode = False

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
        testmode = True

    return testmode


def setup():
    # startup info
    print config.USERAGENT

    # bot does not comment in testing mode
    testmode = False

    pg = False
    if "--postgres" in sys.argv or "-p" in sys.argv:
        pg = True
    load_db_lib(pg)

    sql = db_connect(pg)
    cur = load_db(sql)

    multi = False
    if "--multi" in sys.argv or "-m" in sys.argv:
        multi = True
    r = reddit_connect(config.USERAGENT, multi)


    # login
    if not "--nologin" in sys.argv and not "-n" in sys.argv:
        testmode |= login(r)
    else:
        print "Not logging in."
        testmode = True


    if "--test" in sys.argv or "-t" in sys.argv:
        testmode = True


    if testmode:
        print "Running in testing mode. Bot will not post comments."
    else:
        print "Running in live mode. Bot will post comments."

    return (r, sql, cur, pg, testmode)



def query(q, pg=False):
    # Stupid hack to get it to work with Postgres with minimal effort.
    # It only works because there's no non-text columns in the database.
    if pg:
        return q.replace("?", "%s")
    else:
        return q


def scanSub(r, sql, cur, pg, testmode):
    #list of characters which are allowed in usernames
    CHARS = string.digits + string.ascii_letters + '-_'

    #print 'Searching '+ config.SUBREDDIT + '.'
    subreddit = r.get_subreddit(config.SUBREDDIT)
    posts = subreddit.get_new(limit=config.MAXPOSTS)
    for post in posts:
        ptitle = post.title
        try:
            pauthor = post.author.name
        except AttributeError:
            pauthor = '[DELETED]'
        pid = post.id
        cur.execute(query('SELECT * FROM oldposts WHERE ID = ?', pg), (pid,))
        try:
            if not cur.fetchone():
                cur.execute(query('INSERT INTO oldposts VALUES (?)', pg), (pid,))
                print (u"\n\n| Found post \"%s\" (http://redd.it/%s) by /u/%s" % (ptitle, pid, pauthor)).encode("ascii", "backslashreplace")
                result = []
                if config.TRIGGERSTRING in ptitle:
                    ptitlesplit = ptitle.split(' ')
                    for word in ptitlesplit:
                        if config.TRIGGERSTRING in word:
                            word = word.replace(config.TRIGGERSTRING, '')
                            word = ''.join(c for c in word if c in CHARS)
                            finalword = config.TRIGGERSTRING + word
                            print "|\t" + finalword

                            try:
                                user = r.get_redditor(word, fetch=True)
                                finalword = finalword.replace(word, user.name)
                                finalword += config.NORMALSTRING.replace('_username_', word)
                            except Exception:
                                finalword += config.DEADUSER.replace('_username_', word)
                                print '|\t\tDead'

                            for name in config.SPECIALS.keys():
                                if name.lower() == word.lower():
                                    print '|\t\tSpecial'
                                    finalword += config.SPECIALS[name].replace('_username_', word)

                            result.append(finalword)
                if len(result) > 0:
                    final = config.HEADER + '\n\n- '.join(result) + config.FOOTER
                    if not testmode:
                        print '| Creating comment.'
                        newcomment = post.add_comment(final)
                        if config.DISTINGUISHCOMMENT == True:
                            print '| Distinguishing Comment.'
                            newcomment.distinguish()
                    else:
                        print "| Comment not created (bot is running in testing mode)."
                else:
                    print '| \tNo users mentioned in post title.'
        except:
            sql.rollback()
            raise
        finally:
            sql.commit()


def main(r, sql, cur, pg, testmode):
    while True:
        try:
            scanSub(r, sql, cur, pg, testmode)
        except Exception as e:
            print 'An error has occured:', str(e)
            traceback.print_exc()
        #print 'Running again in %d seconds' % config.WAIT
        sql.commit()
        time.sleep(config.WAIT)


if __name__ == "__main__":
    main(*setup())
