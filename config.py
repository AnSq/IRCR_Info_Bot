#!/usr/bin/python

# Configuration for IRCR_Info_Bot


# Bot version. This goes in the user agent. Try to make sure different versions of the code that go live have different numbers
VERSION = "1.5"


# short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
USERAGENT = "/u/IRCR_Info_Bot v%s, controlled by the moderators of /r/isrconspiracyracist" % VERSION


# sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
SUBREDDIT = "isrconspiracyracist"
#SUBREDDIT = "ircr"


# A list of alias lists. Each account in the sublist is the same person.
# The first name of an alias list will be the "normal" name (used in SPECIALS, for example).
ALIASES = [["4to4", "4to3", "4to2", "4too"], ["Jewish_NeoCon", "Jewish_NeoCon2"], ["Enochx", "Aerioch"]]


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
}


# extra remark aliased names get. $searchquery$ replaced with reddit search query for all aliases, including in flairs.
# $prevcount$ replaced with number of previous posts involving any alias
ALIAS_REMARK = " | [**IRCR posts with any alias** ($prevcount$ previous)](http://www.reddit.com/r/isrconspiracyracist/search?q=$searchquery$&restrict_sr=on&sort=relevance&t=all)"


# list of subreddits to add special remarks to mods of
SPECIAL_MOD_SUBS = ["conspiracy", "ZOG", "WhiteRights", "holocaust", "GreatApes", "BlackCrime", "WhiteNationalism", "AdolfHitler", "NationalSocialism", "WhiteRightsUK", "GoldenDawn", "White_Pride", "Race_Realism", "AmericanJewishPower", "BritishJewishPower", "NorthwestFront", "Reichspost", "FourthReich", "Chimpout", "ChrysiAvgi", "GoEbola", 'AlSharpton', 'Apefrica', 'AskBetas', 'Ausfailia', 'Ben_Garrison', 'BlackAfrica', 'BlackHusbands', 'BritishNationalParty', 'CamelFucker', 'CamelFuckers', 'CaveNigger', 'CaveNiggers', 'ChildFreee', 'ChimpireMETA', 'ChimpireOfftopic', 'Darren_Wilson', 'Detoilet', 'DurkaDurka', 'FunnyNigger', 'GoodLuckEbola', 'GreatApes2', 'HailOdin', 'JewishQuestion', 'Jihadi', 'JustBlackGirlThings', 'LiberalDegeneracy', 'Londonistan', 'N1GGERS', 'NegroFree', 'NiggerCartoons', 'NiggerDocumentaries', 'NiggerDrama', 'NiggerFacts', 'NiggerMythology', 'NiggerNews', 'NiggerTIL', 'NiggersCartoons', 'NiggersDocumentaries', 'NiggersGIFs', 'NiggersNews', 'NiggersRedditDrama', 'NiggersTIL', 'Nignigs', 'Pakis', 'PlanetoftheGreatApes', 'RacistNiggers', 'Raghead', 'Ragheads', 'SandCoon', 'SandCoons', 'SandFleas', 'SandMonkey', 'SandMonkeys', 'SandN1gger', 'SandN1ggers', 'SandNazi', 'SandNazis', 'Sand_Niggers', 'SheetWearingRagHeads', 'ShitMummies', 'ShitMummy', 'ShitNiggersSay', 'SleeperCells', 'SwedenYes', 'TNB', 'Terrab', 'TheGoyimKnow', 'TheProjects', 'TheRacistRedPill', 'ThuleanPerspective', 'TowelHead', 'Towlie', 'TrayvonMartin', 'TrueFerguson', 'TwoXSheboons', 'TypicalNBehavior', 'TypicalNiggerBehavior', 'UKistan', 'USBlackCulture', 'UrbanTurban', 'Volkisch', 'WTFniggers', 'WatchNiggersDie', 'WhiteIdentity', 'WhiteRights1', 'WhiteRightsScience', 'WorldStarHP', 'apewrangling', 'cameljockeys', 'chicongo', 'chimpmusic', 'coons', 'didntdonuffins', 'dintdonuffin', 'dotheads', 'farright', 'feministbeauty', 'ferguson', 'fergusonriot', 'fergusonriots', 'funnyniggers', 'gibsmedat', 'goatfucker', 'jewpride', 'media', 'mudslime', 'muhdick', 'muhdik', 'niggerhistorymonth', 'niggersdrama', 'niggersfacts', 'niggerspics', 'niggersstories', 'niggersvideos', 'niggervideos', 'niglets', 'odinist', 'photobucket', 'pocecil', 'polacks', 'polfacts', 'shegroids', 'teenapers', 'traditional', 'whitebeauty']


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
