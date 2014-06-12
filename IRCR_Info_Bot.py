#!/usr/bin/python
import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import sqlite3
import string

'''USER CONFIGURATION'''

#This is the bot's Username. In order to send mail, it must have some amount of Karma.
USERNAME  = "IRCR_info_bot"

#This is the bot's Password.
PASSWORD  = "BOT_PASSWORD"

#This is a short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
USERAGENT = "/r/ircr info bot"

#This is the sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
SUBREDDIT = "isrconspiracyracist"

NORMALSTRING = ": [previous /r/ircr posts](http://www.reddit.com/r/isrconspiracyracist/search?q=_username_+OR+flair%3A%27_username_%27&restrict_sr=on&sort=relevance&t=all) | [Redective link](http://www.redective.com/?r=e&a=search&s=user&t=redective&q=_username_) | [Redditgraphs link](http://redditgraphs.com/?_username_&PieChart&Number&Submissions)"
#NORMALSTRING = ": [Submissions](http://reddit.com/u/_username_/submitted) | [Comments](http://reddit.com/u/_username_/comments)"
#This is the remark that every user gets. _username_ will be replaced by the username automatically

#This is the list of Special Users
SPECIALS = ["Antiochus88", "European88","Jude_Fetzen911","4to4","4to3","4to2","4too"]

#This is the extra remark that Special Users get. _username_ will be replaced by the username automatically
SPECIALSTRING = [" | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Fantiochus88)",
" | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Feuropean88)"," | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Fjude_fetzen911)"," | [**IRCR search with all aliases**](http://www.reddit.com/r/isrconspiracyracist/search?q=4to4+OR+4to3+OR+4to2+OR+4too+OR+flair%3A%274to4%27+OR+flair%3A%274to3%27+OR+flair%3A%274to2%27OR+flair%3A%274too%27&restrict_sr=on&sort=relevance&t=all) | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2F4to4)"," | [**IRCR search with all aliases**](http://www.reddit.com/r/isrconspiracyracist/search?q=4to4+OR+4to3+OR+4to2+OR+4too+OR+flair%3A%274to4%27+OR+flair%3A%274to3%27+OR+flair%3A%274to2%27OR+flair%3A%274too%27&restrict_sr=on&sort=relevance&t=all) | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2F4to4)"," | [**IRCR search with all aliases**](http://www.reddit.com/r/isrconspiracyracist/search?q=4to4+OR+4to3+OR+4to2+OR+4too+OR+flair%3A%274to4%27+OR+flair%3A%274to3%27+OR+flair%3A%274to2%27OR+flair%3A%274too%27&restrict_sr=on&sort=relevance&t=all) | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2F4to4)"," | [**IRCR search with all aliases**](http://www.reddit.com/r/isrconspiracyracist/search?q=4to4+OR+4to3+OR+4to2+OR+4too+OR+flair%3A%274to4%27+OR+flair%3A%274to3%27+OR+flair%3A%274to2%27OR+flair%3A%274too%27&restrict_sr=on&sort=relevance&t=all) | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2F4to4)"]

#This is the remark for accounts which are invalid or shadowbanned. _username_ will be replaced by the username automatically
DEADUSER = ": [previous /r/ircr posts](http://www.reddit.com/r/isrconspiracyracist/search?q=_username_+OR+flair%3A%27_username_%27&restrict_sr=on&sort=relevance&t=all) | Account shadowbanned/deleted"

#This will be at the very top of the comment. \n\n creates a new line. Set this to "" if you don't want anything.
HEADER = "More information about these users:\n\n#####&#009;\n\n######&#009;\n\n####&#009;\n\n- "

#This will be at the very bottom of the comment. Set to "" if you don't want anything.
FOOTER = "\n\n####&#009;\n\n#####&#009;\n\n###&#009;\n\n*This was done by a bot. Contact the [moderators](http://www.reddit.com/message/compose?to=%2Fr%2Fisrconspiracyracist) or [author](http://reddit.com/u/GoldenSights) if there is a problem.*"

#If your bot is a moderator, you can distinguish the comment. Use True or False (Use capitals! No quotations!)
DISTINGUISHCOMMENT = True

#This is the thing in the title you're looking for.
TRIGGERSTRING = '/u/'

#This is how many posts you want to retrieve all at once. PRAW can download 100 at a time.
MAXPOSTS = 5

#This is how many seconds you will wait between cycles. The bot is completely inactive during this time.
WAIT = 20


'''All done!'''



#This is the list of characters which are allowed in usernames. Don't change this.
CHARS = string.digits + string.ascii_letters + '-_'

try:
    import bot #This is a file in my python library which contains my Bot's username and password. I can push code to Git without showing credentials
    USERNAME = bot.getuG()
    PASSWORD = bot.getpG()
    USERAGENT = bot.getaG()
except ImportError:
    pass
WAITS = str(WAIT)
sql = sqlite3.connect('sql.db')
print('Loaded SQL Database')
cur = sql.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
print('Loaded Completed table')


sql.commit()

r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)

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
        cur.execute('SELECT * FROM oldposts WHERE ID="%s"' % pid)
        if not cur.fetchone():
            cur.execute('INSERT INTO oldposts VALUES("%s")' % pid)
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

                        for m in range(len(SPECIALS)):
                            name = SPECIALS[m]
                            if name.lower() == word.lower():
                                print('\tSpecial')
                                finalword += SPECIALSTRING[m].replace('_username_', word)

                        result.append(finalword)
            if len(result) > 0:
                final = HEADER + '\n\n- '.join(result) + FOOTER
                print('Creating comment.')
                newcomment = post.add_comment(final)
                if DISTINGUISHCOMMENT == True:
                    print('Distinguishing Comment.')
                    newcomment.distinguish()
            else:
                print('\tNone!')
        sql.commit()


while True:
    try:
        scanSub()
    except Exception as e:
        print('An error has occured:', str(e))
    print('Running again in ' + WAITS + ' seconds \n')
    sql.commit()
    time.sleep(WAIT)
