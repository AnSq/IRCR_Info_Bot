# IRCR_Info_Bot

[/u/IRCR_Info_Bot](http://www.reddit.com/user/IRCR_Info_Bot) on [/r/isrconspiracyracist](http://www.reddit.com/r/isrconspiracyracist).

Scans posts and summoning comments for usernames and replies with information about them.

Originally written by [/u/GoldenSights](http://www.reddit.com/user/GoldenSights) ([original code](https://github.com/voussoir/reddit/blob/68b45302fb9fd8129a0ebc41f936ebbb08bad0f3/TitleNames/titlenames.py)), now maintained by the moderators of [/r/isrconspiracyracist](http://www.reddit.com/r/isrconspiracyracist).


## Usage

IRCR_Info_Bot scans posts and comments in a particular subreddit for Reddit usernames and replies with information about the mentioned users. Depending on its configuration, it can provide links that provide additional information about the users, a list of relevant subreddits they moderate, account ages and karma values, information about their account status (ie, if they're deleted, suspended, or shadowbanned).

Usernames are detected (in the contexts described below) if they are in the form `/u/username`. Note that in all cases, both slashes are required.

IRCR_Info_Bot will check all posts in the subreddit it's running on for usernames in post titles. The bot will also scan the body text of self posts for usernames.

IRCR_Info_Bot can also be summoned in comments to give information about additional users. Comments that start with either “+/u/*[bot-username]*” (ie, “+/u/IRCR_Info_Bot” in /r/isrconspiracyracist) or “+ircrbot” (both cases without quotes, and they're not case sensitive) will be scanned for usernames in the same way as post titles and self post bodies. Any other text in the comment will be ignored by the bot, the same as with self post bodies. If you do not want your comment to send a mention notification to the mentioned users inboxes, you can write a backslash in front of their name, for example `\/u/username`. The backslash will not appear in your comment, and their username will not show up as a link.


## Running the Bot

Start with `python IRCR_Info_Bot.py [options]`.

Stop the bot by pressing Ctrl-C.


### Options

**-h, --help**: Show summary of options and exit.

**-t, --test**: Test mode. Bot will scan subreddit and print to the console as normal, but it will not post comments. It *will* update the database, so anything scanned in test mode will not be rescanned if you run the bot again in normal mode.

**-c, --cache**: Load moderator list from cache rather than download it. See the section on `SPECIAL_MOD_SUBS` for more details.

**-m, --multi**: *Deprecated: This should generally no longer be needed since the switch to OAuth. It hasn't been tested in a while, so it's not guaranteed to work.* Connect to and use praw-multiprocess for handling requests. See the [PRAW documentation](https://praw.readthedocs.org/en/stable/pages/multiprocess.html) for more information.

**-n, --nologin**: Don't attempt to log in. This will not work if your wiki config page is restricted to moderators (see the section on the wiki config). It will also fail to download moderator lists for private subreddits you're a member of and all quarantined subreddits (see the section on moderator lists). Implies `--test`.

**-p, --postgres**: Use PostgreSQL instead of SQLite database. Requires that a `DATABASE_URL` environment variable be defined in the form `postgres://<username>:<password>@<host>:<port>/<database>`. **Note:** Using PostgreSQL with this bot has not been tested in quite a while, and it's possible that it may not work anymore. If you find that to be the case, [open an issue](../../issues/new?title=PostgreSQL+support+broken.+[fill+in+details]&body=[Fill+in+details]).

**-v, --version**: Show bot's version number and exit.


## Configuration

IRCR_Info_Bot uses 3 files to control its settings. A local config file called `config.yaml` gives the most basic settings, including the locations of the other two files. Another file gives the OAuth credentials for the bot to log in. The remaining settings are stored on a wiki page of the subreddit the bot runs in.

The local config file and the wiki page are written in [YAML](https://en.wikipedia.org/wiki/YAML). If you don't know YAML, follow the linked examples and you should be fine. Keep in mind that indentation matters in YAML, and it always uses spaces, never tabs.


### Local Config

The local configuration is in a file called `config.yaml`. [This is the local config file that the bot is currently using.](config.yaml)

At the top level, it is a dictionary with the following 6 items:

**USERAGENT**: The User-Agent string that the bot uses to identify itself to the Reddit server. See [Reddit's API rules](https://github.com/reddit/reddit/wiki/API) for more information. `{version}` in this value will be replaced with the bot's version number.

**SUBREDDIT**: The subreddit that the bot will scan and comment in.

**WIKI_CONFIG_PAGE**: Wiki page of SUBREDDIT (ie, `https://www.reddit.com/r/{SUBREDDIT}/wiki/{WIKI_CONFIG_PAGE}`) that contains the wiki config file.

**SQLITE_FILE**: The file name of the SQLite database file. This key needs to be present even if the bot is using a PostgreSQL database (although I suppose you could leave the value blank in that case).

**MAIN_USER**: The username that the bot will log in and post comments as.

**USERS**: A dictionary where the keys are usernames and the values are the filenames of the corresponding OAuth credential file. (It's a dictionary instead of a single value for forward compatibility with the currently unwritten solution to [issue #16](../../issues/16), in case you were wondering.)


### OAuth Credentials

IRCR_Info_Bot uses [praw-OAuth2Util](https://github.com/SmBe19/praw-OAuth2Util) to handle logging in. praw-OAuth2Util uses its own configuration file to store the login credentials, the format of which is documented [here](https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md#config).

IRCR_Info_Bot needs the identity, modposts, read, submit, and wikiread OAuth scopes. See [oauth_example.oauth.ini](oauth_example.oauth.ini) for an example of how to set it up.

To set it up on the Reddit side, go to https://www.reddit.com/prefs/apps, create a new app, and fill in the details. Set the type to “script” and the redirect URL to `http://127.0.0.1:65010/authorize_callback`. Once you click “create app”, the app key will be the random looking string under the name, and the app secret will be the other random looking string labeled “secret”. Copy those in to the appropriate places in the OAuth file. You may also need to add your bot's account as a developer.

To get praw-OAuth2Util to fill in the last section of the file, first go to the [Reddit website](https://www.reddit.com) and log in as the bot's account, then run the bot. A web page will open asking you to give your app access to the account. Click “allow”. After a few seconds you can stop the bot if you would like. You only have to do this once, and the OAuth file will store all the details it needs to log in again.

**Keep your OAuth file secret.** Do not post it anywhere on the internet. In particular, don't push it to a GitHub repository.


### Wiki Config

To allow for easy settings changes without having to mess around with git (and to keep the repository free of the inevitable racist references that come when you're dealing with racist users), the bot loads most of its configuration from a wiki page of the subreddit it runs on.

Some options support variables, which consist of a variable name enclosed in braces, like this: `{variable}`. These will be replaced with their corresponding values each time they are used by the bot.

[Here is an example wiki config file.](wiki_config_example.txt) You can paste this into a new wiki page to use as a base for your own configuration.

If you want to keep the bot's settings private, go to the wiki page's settings and select “only mods may edit and view”. If you do this the bot must be a moderator of the subreddit, and the `--nologin` command line flag will not work.

The bot loads the wiki config by interpreting the contents of the first `<code>` block as a YAML file. This means that everything line you want read as part of the settings must have four spaces at the beginning in addition to any spaces needed for the YAML structure. You can safely put any other text before or after this section and it will be ignored, but you may not use backticks (&#96;) or begin a line with four spaces in these sections. If the bot finds more (or less) than 1 `<code>` tag in the wiki page body, it will print an error message and exit.

Since alignment is important in YAML files, you may find the following CSS snippet useful. It changes the editing area of the wiki config page (as well as of the subreddit's stylesheet) to a monospaced font. Replace `[your_wiki_config_page_name_here]` with the name you gave for `WIKI_CONFIG_PAGE` in the local config file.

```CSS
/* Make the textareas for editing code-type wiki pages monospaced (IRCR_Info_Bot config, stylesheet from wiki, stylesheet from settings) */
.wiki-page-[your_wiki_config_page_name_here] #wiki_page_content, .wiki-page-config-stylesheet #wiki_page_content, #subreddit_stylesheet #stylesheet_contents {font-family: monospace}
```

At its top level, the wiki config file is a dictionary with the following 13 items:

#### NORMALSTRING

The bot's comment is formatted as a bulleted list with one line for each mentioned user. The username is automatically included at the beginning of the line with a link to their profile, formatted in such a way as to not send them a mention notification.

This is the informational string that the bot includes in its comment for every mentioned user who's account is still valid (ie, not deleted, suspended, or shadowbanned). It is blindly concatenated to the end of the username link described above, so this should probably start with some kind of separator (The example file uses ‘colon space’). (This is true of all the informational string values, including `MOD_REMARK`, `DEADUSER`, and `SPECIALS`. The relevant remarks are put together with regular old string concatenation.)

This value supports the following variables:

**{username}**: username

**{age}**: Account age in years, months, and days. For example, `2y 8m 20d` for 2 years, 8 months, and 20 days.

**{karma}**: Account link and comment karma, grouped by thousands when applicable. For example, `277/12.4k` for 277 link karma and about 12400 comment karma.

**{prevcount}**: The number of previous mentions of this user (or their aliases) in the database.

**{searchquery}**: A query for Reddit's search engine to get a list of previous mentions, including aliases. For example, a URL suitable version of `/u/user2 OR /u/alt_of_user2`. See the example file for an example of usage.


#### MOD_REMARK

If a mentioned user is a moderator of any of the subreddits in `SPECIAL_MOD_SUBS`, this string will be added to the end of the information about them, after both the normal remark (either `NORMALSTRING` or `DEADUSER`) and any special remark (from `SPECIALS`). Like `NORMALSTRING`, `DEADUSER`, and `SPECIALS`, this remark is just concatenated on the end, so it should probably start with some kind of separator (the example file uses ‘space pipe space’). It supports the following variable:

**{sublist}**: The list of the subreddits from `SPECIAL_MOD_SUBS` that the user moderates (formatted as "/r/pics, /r/funny, and /r/conspiracy").


#### DEADUSER

If a mentioned user's account is not valid (ie, has been deleted, suspended, or shadowbanned) this value is used instead of `NORMALSTRING`.

This value supports the **`{username}`** and **`{prevcount}`** variables, which have the same meanings as in `NORMALSTRING`.


#### ALIASES

This value can be used to keep track of users who have known alt/sockpuppet/alias accounts. It's formatted as a list of lists. Each element (a list) of the first-level list represents one physical person. Each item in the sub-list is the username of an account used by that person. The first item in the sub-list is the “normal” username of that person. If a person has entries in both `ALIASES` and `SPECIALS`, the `SPECIALS` key must be the normal name.


#### HEADER

This value will be put at the very top of the bot's comment, before anything else.


#### COLLAPSIBLE_HEADER

If there is more than one mentioned user that the bot is reporting on, this value will be put after the `HEADER` and before any of the user information. You can put any collapsible comment trickery here if your subreddit CSS supports that. Otherwise, it can be an empty string.


#### COLLAPSIBLE_FOOTER

If there is more than one mentioned user that the bot is reporting on, this value will be put before the `FOOTER` and after any of the user information. You can put any collapsible comment trickery here if your subreddit CSS supports that. Otherwise, it can be an empty string.


#### FOOTER

This value will be put at the very bottom of the bot's comment, after anything else. This would be a good place to put a link to the bot's source code, a FAQ, or how to contact the person in charge of the bot.


#### SPECIALS

This value can be used to give some individual users an extra remark. It's formatted as a map, where a key is a username (or “normal” username, if the person has an entry in `ALIASES`) and the corresponding value is the extra remark they get. This remark comes after the normal remark (either `NORMALSTRING` or `DEADUSER`) and before any moderator remark (`MOD_REMARK`). Like `NORMALSTRING`, `MOD_REMARK`, and `DEADUSER`, this remark is just concatenated on the end, so it should probably start with some kind of separator (the example file uses ‘space pipe space’). It supports the following variable:

**{username}**: The user's name, which may be different than the key if the user is an alias.


#### SPECIAL_MOD_SUBS

A list of subreddits to keep track of moderators of. If a detected user is a moderator of any of these subreddits, they get the extra `MOD_REMARK` remark.

When the bot is started, it loads the moderator lists of all of these subreddits and saves them to a file called `mod_list_cache.pickle`. Because of Reddit's API rules on rate limiting, this can take a while. If the file already exists and you don't want to update it, you can run the bot with the `--cache` or `-c` command line option to load the moderator lists from this file rather than downloading them.

If any of these subreddits are quarantined, the bot account must be manually opted-in to each of them in order to access their moderator list. The bot will print out a message if it finds a subreddit in this list that it can't access.


#### DISTINGUISHCOMMENT

Whether the bot should distinguish (mark as an official moderator action) the comments it makes. `true` for yes, `false` for no. Obviously, the bot has to actually be a moderator of the subreddit it's running on for this to work.


#### WAIT

The number of seconds to sleep between fetching and scanning new posts. This doesn't take into account the two second wait between requests required by Reddit's API rules.


#### MAXPOSTS

The maximum number of posts to fetch and scan at a time. This can be up to 1000, but numbers higher than 100 will require multiple requests.

If your subreddit ever gets more than [`MAXPOSTS`] posts in a period of less than [`WAIT`] seconds, some posts may be missed.
