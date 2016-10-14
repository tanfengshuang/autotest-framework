"""
@author		: qianzhan@redhat.com
@date		: 2013-03-12
"""

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID178500_bind_and_unbind_action_in_syslog(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		#register
		eu().sub_register(session,username,password)

		#list availalbe entitlement pools
		productid = ee().get_env(params)["productid"]
		availpoollist = eu().sub_listavailpools(session, productid)

		#get an available entitlement pool to subscribe with random.sample
		availpool = random.sample(availpoollist, 1)[0] 
		if "SubscriptionName" in availpool:
			poolid = availpool["PoolID"]
			subscriptionname = availpool["SubscriptionName"]
			productid = availpool["SKU"]
		   
		#subscribe the product with poolid
		cmd = "subscription-manager subscribe --pool=%s" %poolid
		(ret, output) = eu().runcmd(session, cmd, "subscribe with poolid")
		expectout = "Successfully consumed a subscription for: %s" %subscriptionname
		#expectoutnew is for rhel new feature output
		expectoutnew = "Successfully attached a subscription for: %s" %subscriptionname
		if 0 == ret and ((expectout in output) or (expectoutnew in output)):
			logging.info("It's successful to do subscribe to a pool")
		else:
			logging.error("Test Failed - error happened when do subscribe to a pool")
	
		#get the entitlement cert name
		cmd="ls /etc/pki/entitlement/*.pem | grep -v key.pem"
		(ret,certname0)=eu().runcmd(session,cmd,"get the entitlement cert name")
		if (ret==0) and (certname0 != None):
			logging.info("It's successful to get the entitlement cert name")
			certname=certname0.strip('\n')
		else:
			raise error.TestFail("Test Failed - Failed to get the entitlement cert name")
	
		#check the syslog for subscribe info
		cmd="tail -100 /var/log/rhsm/rhsm.log | grep Deleted -B10 |grep Added -A10 | grep '%s'" %certname
		(ret,loginfo)=eu().runcmd(session,cmd,"check the syslog for subscribe info")
		if ret==0 and loginfo!=None:
			logging.info("It's successful to check the syslog for subscribe info")
		else:
			raise error.TestFail("Test Failed - Failed to check the syslog for subscribe info")

		#unsubscribe
		eu().sub_unsubscribe(session)
	
		#check the syslog for unsubscribe info
		cmd="tail -100 /var/log/rhsm/rhsm.log | grep Deleted -A10 | grep '%s'"%certname
		(ret,loginfo)=eu().runcmd(session,cmd,"check the syslog for subscribe info")
		if ret==0 and loginfo!=None:
			logging.info("It's successful to check the syslog for unsubscribe info")
		else:
			raise error.TestFail("Test Failed - Failed to check the syslog for unsubscribe info")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check whether certs come back correctly:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
