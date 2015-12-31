#!/usr/bin/python


import praw
import OAuth2Util
import time
import string
import sys
import os
import urlparse
import traceback
import cPickle as pickle
import argparse
import dateutil.relativedelta
import datetime


# load settings
import config



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



class InfoBot (object):
    """main class for bot functionality"""

    def __init__(self, cmdargs):
        """initialize program"""

        #self.r
        #self.db
        #self.pg
        #self.testmode
        #self.mod_list
        #self.multi
        #self.nologin
        #self.oauth
        #self.cmdargs

        self.cmdargs = cmdargs


        # undocumented feature: use --ircr flag to switch to scanning /r/ircr
        if self.cmdargs.ircr:
            config.SUBREDDIT = "ircr"
            config.WAIT = 5
            config.SQLITE_FILE = "ircr_testing.sqlite"


        # startup info
        print config.USERAGENT

        # lowercase all usernams for easy lookup
        config.SPECIALS = {k.lower():v for k,v in config.SPECIALS.items()}
        config.ALIASES = [[name.lower() for name in person] for person in config.ALIASES]

        # bot does not comment in testing mode
        self.testmode = False

        self.pg = False
        if self.cmdargs.postgres:
            self.pg = True
        self.db = DatabaseAccess(self.pg)

        self.multi = False
        if self.cmdargs.multi:
            self.multi = True
        self.r = self.reddit_connect(config.USERAGENT)


        # login
        self.oauth = None
        self.nologin = False
        if self.cmdargs.nologin:
            self.nologin = True

        if not self.nologin:
            self.bot_username, self.oauth = self.login()
        else:
            print "Not logging in."
            self.testmode = True


        self.mod_list = self.load_mod_list(config.SPECIAL_MOD_SUBS)

        if self.cmdargs.test:
            self.testmode = True


        if self.testmode:
            print "Running in testing mode. Bot will not post comments."
        else:
            print "Running in live mode. Bot will post comments."


    def format(self, s, **kwargs):
        return string.Formatter().vformat(s, (), SafeDict(kwargs))


    def reddit_connect(self, useragent):
        """connect to reddit"""
        # connect to reddit
        handler = None
        if self.multi:
            handler = praw.handlers.MultiprocessHandler()
            print "Connecting to praw-multiprocess"
        else:
            handler = praw.handlers.DefaultHandler()
        r = praw.Reddit(useragent, handler=handler)
        return r


    def login(self, configfile="oauth.ini"):
        """log in to reddit"""

        try:
            oauth = OAuth2Util.OAuth2Util(self.r, configfile=configfile)
            oauth.refresh(force=True)
            username = self.r.get_me().name
            print "Logged in as /u/" + username
            return username, oauth
        except Exception as e:
            print "Failed to log in:"
            print_exception(e)
            print "Exiting"
            sys.exit()


    def load_mod_list(self, subs):
        """returns a map of name to list of subreddits of moderators of the given subs.
        default reddit instance provided for convenience in terminal. Don't use it in scripts."""

        fname = "mod_list_cache.pickle"

        print "Loading moderators of %d subreddits:" % len(subs)

        if self.cmdargs.cache:
            print "Loading mod list from cache."
            f = open(fname, "r")
            mod_list = pickle.load(f)
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
                    ml = self.r.get_subreddit(sub).get_moderators()
                    break
                except praw.errors.Forbidden as e:
                    print "\tsub %s: \tForbidden (Private or Quarantined?)" % subjust
                    skip = True
                    break
                except praw.errors.HTTPException as e:
                    print_exception(e)
                except Exception as e:
                    # warn and skip on unknown error
                    print_exception(e)
                    skip = True
                    break

            i += 1

            if skip:
                continue

            print ("\tsub %s: " % subjust) + str(len(ml)).rjust(2) + " mods"

            mods = [u.name for u in ml]
            for name in mods:
                if name in mod_list:
                    mod_list[name].append(sub)
                else:
                    mod_list[name] = [sub]


        mod_list = {k.lower():v for k,v in mod_list.items()} #lowercase for easy lookup

        print "Saving mod list to `%s`." % fname
        with open(fname, "w") as f:
            pickle.dump(mod_list, f)

        return mod_list


    def scan_subreddit(self):
        """scan post titles and post comments"""

        subreddit = self.r.get_subreddit(config.SUBREDDIT)
        posts = subreddit.get_new(limit=config.MAXPOSTS)
        for post in posts:
            text = "%s %s" % (post.title, post.selftext)
            try:
                pauthor = post.author.name
            except AttributeError:
                pauthor = "[deleted]"
            pid = post.id
            try:
                if not self.db.is_oldpost(pid):
                    self.db.add_oldpost(pid)

                    data = (post.title, pid, pauthor)
                    found_string = u"\n| Found post \"%s\" (http://redd.it/%s) by /u/%s" % data
                    if post.selftext:
                        found_string += " (Self post)"
                    print found_string.encode("ascii", "backslashreplace")

                    comment, names = self.text_to_comment(text)

                    self.db.increment_names(names)

                    if len(names) > 0:
                        self.post_comment(post, comment)
                    else:
                        print "|\tNo users mentioned in post title.\n"
            except:
                self.db.rollback()
                raise
            finally:
                self.db.commit()


    def scan_comments(self):
        try:
            generator = self.r.get_subreddit(config.SUBREDDIT).get_comments(limit=100)
            for comment in generator:
                self.handle_comment(comment)
            time.sleep(config.WAIT)
        except Exception as e:
            print_exception(e)


    def handle_comment(self, comment):
        """do stuff with a comment.
        Part of comment scanner."""

        triggers = ["+/u/" + self.bot_username.lower(), "+ircrbot"]

        matching = [comment.body[:len(t)].lower() == t for t in triggers]
        if any(matching):
            id = comment.id
            try:
                if not self.db.is_oldcomment(id):
                    self.db.add_oldcomment(id)

                    text = comment.body[len(triggers[matching.index(True)]):]
                    try:
                        author = comment.author.name
                    except AttributeError:
                        author = "[deleted]"

                    link = "http://www.reddit.com/comments/%s/-/%s" % (comment.link_id[3:], comment.id)
                    found_string = u"\n! Found comment (%s) by /u/%s" % (link, author)
                    print found_string.encode("ascii", "backslashreplace")

                    reply, names = self.text_to_comment(text, [config.TRIGGERSTRING, "u/"])

                    # Don't increment counts from summons (http://www.reddit.com/comments/2amark/-/cixzt9k?context=3)

                    if len(names) > 0:
                        self.post_reply(comment, reply)
                    else:
                        print "!\tNo users mentioned in comment.\n"
            except:
                self.db.rollback()
                raise
            finally:
                self.db.commit()


    def text_to_comment(self, text, triggers=[config.TRIGGERSTRING]):
        """generate a comment from a post"""
        # default reddit instance provided for convenience in terminal. Don't use it in scripts.

        names_set = set()
        for t in triggers:
            names_set |= self.scan_post(text, t)

        names = [n.lower() for n in names_set]
        names.sort()

        remarks = []
        for name in names:
            remarks.append(self.make_info(name))

        comment = self.make_comment(remarks)

        return (comment, names)


    def scan_post(self, text, trigger=config.TRIGGERSTRING):
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


    def make_info(self, username):
        """Generate remark for a user.
        default reddit instance provided for convenience in terminal. Don't use it in scripts."""

        info  = self.make_normal_info(username)
        info += self.make_special_info(username)
        info += self.make_mod_info(username)

        return info


    def make_normal_info(self, username):
        """generate normal remark for all users, or dead remark"""

        info = config.TRIGGERSTRING + username
        print "|\t" + info

        prevcount = 0
        alias_list = []

        while True:
            try:
                user = self.r.get_redditor(username, fetch=True)
                rel_d = dateutil.relativedelta.relativedelta(datetime.datetime.utcnow(), datetime.datetime.utcfromtimestamp(user.created_utc))
                age = "%dy %dm %dd" % (rel_d.years, rel_d.months, rel_d.days) if rel_d.years > 0 else ("%dm %dd" % (rel_d.months, rel_d.days) if rel_d.months > 0 else "%dd" % rel_d.days)
                comment_karma = str(user.comment_karma) if user.comment_karma < 1000 else "%.1fk" % (float(user.comment_karma)/1000)
                link_karma    = str(user.link_karma)    if user.link_karma    < 1000 else "%.1fk" % (float(user.link_karma)   /1000)
                karma = "%s/%s" % (link_karma, comment_karma)

                info = info.replace(username, user.name) # standardize capitalization
                info = "[%s](http://reddit.com%s)" % (info.replace("_", "\_"), info) # block username mention and fix underscore italics

                searchquery = "%2Fu%2F" + username
                alias_list = self.get_alias_list(username.lower())
                if len(alias_list) > 0:
                    print "|\t\tAlias"

                    if self.db:
                        prevcount = self.db.get_alias_mentions(alias_list)

                    print "|\t\t%d previous alias mentions" % prevcount
                    searchquery = self.make_searchquery(alias_list)

                info += self.format(config.NORMALSTRING, username=username, age=age, karma=karma, searchquery=searchquery)
                break
            except praw.errors.NotFound as e:
                # A 404 error means the user was deleted or banned
                info += self.format(config.DEADUSER, username=username)
                print '|\t\tDead'
                break
            except Exception as e:
                # Any other error (notably a 504) means we should try again to get the user
                print "Error handling user: %s: %s" % (type(e).__name__, str(e))
                time.sleep(2)
                continue

        if self.db and len(alias_list) == 0:
            prevcount = self.db.get_mentions(username)
        info = self.format(info, prevcount=prevcount)
        if len(alias_list) == 0: print "|\t\t%d previous mentions" % prevcount

        return info


    def make_special_info(self, username):
        """generate special remark for user, if any"""
        info = ""
        normal = self.normalize_name(username.lower())
        if normal in config.SPECIALS:
            print '|\t\tSpecial'
            info += self.format(config.SPECIALS[normal], username=normal)
        if username.lower() != normal.lower() and username in config.SPECIALS:
            print '|\t\tAlias special'
            info += self.format(config.SPECIALS[username], username=username)
        return info


    def make_mod_info(self, username):
        """generate mod remark, if user is a mod"""
        info = ""
        if username.lower() in self.mod_list:
            name = username.lower()
            subs = self.mod_list[name]
            print "|\t\tMod " + str(subs)
            info += self.format(config.MOD_REMARK, sublist=self.make_sublist(subs))
        return info


    def make_searchquery(self, names):
        """construct a search query for all the given names"""
        q = ""
        for name in names:
            q += "%2Fu%2F{username}+OR+".format(username=name)
        return q[:-4] # chop off final "+OR+"


    def normalize_name(self, name):
        """returns the "normal" name if the given name is an alias"""
        alias_list = self.get_alias_list(name)
        if len(alias_list) > 0:
            return alias_list[0]
        else:
            return name


    def get_alias_list(self, name):
        """return a list of names the given name also goes by"""
        # haha, yes! See https://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        return [n for p in filter(lambda person: name in person, config.ALIASES) for n in p]


    def make_sublist(self, subs):
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


    def make_comment(self, remarks):
        """generate a complete comment from a collection of remarks"""
        header = config.HEADER
        footer = config.FOOTER

        if len(remarks) > 1:
            header = header + config.COLLAPSIBLE_HEADER
            footer = config.COLLAPSIBLE_FOOTER + footer

        return header + "\n\n- " + "\n\n- ".join(remarks) + footer


    def post_comment(self, post, comment):
        """submit a comment on a post"""
        if not self.testmode:
            print "| Posting comment..."
            try:
                newcomment = post.add_comment(comment)
                self.db.commit()
                print "| Comment posted. (http://reddit.com/comments/%s/-/%s)" % (newcomment.link_id[3:], newcomment.id)
                if config.DISTINGUISHCOMMENT:
                    newcomment.distinguish()
                    print "| Comment distinguished."
            except:
                raise
            finally:
                self.db.commit()
        else:
            print "| Comment not posted (bot is running in testing mode)."
        print


    def post_reply(self, parent, comment):
        """submit a reply to a parent comment.
        Part of comment scanner."""
        if not self.testmode:
            print "! Posting comment..."
            try:
                newcomment = parent.reply(comment)
                self.db.commit()
                print "! Comment posted. (http://reddit.com/comments/%s/-/%s)" % (newcomment.link_id[3:], newcomment.id)
                if config.DISTINGUISHCOMMENT:
                    newcomment.distinguish()
                    print "! Comment distinguished."
            except:
                raise
            finally:
                self.db.commit()
        else:
            print "! Comment not posted (bot is running in testing mode)."
        print


    def mainloop(self):
        """continuously scan and post comments"""
        while True:
            try:
                self.scan_subreddit()
                self.scan_comments()
            except Exception as e:
                print_exception(e)
            self.db.commit()
            time.sleep(config.WAIT)


# for config handling
# see https://stackoverflow.com/questions/17215400/python-format-string-unused-named-arguments
class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def print_exception(e):
    print "\n--------------------------------"
    print "*** ERROR: %s.%s: %s" % (e.__module__, type(e).__name__, str(e))
    traceback.print_exc()
    print "--------------------------------\n"


def main():
    try:
        parser = argparse.ArgumentParser(description="Scan posts and summoning comments for usernames and reply with information about them.", epilog="See the full documentation at https://github.com/AnSq/IRCR_Info_Bot for more details.")
        parser.add_argument("-t", "--test",     action="store_true", help="Test mode. Bot will not post comments.")
        parser.add_argument("-c", "--cache",    action="store_true", help="Load moderator list from cache rather than download it.")
        parser.add_argument("-m", "--multi",    action="store_true", help="Connect to and use praw-multiprocess for handling requests.")
        parser.add_argument("-n", "--nologin",  action="store_true", help="Don't attempt to log in. Implies --test.")
        parser.add_argument("-p", "--postgres", action="store_true", help="Use PostgreSQL instead of SQLite database.")
        parser.add_argument("-i", "--ircr",     action="store_true", help=argparse.SUPPRESS)
        parser.add_argument("-v", "--version",  action="version",    version="IRCR_Info_Bot v" + config.VERSION)
        cmdargs = parser.parse_args()

        bot = InfoBot(cmdargs)
        bot.mainloop()
    except KeyboardInterrupt:
        print "\nExit"


if __name__ == "__main__":
    main()
