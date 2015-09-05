#!/usr/bin/python

import sys
import cPickle

import IRCR_Info_Bot as ircr


fname = "mod_list_cache.pickle"


def main(r=None):
    if r == None:
        multi = "-m" in sys.argv or "--multi" in sys.argv
        r = ircr.reddit_connect(ircr.config.USERAGENT + " (script-manual mod_list loader mode)", multi)

    nologin = "-n" in sys.argv or "--nologin" in sys.argv
    if not nologin:
        ircr.login(r)

    mod_list = ircr.load_mod_list(ircr.config.SPECIAL_MOD_SUBS, r, True)

    print "Saving mod list to `%s`." % fname
    f = open(fname, "w")
    cPickle.dump(mod_list, f)
    f.close()


if __name__ == "__main__":
    main()
