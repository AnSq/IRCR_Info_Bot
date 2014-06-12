/u/IRCR_Info_Bot
================

[/u/IRCR_Info_Bot](http://www.reddit.com/user/IRCR_Info_Bot) on [/r/isrconspiracyracist](http://www.reddit.com/r/isrconspiracyracist).

Scans for usernames in post titles and comments with information about them.

Originally written by [/u/GoldenSights](http://www.reddit.com/user/GoldenSights) ([original code](https://github.com/voussoir/reddit/blob/master/TitleNames/titlenames.py)), now maintainted by the moderators of [/r/isrconspiracyracist](http://www.reddit.com/r/isrconspiracyracist).

Settings are stored in `config.py`.

For automatic login, create a file called `auth.py` that looks like this:

    USERNAME = "IRCR_Info_Bot"
    PASSWORD = "BOT-PASSWORD"

If defined, the environment variables `IRCR_USERNAME` and `IRCR_PASSWORD` override these settings.

Use the `--test` (or `-t`) flag to turn on testing mode. The bot will not post comments in testing mode.

Use the `--multi` (or `-m`) flag to connect to `praw-multiprocess` if you're running other reddit bots at the same time. ([More info in the praw docs.](http://praw.readthedocs.org/en/latest/pages/multiprocess.html))

To not even attempt logging in, use the `--nologin` (or `-n`) flag (implies `--test`).

To use PostgreSQL instead of SQLite use the `--postgres` (or `-p`) flag. (Mainly for Heroku.) Requires that a `DATABASE_URL` environment variable be defined in the form `postgres://<username>:<password>@<host>:<port>/<database>`.

The argument parsing isn't all that sophisticated, so, for example, `-mn` is *not* a synonym for `-m -n`.
