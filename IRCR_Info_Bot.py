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
    """load correct database library"""
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
    """connect to the database"""
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
    """initialize the database and return a cursor"""
    cur = sql.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
    sql.commit()
    return cur


def reddit_connect(useragent, multi):
    """connect to reddit"""
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
    """log in to reddit"""

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


def load_mod_list(subs, r=praw.Reddit(config.USERAGENT + " (manual mode)")):
    """returns a map of name to list of subreddits of moderators of the given subs.
    default reddit instance provided for convenience in terminal. Don't use it in scripts."""

    mod_list = {}
    for sub in subs:
        ml = None
        while True:
            try:
                ml = r.get_subreddit(sub).get_moderators()
                break
            except HTTPError as e:
                if str(e)[:3] == "504":
                    continue
                else:
                    raise

        mods = [u.name for u in ml]
        for name in mods:
            if name in mod_list:
                mod_list[name].append(sub)
            else:
                mod_list[name] = [sub]

    mod_list = {k.lower():v for k,v in mod_list.items()} #lowercase for easy lookup
    return mod_list


def setup():
    """initialize program"""

    # startup info
    print config.USERAGENT

    # lowercase all usernams for easy lookup
    config.SPECIALS = {k.lower():v for k,v in config.SPECIALS.items()}

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

    mod_list = load_mod_list(config.SPECIAL_MOD_SUBS, r)

    if "--test" in sys.argv or "-t" in sys.argv:
        testmode = True


    if testmode:
        print "Running in testing mode. Bot will not post comments."
    else:
        print "Running in live mode. Bot will post comments."

    return (r, sql, cur, pg, testmode, mod_list)


def query(q, pg=False):
    """Stupid hack to get it to work with Postgres with minimal effort."""
    if pg:
        return q.replace("?", "%s")
    else:
        return q


def make_sublist(subs):
    if len(subs) == 1:
        return "/r/%s" % subs[0]

    if len(subs) == 2:
        return "/r/%s and /r/%s" % (subs[0], subs[1])

    result = ""
    for i in range(0, len(subs)):
        if i < len(subs)-1:
            result += "/r/%s, " % subs[i]
        else:
            result += "and /r/%s" % subs[i]
    return result


def make_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False):
    """Generate remark for a user.
    default reddit instance provided for convenience in terminal. Don't use it in scripts."""

    info = config.TRIGGERSTRING + username
    if p: print "|\t" + info

    while True:
        try:
            user = r.get_redditor(username, fetch=True)
            info = info.replace(username, user.name) # standardize capitalization
            info += config.NORMALSTRING.replace('_username_', username)
            break
        except Exception as e:
            if type(e).__name__ == "HTTPError" and str(e)[:3] == "404":
                # A 404 error means the user was deleted or banned
                info += config.DEADUSER.replace('_username_', username)
                if p: print '|\t\tDead'
                break
            else:
                # Any other error (notably a 504) means we should try again to get the user
                print "Error getting user: %s: %s" % (type(e).__name__, str(e))
                time.sleep(2)
                continue

    if username.lower() in config.SPECIALS:
        if p: print '|\t\tSpecial'
        info += config.SPECIALS[username.lower()].replace('_username_', username)

    if username.lower() in mod_list:
        name = username.lower()
        subs = mod_list[name]
        if p: print "|\t\tMod " + str(subs)
        info += config.MOD_REMARK.replace("_sublist_", make_sublist(subs))

    return info


def scan_title(title):
    """extract a set of usernames from a string"""
    users = set()
    CHARS = string.digits + string.ascii_letters + '-_'
    index = title.find(config.TRIGGERSTRING)
    while index != -1:
        start = index + len(config.TRIGGERSTRING)
        end = start

        if end < len(title):
            while title[end] in CHARS:
                end += 1

            users.add(title[start:end])

        title = title[start:]
        index = title.find(config.TRIGGERSTRING)
    return users


def make_comment(remarks):
    """generate a complete comment from a collection of remarks"""
    return config.HEADER + '\n\n- '.join(remarks) + config.FOOTER


def title_to_comment(ptitle, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False):
    """generate a comment from a post title"""
    # default reddit instance provided for convenience in terminal. Don't use it in scripts.

    names = [n.lower() for n in scan_title(ptitle)]
    names.sort()

    remarks = []
    for name in names:
        remarks.append(make_info(name, mod_list, r, p))

    num_names = len(names)
    comment = make_comment(remarks)

    return (num_names, comment)


def post_comment(post, comment, sql, testmode=False):
    """submit a comment on a post"""
    if not testmode:
        print "| Posting comment..."
        newcomment = post.add_comment(comment)
        sql.commit()
        print '| Comment posted. (http://reddit.com/comments/%s/-/%s)' % (newcomment.link_id[3:], newcomment.id)
        if config.DISTINGUISHCOMMENT:
            newcomment.distinguish()
            print '| Comment distinguished.'
    else:
        print "| Comment not posted (bot is running in testing mode)."
    print


def scanSub(r, sql, cur, pg, testmode, mod_list):
    """scan post titles and post comments"""

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
            pauthor = '[deleted]'
        pid = post.id
        cur.execute(query('SELECT * FROM oldposts WHERE ID = ?', pg), (pid,))
        try:
            if not cur.fetchone():
                cur.execute(query('INSERT INTO oldposts VALUES (?)', pg), (pid,))
                print (u"\n| Found post \"%s\" (http://redd.it/%s) by /u/%s" % (ptitle, pid, pauthor)).encode("ascii", "backslashreplace")

                num_names, comment = title_to_comment(ptitle, mod_list, r, True)

                if num_names > 0:
                    post_comment(post, comment, sql, testmode)
                else:
                    print '| \tNo users mentioned in post title.\n'
        except:
            sql.rollback()
            raise
        finally:
            sql.commit()


def main(r, sql, cur, pg, testmode, mod_list):
    """continuously scan and post comments"""
    while True:
        try:
            scanSub(r, sql, cur, pg, testmode, mod_list)
        except Exception as e:
            print '\n*** ERROR: %s: %s' % (type(e).__name__, str(e))
            if not (type(e).__name__ == "HTTPError" and str(e)[:3] == "504"):
                # It gets so many 504s on Heroku and I don't want to hear about it.
                print "--------------------------------"
                traceback.print_exc()
                print "--------------------------------\n"
        #print 'Running again in %d seconds' % config.WAIT
        sql.commit()
        time.sleep(config.WAIT)


if __name__ == "__main__":
    main(*setup())
