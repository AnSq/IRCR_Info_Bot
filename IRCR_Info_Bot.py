#!/usr/bin/python


import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import string
import sys
import os
import urlparse
import traceback
#import cPickle


# load settings
import config


class DatabaseAccess (object):
    def __init__(self, pg):
        self.pg = pg
        self.load_db_lib()
        self.db_connect()
        self.load_db()


    def load_db_lib(self):
        """load correct database library"""
        if self.pg:
            try:
                import psycopg2
                self.psycopg2 = psycopg2
            except:
                print "Failed to load psycopg2 (Postgres library). Exiting."
                sys.exit()
        else:
            import sqlite3
            self.sqlite3 = sqlite3

        if self.pg:
            print "Using PostgreSQL"
        else:
            print "Using SQLite"


    def db_connect(self):
        """connect to the database"""
        self.conn = None
        if self.pg:
            # see https://devcenter.heroku.com/articles/heroku-postgresql#connecting-in-python
            urlparse.uses_netloc.append("postgres")
            url = urlparse.urlparse(os.environ["DATABASE_URL"])

            self.conn = self.psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
        else:
            self.conn = self.sqlite3.connect('sql.db')

        print "Connected to database"
        return self.conn


    def load_db(self):
        """initialize the database and return a cursor"""
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS oldposts(ID TEXT);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS users(name TEXT UNIQUE, mentions INT);")
        self.conn.commit()
        return self.cur


    def query(self, q):
        """Stupid hack to get it to work with Postgres with minimal effort."""
        if self.pg:
            return q.replace("?", "%s")
        else:
            return q


    def get_mentions(self, username):
        prevcount = 0
        self.cur.execute(self.query("SELECT mentions FROM users WHERE name = ?"), (username,))
        result = self.cur.fetchone()
        if result:
            prevcount = result[0]
        return prevcount


    def get_alias_mentions(self, alias_list):
        self.cur.execute(self.query("SELECT sum(mentions) FROM users WHERE " + ("name=? OR "*len(alias_list))[:-4]), alias_list)
        result = self.cur.fetchone()
        prevcount = 0
        if result and len(result) > 0 and result[0]:
            prevcount = result[0]
        return prevcount


    def increment_names(self, names):
        """increment the 'mentioned' value for all the given names"""
        for name in names:
            self.cur.execute(self.query("SELECT * FROM users WHERE name = ?"), (name,))
            if not self.cur.fetchone():
                self.cur.execute(self.query("INSERT INTO users (name, mentions) VALUES (?,?)"), (name, 1))
            else:
                self.cur.execute(self.query("UPDATE users SET mentions = mentions + 1 WHERE name = ?"), (name,))


    def commit(self):
        self.conn.commit()


    def rollback(self):
        self.conn.rollback()


    def is_oldpost(self, post_id):
        self.cur.execute(self.query("SELECT * FROM oldposts WHERE ID = ?"), (post_id,))
        return bool(cur.fetchone())


    def add_oldpost(self, post_id):
        self.cur.execute(self.query("INSERT INTO oldposts VALUES (?)"), (post_id,))



def reddit_connect(useragent, multi=False):
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


def load_mod_list(subs, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False):
    """returns a map of name to list of subreddits of moderators of the given subs.
    default reddit instance provided for convenience in terminal. Don't use it in scripts."""

    if p: print "Loading moderators of %d subreddits:" % len(subs)

    #f = open("mod_list_cache.pickle", "r")
    #mod_list = cPickle.load(f)
    #f.close()
    #return mod_list

    mod_list = {}
    i = 1
    for sub in subs:
        if p: print "\t%s: /r/%s" % (str(i).rjust(2), sub)
        ml = None
        while True:
            try:
                ml = r.get_subreddit(sub).get_moderators()
                break
            except praw.requests.exceptions.HTTPError as e:
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


        i += 1

    mod_list = {k.lower():v for k,v in mod_list.items()} #lowercase for easy lookup
    return mod_list


def setup():
    """initialize program"""

    # startup info
    print config.USERAGENT

    # lowercase all usernams for easy lookup
    config.SPECIALS = {k.lower():v for k,v in config.SPECIALS.items()}
    config.ALIASES = [[name.lower() for name in person] for person in config.ALIASES]

    # bot does not comment in testing mode
    testmode = False

    pg = False
    if "--postgres" in sys.argv or "-p" in sys.argv:
        pg = True
    db = DatabaseAccess(pg)

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

    mod_list = load_mod_list(config.SPECIAL_MOD_SUBS, r, True)

    if "--test" in sys.argv or "-t" in sys.argv:
        testmode = True


    if testmode:
        print "Running in testing mode. Bot will not post comments."
    else:
        print "Running in live mode. Bot will post comments."

    return (r, db, pg, testmode, mod_list)


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


def get_alias_list(name):
    """return a list of names the given name also goes by"""
    # haha, yes! See https://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    return [n for p in filter(lambda person: name in person, config.ALIASES) for n in p]


def normalize_name(name):
    """returns the "normal" name if the given name is an alias"""
    alias_list = get_alias_list(name)
    if len(alias_list) > 0:
        return alias_list[0]
    else:
        return name


def make_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    """Generate remark for a user.
    default reddit instance provided for convenience in terminal. Don't use it in scripts."""

    args = (username, mod_list, r, p, db, pg)

    info = make_normal_info(*args)
    info += make_alias_info(*args)
    info += make_special_info(*args)
    info += make_mod_info(*args)

    return info


def make_normal_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    info = config.TRIGGERSTRING + username
    if p: print "|\t" + info

    while True:
        try:
            user = r.get_redditor(username, fetch=True)
            info = info.replace(username, user.name) # standardize capitalization
            info += config.NORMALSTRING.replace('$username$', username)
            break
        except Exception as e:
            if type(e).__name__ == "HTTPError" and str(e)[:3] == "404":
                # A 404 error means the user was deleted or banned
                info += config.DEADUSER.replace('$username$', username)
                if p: print '|\t\tDead'
                break
            else:
                # Any other error (notably a 504) means we should try again to get the user
                print "Error getting user: %s: %s" % (type(e).__name__, str(e))
                time.sleep(2)
                continue

    prevcount = 0
    if db:
        prevcount = db.get_mentions(username)
    info = info.replace("$prevcount$", str(prevcount))
    if p: print "|\t\t%d previous mentions" % prevcount

    return info


def make_alias_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    info = ""
    alias_list = get_alias_list(username.lower())
    if len(alias_list) > 0:
        if p: print "|\t\tAlias"

        prevcount = 0
        if db:
            prevcount = db.get_alias_mentions(alias_list)

        if p: print "|\t\t%d previous alias mentions" % prevcount
        searchquery = make_searchquery(alias_list)
        info += config.ALIAS_REMARK.replace("$searchquery$", searchquery).replace("$prevcount$", str(prevcount))
    return info


def make_special_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    info = ""
    normal = normalize_name(username.lower())
    if normal in config.SPECIALS:
        if p: print '|\t\tSpecial'
        info += config.SPECIALS[normal].replace('$username$', normal)
    return info


def make_mod_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    info = ""
    if username.lower() in mod_list:
        name = username.lower()
        subs = mod_list[name]
        if p: print "|\t\tMod " + str(subs)
        info += config.MOD_REMARK.replace("$sublist$", make_sublist(subs))
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
            while end < len(title) and title[end] in CHARS:
                end += 1

            users.add(title[start:end])

        title = title[start:]
        index = title.find(config.TRIGGERSTRING)
    return users


def make_comment(remarks):
    """generate a complete comment from a collection of remarks"""
    return config.HEADER + '\n\n- '.join(remarks) + config.FOOTER


def title_to_comment(ptitle, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    """generate a comment from a post title"""
    # default reddit instance provided for convenience in terminal. Don't use it in scripts.

    names = [n.lower() for n in scan_title(ptitle)]
    names.sort()

    remarks = []
    for name in names:
        remarks.append(make_info(name, mod_list, r, p, db, pg))

    comment = make_comment(remarks)

    return (comment, names)


def post_comment(post, comment, db, testmode=False):
    """submit a comment on a post"""
    if not testmode:
        print "| Posting comment..."
        newcomment = post.add_comment(comment)
        db.commit()
        print "| Comment posted. (http://reddit.com/comments/%s/-/%s)" % (newcomment.link_id[3:], newcomment.id)
        if config.DISTINGUISHCOMMENT:
            newcomment.distinguish()
            print "| Comment distinguished."
    else:
        print "| Comment not posted (bot is running in testing mode)."
    print


def make_searchquery(names):
    """construct a search query for all the given names"""
    q = ""
    for name in names:
        q += "$username$+OR+flair%3A%27$username$%27+OR+".replace("$username$", name)
    return q[:-4] # chop off final "+OR+"


def scanSub(r, db, pg, testmode, mod_list):
    """scan post titles and post comments"""

    subreddit = r.get_subreddit(config.SUBREDDIT)
    posts = subreddit.get_new(limit=config.MAXPOSTS)
    for post in posts:
        ptitle = "%s %s" % (post.link_flair_text, post.title)
        try:
            pauthor = post.author.name
        except AttributeError:
            pauthor = "[deleted]"
        pid = post.id
        try:
            if not db.is_oldpost(pid):
                db.add_oldpost(pid)

                data = (post.link_flair_text, post.title, pid, pauthor)
                found_string = u"\n| Found post [%s] \"%s\" (http://redd.it/%s) by /u/%s" % data
                print found_string.encode("ascii", "backslashreplace")

                comment, names = title_to_comment(ptitle, mod_list, r, True, db, pg)

                db.increment_names(names)

                if len(names) > 0:
                    post_comment(post, comment, db, testmode)
                else:
                    print "|\tNo users mentioned in post title.\n"
        except:
            db.rollback()
            raise
        finally:
            db.commit()


def main(r, db, pg, testmode, mod_list):
    """continuously scan and post comments"""
    while True:
        try:
            scanSub(r, db, pg, testmode, mod_list)
        except Exception as e:
            print "\n*** ERROR: %s: %s" % (type(e).__name__, str(e))
            if not (type(e).__name__ == "HTTPError" and str(e)[:3] == "504"):
                # It gets so many 504s on Heroku and I don't want to hear about it.
                print "--------------------------------"
                traceback.print_exc()
                print "--------------------------------\n"
        sql.commit()
        time.sleep(config.WAIT)


if __name__ == "__main__":
    main(*setup())
