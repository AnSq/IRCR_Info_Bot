#!/usr/bin/python

import sys
import cPickle

import IRCR_Info_Bot as ircr


fname = "mod_list_cache.pickle"


def main(r=None):
    if r == None:
        multi = len(sys.argv) > 1 and (sys.argv[1]=="-m" or sys.argv[1]=="--multi")
        r = ircr.reddit_connect(ircr.config.USERAGENT + " (script-manual mod_list loader mode)", multi)
    multi = len(sys.argv) > 1 and (sys.argv[1]=="-m" or sys.argv[1]=="--multi")

    mod_list = ircr.load_mod_list(ircr.config.SPECIAL_MOD_SUBS, r, True)

    print "Saving mod list to `%s`." % fname
    f = open(fname, "w")
    cPickle.dump(mod_list, f)
    f.close()


if __name__ == "__main__":
    main()
