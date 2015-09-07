# /u/IRCR_Info_Bot

[/u/IRCR_Info_Bot](http://www.reddit.com/user/IRCR_Info_Bot) on [/r/isrconspiracyracist](http://www.reddit.com/r/isrconspiracyracist).

Scans posts and summoning comments for usernames and replies with information about them.

Originally written by [/u/GoldenSights](http://www.reddit.com/user/GoldenSights) ([original code](https://github.com/voussoir/reddit/blob/68b45302fb9fd8129a0ebc41f936ebbb08bad0f3/TitleNames/titlenames.py)), now maintained by the moderators of [/r/isrconspiracyracist](http://www.reddit.com/r/isrconspiracyracist).


## Bot Operation

Run with `python IRCR_Info_Bot.py [options]`.

Settings are stored in [`config.py`](https://github.com/AnSq/IRCR_Info_Bot/blob/master/config.py). Descriptions of each setting can be found in the comments of that file.

The file `oauth.ini` is used to log in. See [the praw-OAuth2Util documentation](https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md#config) for more information.

Use the `--test` (or `-t`) flag to turn on testing mode. The bot will not post comments in testing mode.

Use the `--cache` (or `-c`) flag to load the moderator list from cache instead of downloading it. See the "Manual Operation" section below for more information.

Use the `--multi` (or `-m`) flag to connect to `praw-multiprocess` if you're running other reddit bots at the same time. ([More info in the praw docs.](http://praw.readthedocs.org/en/latest/pages/multiprocess.html))

To not even attempt logging in, use the `--nologin` (or `-n`) flag (implies `--test`).

To use PostgreSQL instead of SQLite use the `--postgres` (or `-p`) flag. Requires that a `DATABASE_URL` environment variable be defined in the form `postgres://<username>:<password>@<host>:<port>/<database>`.

The script also supports `--help` (or `-h`) to show a summary of options and `--version` (or `-v`) to show the version number.


## Summoning

The bot can be summoned to post information about additional users not in the title by posting a comment beginning with “+/u/*[bot-username]*” or “+ircrbot”. Everything after this is scanned for usernames exactly the same way submission titles are.

This only works in subreddits the bot is scanning submission in, as defined in `config.SUBREDDIT`.


## Manual Operation

*This functionality is currently undergoing maintenance and may be temporarily broken.*

You can manually generate a comment based on a list of usernames using the `manual.py` script. This script will print out a comment to the console. It will not post it.

Run it with `python manual.py [--multi|-m] [users]`.

In order to use the moderator remark feature of the bot, the sctipt has to download the moderator lists first. With reddit's API rules, this can take a while, so the script first trys to load them from a cache. If the cache doesn't exist, it will download the lists and create it. You can manually generate or refresh the cache by running `python get_mod_list.py`.

With Reddit's new quarantine system, the bot can't get the moderators of some subreddits without being manually opted-in to them and logged in. Loggin in for `get_mod_list` works the same as for the main bot. `get_mod_list.py` also accepts the `--nologin` (or `-n`) argument, in which case the mods of quarantined subs won't be loaded, and of course the `--multi` (or `-m`) argument. `manual.py` does not support `--nologin`, so if you want it to use mods of quarantined subs, run `get_mod_list` logged in first to generate the cache.
