#!/usr/bin/python

# Configuration for IRCR_Info_Bot


# Bot version. This goes in the user agent. Try to make sure different versions of the code that go live have different numbers
VERSION = "1.1"


# short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
USERAGENT = "/u/IRCR_Info_Bot v%s, controlled by the moderators of /r/isrconspiracyracist" % VERSION


# sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
SUBREDDIT = "isrconspiracyracist"


# remark that every user gets. _username_ will be replaced by the username automatically
#NORMALSTRING = ": [Submissions](http://reddit.com/u/_username_/submitted) | [Comments](http://reddit.com/u/_username_/comments)"
NORMALSTRING = ": [previous /r/ircr posts](http://www.reddit.com/r/isrconspiracyracist/search?q=_username_+OR+flair%3A%27_username_%27&restrict_sr=on&sort=relevance&t=all) | [Redective link](http://www.redective.com/?r=e&a=search&s=user&t=redective&q=_username_) | [Redditgraphs link](http://redditgraphs.com/?_username_&PieChart&Number&Submissions)"


# Map of special users to their extra remark. _username_ will be replaced by the username automatically
SPECIALS = {
"Antiochus88"
	: " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Fantiochus88)",

"European88"
	: " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Feuropean88)",

"Jude_Fetzen911"
	: " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Fjude_fetzen911)",

"4to4"
	: " | [**IRCR search with all aliases**](http://www.reddit.com/r/isrconspiracyracist/search?q=4to4+OR+4to3+OR+4to2+OR+4too+OR+flair%3A%274to4%27+OR+flair%3A%274to3%27+OR+flair%3A%274to2%27OR+flair%3A%274too%27&restrict_sr=on&sort=relevance&t=all) | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2F4to4)",
}
# duplicate for 4to4 aliases
SPECIALS["4to3"] = SPECIALS["4to4"]
SPECIALS["4to2"] = SPECIALS["4to4"]
SPECIALS["4too"] = SPECIALS["4to4"]

# list of subreddits to add special remarks to mods of
SPECIAL_MOD_SUBS = ["conspiracy", "ZOG", "WhiteRights", "holocaust"]

# extra remark that mods of subs in SPECIAL_MOD_SUBS get. _subreddit_ replaced with subreddit name (no /r/) automatically (and _username_)
MOD_REMARK = " | /r/_subreddit_ mod"

# remark for accounts which are invalid or shadowbanned. _username_ will be replaced by the username automatically
DEADUSER = ": [previous /r/ircr posts](http://www.reddit.com/r/isrconspiracyracist/search?q=_username_+OR+flair%3A%27_username_%27&restrict_sr=on&sort=relevance&t=all) | Account shadowbanned/deleted"


# This will be at the very top of the comment. \n\n creates a new line. Set this to "" if you don't want anything.
HEADER = "More information about these users:\n\n#####&#009;\n\n######&#009;\n\n####&#009;\n\n- "


# This will be at the very bottom of the comment. Set to "" if you don't want anything.
FOOTER = "\n\n####&#009;\n\n#####&#009;\n\n###&#009;\n\n*[I am a bot](https://github.com/AnSq/IRCR_Info_Bot). Contact the [moderators](http://www.reddit.com/message/compose?to=%2Fr%2Fisrconspiracyracist) if there is a problem.*"


# If your bot is a moderator, you can distinguish the comment. Use True or False (Use capitals! No quotations!)
DISTINGUISHCOMMENT = True


# This is the thing in the title you're looking for.
TRIGGERSTRING = '/u/'


# This is how many posts you want to retrieve all at once. PRAW can download 100 at a time.
MAXPOSTS = 10


# This is how many seconds you will wait between cycles. The bot is completely inactive during this time.
WAIT = 30
