##@ Summary: Reserve Machine From Virtlab
##@ Description: Eliminate the efforts of sending ticket
##@ Maintainer: Jason Wang <jasowang@redhat.com>
##@ Updated:     Sat Sep 12, 2009
##@ Version:    2

import signal

if __name__ == "__main__":

    # sleep for 60 days, if the user want to release the machine, 
    # just stop the job
    signal.pause()
    
    
