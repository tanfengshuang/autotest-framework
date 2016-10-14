contenttestrun()
{
  execute
  archive
}

execute()
{
  rlPhaseStartTest "Execute Content Test"
    if [ "$host_arch" == "ppc64" ] || [ "$host_arch" == "s390x" ] ; then
    	guestname="RHEL-$variant-$host_arch-$release"
    else
    	guestname="RHEL-$variant-$release"
    fi
    manifest="$MANIFEST"

    # Testing against stage or production for content
    
    if [ "$CONTENT" == "QA" ] ; then
	baseurl="https://cdn.rcm-qa.redhat.com"
	rlLog "Testing content against $CONTENT CDN"
    fi
    if [ "$CONTENT" == "PROD" ] ; then
	baseurl="https://cdn.redhat.com"
	rlLog "Testing content against $CONTENT CDN"
    fi

   # Testing against stage or production for subscriptions
   if [ "$CANDLEPIN" == "STAGE" ] ; then
	candlepin="subscription.rhn.stage.redhat.com"
	rlLog "Testing subscriptions against $CANDLEPIN"
   fi

   if [ "$CANDLEPIN" == "PROD" ] ; then
	candlepin="subscription.rhn.redhat.com"
	rlLog "Testing subscriptions against $CANDLEPIN"
   fi

   cd ./autotest
   rlRun "python ConfigLoop.py --category=entitlement_content_test_for_rhel --guestname=$guestname --platform=$platform --baseurl=$baseurl --hostname=$candlepin --content_level=level1,level2 --runcasein=host --manifest_url=$manifest"
  rlPhaseEnd 
}

archive()
{
  rlPhaseStartTest "Archive the Test Results"
    # mount the archive location
    rlRun "mkdir /ent" 0 "Create a directory to mount archive location"
    rlRun "mount hp-z220-11.qe.lab.eng.nay.redhat.com:/data/logs/content/log /ent" 0 "Mount the archive location hp-z220-11.qe.lab.eng.nay.redhat.com:/data/logs/content/log"
    # create a unique archive location
    ls /ent/$guestname/
    if [ $? -ne 0 ] ; then
    	rlRun "mkdir /ent/$guestname/" 0 "Create a unique directory for $guestname/"
	rlRun "mkdir /ent/$guestname/$CONTENT/" 0 "Create a directory for content on $CONTENT CDN"
    else
    	ls /ent/$guestname/$CONTENT/
	if [ $? -ne 0 ] ; then
	    rlRun "mkdir /ent/$guestname/$CONTENT/" 0 "Create a directory for content on $CONTENT CDN"
	fi
    fi
    NOW=`date +%m%d%y-%H%M%S`
    rlRun "mkdir /ent/$guestname/$CONTENT/$NOW" 0 "Create a unique directory for the date and time"
    rlRun "scp -r ./autotest/client/results/default/* /ent/$guestname/$CONTENT/$NOW" 0 "Copy results to /ent/$guestname/$CONTENT/$NOW"

    rlLog "You can view your results at http://hp-z220-11.qe.lab.eng.nay.redhat.com/logs/content/log/$guestname/$CONTENT/$NOW"
    rhts-submit-log -l ./autotest/client/results/default/job_report.html
  rlPhaseEnd
}
