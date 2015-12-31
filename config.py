#!/usr/bin/python

# Configuration for IRCR_Info_Bot


# Bot version. This goes in the user agent. Try to make sure different versions of the code that go live have different numbers
VERSION = "1.8.2"


# short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
USERAGENT = "IRCR Info Scanner v%s, controlled by the moderators of /r/isrconspiracyracist" % VERSION


# sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
SUBREDDIT = "isrconspiracyracist"
#SUBREDDIT = "ircr"


# A list of alias lists. Each account in the sublist is the same person.
# The first name of an alias list will be the "normal" name (used in SPECIALS, for example).
ALIASES = [
	["4to4", "4to3", "4to2", "4too", "4to6", "luckinator"],
	["Jewish_NeoCon", "Jewish_NeoCon2"],
	["Enochx", "Aerioch", "Thothx3"],
	["European88", "MayMayPoster", "Kill_All_Pakis", "gas-the-kikes"],
	["KlausDuJong", "AbsolomVonWret", "TheCanticleer", "HideoYamaguchi", "CaptainRalph", "ToquersCafe", "MelvinMole", "TheCantalabrian", "JohnnyJingleballs","JonApplethorn","CaptainRalph","TankTinker","ToquersCafe"], # Martin Timothy
	["Antiochus88", "Indra-Varuna"],
	["baller222", "theskunk90", "bogota79", "gregster3", "jarmin9", "lexicon80", "arabiaz", "jackson990"], # "Precepts of the Talmud" guy
	["iamagod______","iamagod_____", "iamagod____", "iamagod___", "iamagod__"],
	["eagleshigh", "EaglezhighH8H8"],
	["Detroit_Safari", "NolanChancellor", "Nolan_Chancellor"],
	["AlphamaxHD", "MossadOwnsPOTUS", "AnonBTCShoppin", "YHWHisSatan", "LOLHOLOHOAX"],
	["RedditRevisionist", "user1060", "user1065", "user1067", "HDNWdotcom", "NankingThrowaway", "AHdidnothingwrong", "holocaustisholohoax", "Boredquestioner", "JUSTASKINGQUESTlONS", "davesimmonds3"],
	["davidtoni", "xanaxinator"]
]


# remark that every user gets. {username} will be replaced by the username automatically
# These variables will be automatically replaced with their corresponding values
#     {username}    : username
#     {age}         : account age, for example, "2y 8m 20d" for 2 years, 8 months, and 20 days
#     {karma}       : account karma, for example, 277/12.4k for 277 link karma and 12400 comment karma
#     {prevcount}   : number of previous mentions of this user (or their aliases) in the database
#     {searchquery} : a query for reddit's search engine to get a list of previous mentions, including aliases
NORMALSTRING = ": Age: {age} | Karma: {karma} | [{prevcount} previous posts](http://www.reddit.com/r/isrconspiracyracist/search?q={searchquery}&restrict_sr=on&sort=relevance&t=all) | [Redective](http://www.redective.com/?r=e&a=search&s=user&t=redective&q={username}) | [RedditGraphs](http://www.roadtolarissa.com/redditgraphs/?{username}&PieChart&Number&Comments) | [SnoopSnoo](http://snoopsnoo.com/u/{username})"


# extra remark that mods of subs in SPECIAL_MOD_SUBS get.
# Variables:
#     {sublist} : a list of modded subs (e.g., "/r/pics, /r/funny, and /r/conspiracy")
MOD_REMARK = " | Moderator of {sublist}"


# remark for accounts which are invalid or shadowbanned. $username$ will be replaced by the username automatically
# $prevcount$ is replaced by the number of previous posts mentioning the user
# Variables (see NORMALSTRING):
#     {username}
#     {prevcount}
DEADUSER = ": [{prevcount} previous posts](http://www.reddit.com/r/isrconspiracyracist/search?q=%2Fu%2F{username}&restrict_sr=on&sort=relevance&t=all) | Account shadowbanned/deleted"


# list of subreddits to add special remarks to mods of
SPECIAL_MOD_SUBS = ["conspiracy", "ZOG", "WhiteRights", "holocaust", "GreatApes", "BlackCrime", "WhiteNationalism", "AdolfHitler", "NationalSocialism", "GoldenDawn", "White_Pride", "Race_Realism", "AmericanJewishPower", "BritishJewishPower", "NorthwestFront", "Reichspost", "FourthReich", "Chimpout", "ChrysiAvgi", "GoEbola", 'Apefrica', 'Ausfailia', 'Ben_Garrison', 'BritishNationalParty', 'Detoilet', 'Londonistan', 'N1GGERS', 'NegroFree', 'NiggerCartoons', 'NiggerMythology', 'NiggersGIFs', 'NiggersNews', 'NiggersTIL', 'RacistNiggers', 'TNB', 'TheGoyimKnow', 'TheProjects', 'TrayvonMartin', 'UKistan', 'WTFniggers', 'WhiteIdentity', 'WhiteRights1', 'chimpmusic', 'farright', 'ferguson', 'funnyniggers', 'niggerspics', 'polacks', 'polfacts', 'whitebeauty']


# Map of special users to their extra remark.
# Automatically works for any alias when the key is the "normal" name (first name in alias list)
# Variables:
#     {username}
SPECIALS = {
"Antiochus88"
    : " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Fantiochus88)",

"European88"
    : " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Feuropean88)",

"Jude_Fetzen911"
    : " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2Fjude_fetzen911)",

"4to4"
    : " | [Top Racist Posters entry](http://www.reddit.com/r/isrconspiracyracist/wiki/topracistposters#wiki_.2Fu.2F4to4)",

"MayMayPoster"
    : " | Alt account of /u/European88",

"KlausDuJong"
    : " | [Martin Timothy alt](http://redd.it/2ux5ym). [Fantasizes about personally gassing Jews](http://redd.it/2eob41).",

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

"RedditRevisionist"
    : " | [neo-Nazi](http://redd.it//2ykqgx/) with [lots of alts](http://redd.it/2zntjv)",

"AssuredlyAThrowAway"
    : "| former mod of /r/conspiracy",
}


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
MAXPOSTS = 25


# This is how many seconds you will wait between cycles. The bot is completely inactive during this time.
WAIT = 30


SQLITE_FILE = "database.sqlite"
