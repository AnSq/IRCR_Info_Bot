# /u/IRCR_Info_Bot

[/u/IRCR_Info_Bot](http://www.reddit.com/user/IRCR_Info_Bot) on [/r/isrconspiracyracist](http://www.reddit.com/r/isrconspiracyracist).

Scans for usernames in post titles and comments with information about them.

Originally written by [/u/GoldenSights](http://www.reddit.com/user/GoldenSights) ([original code](https://github.com/voussoir/reddit/blob/68b45302fb9fd8129a0ebc41f936ebbb08bad0f3/TitleNames/titlenames.py)), now maintained by the moderators of [/r/isrconspiracyracist](http://www.reddit.com/r/isrconspiracyracist).


## Bot Operation

Run with `python IRCR_Info_Bot.py [options]`.

Settings are stored in `config.py`.

The environment variables `IRCR_USERNAME` and `IRCR_PASSWORD` are used to log in.

Use the `--test` (or `-t`) flag to turn on testing mode. The bot will not post comments in testing mode.

Use the `--multi` (or `-m`) flag to connect to `praw-multiprocess` if you're running other reddit bots at the same time. ([More info in the praw docs.](http://praw.readthedocs.org/en/latest/pages/multiprocess.html))

To not even attempt logging in, use the `--nologin` (or `-n`) flag (implies `--test`).

To use PostgreSQL instead of SQLite use the `--postgres` (or `-p`) flag. (Mainly for Heroku.) Requires that a `DATABASE_URL` environment variable be defined in the form `postgres://<username>:<password>@<host>:<port>/<database>`.

The argument parsing isn't all that sophisticated, so, for example, `-mn` is *not* a synonym for `-m -n`.


## Manual Operation

You can manually generate a comment based on a list of usernames using the `manual.py` script. This script will print out a comment to the console. It will not post it.

Run it with `python manual.py [--multi|-m] [users]`.

In order to use the moderator remark feature of the bot, the sctipt has to download the moderator lists first. With reddit's API rules, this can take a while, so the script first trys to load them from a cache. If the cache doesn't exist, it will download the lists and create it. You can manually generate or refresh the cache by running `python get_mod_list.py [--multi|-m]`.
