import sys, os, subprocess, commands, random, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115118_healing_for_expiration(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#prepare product cert
	cmd="rm -f /etc/pki/product/*.pem"
	(ret,output)=eu().runcmd(session,cmd,"remove current product cert")

	cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%(ee().get_env(params)["pid"])
	(ret,output)=eu().runcmd(session,cmd,"copying specific product cert to cert dir")
	oldtime = ""
	rindex = 0

	try:   
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]	
		eu().sub_register(session,username,password)
		
		#list available entitlement pools
		#productid=ee.productid2cc
		productid = ee().get_env(params)["productid"]
		productname = ee().get_env(params)["productname"]
		availpoollist = eu().sub_listallavailpools(session,productid)

		#get an available pool
		length = len(availpoollist)
		for index in range(0, length):
			if (availpoollist[index]["SKU"] == productid):
				rindex=index
				break
		poolid=availpoollist[rindex]["PoolId"]

		#subscribe to the pool
		eu().sub_subscribetopool(session,poolid)

		#change current time to make entitlement expire within 24 hours
		oldtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		newtime="00:00:00 "+ee().get_env(params)["expires"] 
		cmd="date -s '%s'"%(newtime)
		(ret,output)=eu().runcmd(session,cmd,"set system time to be the expiration time")

		#change healing frequancy
		cmd="subscription-manager config --rhsmcertd.healfrequency=1"
		(ret,output)=eu().runcmd(session,cmd,"change healfrequency to be 1 min")

		cmd="service rhsmcertd restart"
		(ret,output)=eu().runcmd(session,cmd,"restart rhsmcerts to make it work")

		#Check compliance status after healing
		time.sleep(90)

		cmd="subscription-manager list --consumed"
		(ret,output)=eu().runcmd(session,cmd,"list consumed subscriptions")

		cmd="subscription-manager list --consumed|grep \"%s\" |wc -l" %productname
		(ret,output)=eu().runcmd(session,cmd,"check healed subscription")

		if ret == 0 and int(output) >= 2:
			logging.info("It's successful to heal when there is expired entitlement.")
		else:
			raise error.TestFail("Test Failed - Failed to heal when there is expired entitlement.")
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do heal for expiration:"+str(e))
	finally:
		cmd="rm -f /etc/pki/product/*.pem"
		(ret,output)=eu().runcmd(session,cmd,"remove current product cert")
		cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%ee.pidcc
		(ret,output)=eu().runcmd(session,cmd,"copying default product cert to cert dir")
		cmd="subscription-manager config --rhsmcertd.healfrequency=1440"
		(ret,output)=eu().runcmd(session,cmd,"change healfrequency to be 1 day")
		cmd="service rhsmcertd restart"	
		(ret,output)=eu().runcmd(session,cmd,"restart rhsmcerts to make it work")
		if oldtime != "":
			cmd="date -s '%s'"%(oldtime)
			(ret,output)=eu().runcmd(session,cmd,"set system time to be the normal time")
		eu().sub_unregister(session)

		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

