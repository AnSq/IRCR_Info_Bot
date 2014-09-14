#!/usr/bin/python

# Configuration for IRCR_Info_Bot


# Bot version. This goes in the user agent. Try to make sure different versions of the code that go live have different numbers
VERSION = "1.6.2"


# short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
USERAGENT = "/u/IRCR_Info_Bot v%s, controlled by the moderators of /r/isrconspiracyracist" % VERSION


# sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
SUBREDDIT = "isrconspiracyracist"
#SUBREDDIT = "ircr"


# A list of alias lists. Each account in the sublist is the same person.
# The first name of an alias list will be the "normal" name (used in SPECIALS, for example).
ALIASES = [["4to4", "4to3", "4to2", "4too"], ["Jewish_NeoCon", "Jewish_NeoCon2"], ["Enochx", "Aerioch"], ["European88", "MayMayPoster"]]


# remark that every user gets. $username$ will be replaced by the username automatically
# $prevcount$ is replaced by the number of previous posts mentioning the user
#NORMALSTRING = ": [Submissions](http://reddit.com/u/$username$/submitted) | [Comments](http://reddit.com/u/$username$/comments)"
NORMALSTRING = ": [other /r/ircr posts ($prevcount$ previous)](http://www.reddit.com/r/isrconspiracyracist/search?q=$username$+OR+flair%3A%27$username$%27&restrict_sr=on&sort=relevance&t=all) | [Redective link](http://www.redective.com/?r=e&a=search&s=user&t=redective&q=$username$) | [Redditgraphs link](http://redditgraphs.com/?$username$&PieChart&Number&Submissions)"


# Map of special users to their extra remark. $username$ will be replaced by the username automatically.
# Automatically works for any alias when the key is the "normal" name (first name in alias list)
SPECIALS = {
"Antiochus88"
    : " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Fantiochus88)",

"European88"
    : " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Feuropean88)",

"Jude_Fetzen911"
    : " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Fjude_fetzen911)",

"4to4"
    : " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2F4to4)",

"SovereignMan"
    : " | Former moderator of /r/conspiracy",

"MayMayPoster"
    : " | Alt account of /u/European88",

"TheCanticleer"
    : " | Unashamed anti-semite, blames Jews for 9/11",

"KlausDuJong"
    : " | [White supremacist. Literally fantasizes about genociding Jews; blames them for 9/11](http://redd.it/2eob41)",

"Flytape"
    : " | Pro-racism mod of /r/conspiracy",

"Enochx"
    : " | Anti-semite; likes to hide behind 'Zionist-Jews'",

"PrimaryPerception"
    : " | Extreme anti-semite; thinks all Jews are responsible for 9/11",

"InUrHiveKickinUrBees"
    : " | Thinks Jews banned /r/thefappening",

"sinominous"
    : " | Anti-semite and Holocaust denier",

"dindu_nuffin"
    : " | Racist anti-semite. [Has been heavily upvoted for Holocaust Denial](http://redd.it/2f7wou).",

"I_WILL_REMIND_THEM"
    : " | [\"Jews are hated by everyone on this planet and better off dead. I consider them far less than human.\"](http://redd.it/2donjh/)",

"mtersen"
    : " | [\"Everyday, it becomes clearer and clearer that these jews really are as evil as Hitler described!\"](http://www.reddit.com/r/isrconspiracyracist/comments/2dn936/ircr/cjrc0qu/)",

"foldegrep"
    : " | [Thinks Hitler was right about the Jews](http://www.reddit.com/r/isrconspiracyracist/comments/2dn936/ircr/cjrc0qu)",

"ValikorWarlock"
    : " | [\"jews fuck with the economy and kill people\"](http://www.reddit.com/r/isrconspiracyracist/comments/2dn936/ircr/cjrc0qu)",

"Oh_No_You_Did_Not"
    : " | Proud anti-semite",

"the_no_bro"
    : " | Blatant anti-semite",

"Jalapenile"
    : " | Blatant anti-semite",
}


# extra remark aliased names get. $searchquery$ replaced with reddit search query for all aliases, including in flairs.
# $prevcount$ replaced with number of previous posts involving any alias
ALIAS_REMARK = " | [**IRCR posts with any alias** ($prevcount$ previous)](http://www.reddit.com/r/isrconspiracyracist/search?q=$searchquery$&restrict_sr=on&sort=relevance&t=all)"


# list of subreddits to add special remarks to mods of
SPECIAL_MOD_SUBS = ["conspiracy", "ZOG", "WhiteRights", "holocaust", "GreatApes", "BlackCrime", "WhiteNationalism", "AdolfHitler", "NationalSocialism", "WhiteRightsUK", "GoldenDawn", "White_Pride", "Race_Realism", "AmericanJewishPower", "BritishJewishPower", "NorthwestFront", "Reichspost", "FourthReich", "Chimpout", "ChrysiAvgi", "GoEbola", 'Apefrica', 'Ausfailia', 'Ben_Garrison', 'BritishNationalParty', 'Detoilet', 'Londonistan', 'N1GGERS', 'NegroFree', 'NiggerCartoons', 'NiggerMythology', 'NiggersGIFs', 'NiggersNews', 'NiggersTIL', 'RacistNiggers', 'TNB', 'TheGoyimKnow', 'TheProjects', 'TrayvonMartin', 'UKistan', 'WTFniggers', 'WatchNiggersDie', 'WhiteIdentity', 'WhiteRights1', 'chimpmusic', 'farright', 'ferguson', 'funnyniggers', 'niggerspics', 'polacks', 'polfacts', 'whitebeauty']


# extra remark that mods of subs in SPECIAL_MOD_SUBS get.
# $sublist$ replaced with list of modded subs (e.g., "/r/pics, /r/funny, and /r/conspiracy")
MOD_REMARK = " | Moderator of $sublist$"


# remark for accounts which are invalid or shadowbanned. $username$ will be replaced by the username automatically
# $prevcount$ is replaced by the number of previous posts mentioning the user
DEADUSER = ": [previous /r/ircr posts ($prevcount$)](http://www.reddit.com/r/isrconspiracyracist/search?q=$username$+OR+flair%3A%27$username$%27&restrict_sr=on&sort=relevance&t=all) | Account shadowbanned/deleted"


# This will be at the very top of the comment. \n\n creates a new line. Set this to "" if you don't want anything.
HEADER = "More information about these users:"


# This will follow the header if there is more than one user
COLLAPSIBLE_HEADER = "\n\n#####&#009;\n\n######&#009;\n\n####&#009;"


# Something about this being a bot and tell us if there's a problem. Maybe a source code link too.
DISCLAIMER = "\n\n*[I am a bot](https://github.com/AnSq/IRCR_Info_Bot). Contact the [moderators](http://www.reddit.com/message/compose?to=%2Fr%2Fisrconspiracyracist) if there is a problem.*"


# This will precede the footer if there is more than one user
COLLAPSIBLE_FOOTER = "\n\n####&#009;\n\n#####&#009;\n\n###&#009;"


# This will be at the very bottom of the comment. Set to "" if you don't want anything.
FOOTER = DISCLAIMER


# If your bot is a moderator, you can distinguish the comment. Use True or False (Use capitals! No quotations!)
DISTINGUISHCOMMENT = True


# This is the thing in the title you're looking for.
TRIGGERSTRING = '/u/'


# This is how many posts you want to retrieve all at once. PRAW can download 100 at a time.
MAXPOSTS = 10


# This is how many seconds you will wait between cycles. The bot is completely inactive during this time.
WAIT = 30
