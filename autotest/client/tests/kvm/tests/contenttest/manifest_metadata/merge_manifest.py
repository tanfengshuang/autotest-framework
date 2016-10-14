#!/bin/env python

import sys
import simplejson as json

def merge_manifest(base, manifests=[]):
    bj = json.load(file(base))

    for m in manifests:
        mj = json.load(file(m))

        # merge repo
	if bj.has_key("cdn") and mj.has_key("cdn"):
            for pid in mj["cdn"]["products"]:
                if bj["cdn"]["products"].has_key(pid):
                    # comment below three lines if you want to use 'Product Version' in base manifest.
                    if bj["cdn"]["products"][pid]["Product Version"] != mj["cdn"]["products"][pid]["Product Version"]:
                        print "[ERROR] 'Product Version' of %s different in %s & %s" % (pid, base, m)
                        return False
    
                    for url in mj['cdn']['products'][pid]['Repo Paths']:
                        if bj['cdn']['products'][pid]['Repo Paths'].has_key(url):
                            # return if the repo(url) already exists in base manifest
                            print "[ERROR] repo %s of %s exists in %s & %s" % (url, pid, base, m)
                            return False
                        else:
                            # merge repo into base manifest
                            bj['cdn']['products'][pid]['Repo Paths'][url] = mj['cdn']['products'][pid]['Repo Paths'][url]
                else:
                    # merge if product not in base manifest
                    bj["cdn"]["products"][pid] = mj["cdn"]["products"][pid]

        # merge rhn
	if bj.has_key("rhn") and mj.has_key("rhn"):
            for chn in mj["rhn"]["channels"]:
                if bj["rhn"]["channels"].has_key(chn):
                    # return if the channel already exists in base manifest
                    print "[ERROR] channel %s exists in %s & %s" % (chn, base, m)
                    return False
                else:
                    # merge channel into base manifest
                    bj["rhn"]["channels"][chn] = mj["rhn"]["channels"][chn]
    

    print json.dumps(bj, indent=4)
    return True

def usage():
    print "Usage: python %s manifest1 manifest2 [manifest3 ...] > new_manifest.json" % sys.argv[0]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    if merge_manifest(sys.argv[1], sys.argv[2:]):
        sys.exit(0)
    else:
        sys.exit(2)

