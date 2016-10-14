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

def run_tc_ID178503_only_one_cert_with_each_subscription(test, params, env):
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

		#get the number of entitlement cert
		cmd="ls /etc/pki/entitlement | grep -v key.pem | wc -l"
		(ret,number)=eu().runcmd(session,cmd,"get the number of entitlement cert")
		if (ret==0) and (number.strip('\n')=="1"):
			logging.info("It's successful to verify that only one entitlement certificate is produced for each subscription to an entitlement pool")
		else:
			raise error.TestFail("Test Failed - Failed to verify that only one entitlement certificate is produced for each subscription to an entitlement pool")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check whether certs come back correctly:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

