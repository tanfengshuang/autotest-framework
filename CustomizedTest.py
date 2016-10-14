##@ Summary: Execute Customized Test
##@ Description: Assign supercmd for submit jobs in Virtlab by staf cmdline
##@ Maintainer: Amos Kong <akong@redhat.com>
##@ Updated:    Mon May 10, 2010
##@ Version:    1

import sys, os, re
import wrapper

if __name__ == "__main__":

    argv = ' '.join(sys.argv)
    if "--supercmd" not in argv:
        print 'Usage: python %s --supercmd=... ...' % sys.argv[0]
        sys.exit(1)
    supercmd = re.findall("--supercmd=(.*)$", argv)[0]
    print "Execute Super Command: %s" % supercmd
    os.system("%s" % supercmd)
