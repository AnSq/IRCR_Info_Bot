#!/usr/bin/python


import praw
import OAuth2Util
import time
import string
import sys
import os
import urlparse
import traceback
import cPickle
import threading


# load settings
import config


# undocumented feature: use --ircr flag to switch to scanning /r/ircr
if "--ircr" in sys.argv:
    config.SUBREDDIT = "ircr"
    config.WAIT = 5
    config.SQLITE_FILE = "ircr_testing.sqlite"


class DatabaseAccess (object):
    """contains all methods for accessing the database"""

    def __init__(self, pg):
        """load and connect to the database"""
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
            self.conn = self.sqlite3.connect(config.SQLITE_FILE)

        print "Connected to database"
        return self.conn


    def load_db(self):
        """initialize the database and return a cursor"""
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS oldposts(ID TEXT);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS users(name TEXT UNIQUE, mentions INT);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS oldcomments(ID TEXT);")
        self.conn.commit()
        return self.cur


    def query(self, q):
        """Stupid hack to get it to work with Postgres with minimal effort."""
        if self.pg:
            return q.replace("?", "%s")
        else:
            return q


    def get_mentions(self, username):
        """get number of previous mentions of a username"""
        prevcount = 0
        self.cur.execute(self.query("SELECT mentions FROM users WHERE name = ?"), (username,))
        result = self.cur.fetchone()
        if result:
            prevcount = result[0]
        return prevcount


    def get_alias_mentions(self, alias_list):
        """get combined number of previous mentions for a list of aliases"""
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
        """commit all database changes"""
        self.conn.commit()


    def rollback(self):
        """undo pending database changes"""
        self.conn.rollback()


    def is_oldpost(self, post_id):
        """checks if a post is already in the database"""
        self.cur.execute(self.query("SELECT * FROM oldposts WHERE ID = ?"), (post_id,))
        return bool(self.cur.fetchone())


    def is_oldcomment(self, comment_id):
        """checks if a comment is already in the database"""
        self.cur.execute(self.query("SELECT * FROM oldcomments WHERE ID = ?"), (comment_id,))
        return bool(self.cur.fetchone())


    def add_oldpost(self, post_id):
        """add a post to the database"""
        self.cur.execute(self.query("INSERT INTO oldposts VALUES (?)"), (post_id,))


    def add_oldcomment(self, comment_id):
        """add a post to the database"""
        self.cur.execute(self.query("INSERT INTO oldcomments VALUES (?)"), (comment_id,))



def print_exception(e):
    http504 = (type(e).__name__ == "HTTPError" and str(e)[:3] == "504") # It gets so many 504s on Heroku and I don't want to hear about it.

    if not http504:
        print "\n--------------------------------"

    print "*** ERROR: %s: %s" % (type(e).__name__, str(e))

    if not http504:
        traceback.print_exc()
        print "--------------------------------\n"


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


def login(r, configfile="oauth.ini"):
    """log in to reddit"""

    try:
        oauth = OAuth2Util.OAuth2Util(r, configfile=configfile)
        oauth.refresh(force=True)
        print "Logged in as /u/" + r.get_me().name
        return oauth
    except Exception as e:
        print "Failed to log in:"
        print_exception(e)
        print "Exiting"
        sys.exit()


def load_mod_list(subs, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False):
    """returns a map of name to list of subreddits of moderators of the given subs.
    default reddit instance provided for convenience in terminal. Don't use it in scripts."""

    if p: print "Loading moderators of %d subreddits:" % len(subs)

    if "--cache" in sys.argv or "-c" in sys.argv:
        print "Loading mod list from cache."
        f = open("mod_list_cache.pickle", "r")
        mod_list = cPickle.load(f)
        f.close()
        return mod_list

    mod_list = {}
    i = 0
    for sub in subs:
        subjust = str(i).rjust(2)
        ml = None
        skip = False
        while True:
            try:
                ml = r.get_subreddit(sub).get_moderators()
                break
            except praw.errors.Forbidden as e:
                print "\tsub %s: \tForbidden" % subjust
                skip = True
                break
            except praw.errors.HTTPException as e:
                print_exception(e)
            except Exception as e:
                # warn and skip on unknown error
                print e.__module__ + "." + e.__class__.__name__
                print_exception(e)
                skip = True
                break

        i += 1

        if skip:
            continue

        if p: print ("\tsub %s: " % subjust) + str(len(ml)).rjust(2) + " mods"

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
    oauth = None
    nologin = False
    if "--nologin" in sys.argv or "-n" in sys.argv:
        nologin = True

    if not nologin:
        oauth = login(r)
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

    return (r, db, pg, testmode, mod_list, multi, nologin, oauth)


def make_sublist(subs):
    """add '/r/'s to sub names and combine them with commas and 'and'"""
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
    info += make_special_info(*args)
    info += make_mod_info(*args)

    return info


def make_normal_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    """generate normal remark for all users, or dead remark"""

    info = config.TRIGGERSTRING + username
    if p: print "|\t" + info

    prevcount = 0
    alias_list = []

    while True:
        try:
            user = r.get_redditor(username, fetch=True)
            info = info.replace(username, user.name) # standardize capitalization
            info = "[{0}](http://reddit.com{0})".format(info)

            searchquery = "%2Fu%2F" + username
            alias_list = get_alias_list(username.lower())
            if len(alias_list) > 0:
                if p: print "|\t\tAlias"

                if db:
                    prevcount = db.get_alias_mentions(alias_list)

                if p: print "|\t\t%d previous alias mentions" % prevcount
                searchquery = make_searchquery(alias_list)

            info += config.NORMALSTRING.replace('$username$', username).replace("$searchquery$", searchquery)
            break
        except praw.errors.NotFound as e:
            # A 404 error means the user was deleted or banned
            info += config.DEADUSER.replace('$username$', username)
            if p: print '|\t\tDead'
            break
        except Exception as e:
            # Any other error (notably a 504) means we should try again to get the user
            print "Error getting user: %s: %s" % (type(e).__name__, str(e))
            time.sleep(2)
            continue

    if db and len(alias_list) == 0:
        prevcount = db.get_mentions(username)
    info = info.replace("$prevcount$", str(prevcount))
    if p and len(alias_list) == 0: print "|\t\t%d previous mentions" % prevcount

    return info


def make_special_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    """generate special remark for user, if any"""
    info = ""
    normal = normalize_name(username.lower())
    if normal in config.SPECIALS:
        if p: print '|\t\tSpecial'
        info += config.SPECIALS[normal].replace('$username$', normal)
    if username.lower() != normal.lower() and username in config.SPECIALS:
		if p: print '|\t\tAlias special'
		info += config.SPECIALS[username].replace('$username$', username)
    return info


def make_mod_info(username, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False):
    """generate mod remark, if user is a mod"""
    info = ""
    if username.lower() in mod_list:
        name = username.lower()
        subs = mod_list[name]
        if p: print "|\t\tMod " + str(subs)
        info += config.MOD_REMARK.replace("$sublist$", make_sublist(subs))
    return info


def scan_post(text, trigger=config.TRIGGERSTRING):
    """extract a set of usernames from a string"""
    users = set()
    CHARS = string.digits + string.ascii_letters + '-_'
    index = text.find(trigger)
    while index != -1:
        start = index + len(trigger)
        end = start

        if end < len(text):
            while end < len(text) and text[end] in CHARS:
                end += 1

            if len(text[start:end]) > 0:
                users.add(text[start:end])

        text = text[start:]
        index = text.find(trigger)
    return users


def make_comment(remarks):
    """generate a complete comment from a collection of remarks"""
    header = config.HEADER
    footer = config.FOOTER

    if len(remarks) > 1:
        header = header + config.COLLAPSIBLE_HEADER
        footer = config.COLLAPSIBLE_FOOTER + footer

    return header + "\n\n- " + "\n\n- ".join(remarks) + footer


def text_to_comment(text, mod_list={}, r=praw.Reddit(config.USERAGENT + " (manual mode)"), p=False, db=None, pg=False, triggers=[config.TRIGGERSTRING]):
    """generate a comment from a post"""
    # default reddit instance provided for convenience in terminal. Don't use it in scripts.

    names_set = set()
    for t in triggers:
        names_set |= scan_post(text, t)

    names = [n.lower() for n in names_set]
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
        try:
            newcomment = post.add_comment(comment)
            db.commit()
            print "| Comment posted. (http://reddit.com/comments/%s/-/%s)" % (newcomment.link_id[3:], newcomment.id)
            if config.DISTINGUISHCOMMENT:
                newcomment.distinguish()
                print "| Comment distinguished."
        except:
            raise
        finally:
            db.commit()
    else:
        print "| Comment not posted (bot is running in testing mode)."
    print


def post_reply(parent, comment, db, testmode=False):
    """submit a reply to a parent comment.
    Part of comment scanner."""
    if not testmode:
        print "! Posting comment..."
        try:
            newcomment = parent.reply(comment)
            db.commit()
            print "! Comment posted. (http://reddit.com/comments/%s/-/%s)" % (newcomment.link_id[3:], newcomment.id)
            if config.DISTINGUISHCOMMENT:
                newcomment.distinguish()
                print "! Comment distinguished."
        except:
            raise
        finally:
            db.commit()
    else:
        print "! Comment not posted (bot is running in testing mode)."
    print


def handle_comment(comment, r, db, mod_list, pg):
    """do stuff with a comment.
    Part of comment scanner."""

    username = "ircr"
    try:
        username = os.environ["IRCR_USERNAME"]
    except:
        pass
    triggers = ["+/u/" + username.lower(), "+ircrbot"]

    matching = [comment.body[:len(t)].lower() == t for t in triggers]
    if any(matching):
        id = comment.id
        try:
            if not db.is_oldcomment(id):
                db.add_oldcomment(id)

                text = comment.body[len(triggers[matching.index(True)]):]
                try:
                    author = comment.author.name
                except AttributeError:
                    author = "[deleted]"

                link = "http://www.reddit.com/comments/%s/-/%s" % (comment.link_id[3:], comment.id)
                found_string = u"\n! Found comment (%s) by /u/%s" % (link, author)
                print found_string.encode("ascii", "backslashreplace")

                reply, names = text_to_comment(text, mod_list, r, True, db, pg, [config.TRIGGERSTRING, "u/"])

                # Don't increment counts from summons (http://www.reddit.com/comments/2amark/-/cixzt9k?context=3)

                if len(names) > 0:
                    post_reply(comment, reply, db)
                else:
                    print "!\tNo users mentioned in comment.\n"
        except:
            db.rollback()
            raise
        finally:
            db.commit()


def make_searchquery(names):
    """construct a search query for all the given names"""
    q = ""
    for name in names:
        q += "%2Fu%2F$username$+OR+".replace("$username$", name)
    return q[:-4] # chop off final "+OR+"


def scan_subreddit(r, db, pg, testmode, mod_list):
    """scan post titles and post comments"""

    subreddit = r.get_subreddit(config.SUBREDDIT)
    posts = subreddit.get_new(limit=config.MAXPOSTS)
    for post in posts:
        text = "%s %s" % (post.title, post.selftext)
        try:
            pauthor = post.author.name
        except AttributeError:
            pauthor = "[deleted]"
        pid = post.id
        try:
            if not db.is_oldpost(pid):
                db.add_oldpost(pid)

                data = (post.title, pid, pauthor)
                found_string = u"\n| Found post \"%s\" (http://redd.it/%s) by /u/%s" % data
                if post.selftext:
                    found_string += " (Self post)"
                print found_string.encode("ascii", "backslashreplace")

                comment, names = text_to_comment(text, mod_list, r, True, db, pg)

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


def scan_comments(r, db, mod_list, pg):
    try:
        generator = r.get_subreddit(config.SUBREDDIT).get_comments(limit=100)
        for comment in generator:
            handle_comment(comment, r, db, mod_list, pg)
        time.sleep(config.WAIT)
    except Exception as e:
        print_exception(e)


def main(r, db, pg, testmode, mod_list):
    """continuously scan and post comments"""
    while True:
        try:
            scan_subreddit(r, db, pg, testmode, mod_list)
            scan_comments(r, db, mod_list, pg)
        except Exception as e:
            print_exception(e)
        db.commit()
        time.sleep(config.WAIT)


if __name__ == "__main__":
    try:
        r, db, pg, testmode, mod_list, multi, nologin, oauth = setup()
        main(r, db, pg, testmode, mod_list)

    except KeyboardInterrupt:
        print "\nExit"
