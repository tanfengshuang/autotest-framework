import sys, os, subprocess, commands, random, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115119_healing_for_compliance_broken(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#prepare product cert
	cmd="rm -f /etc/pki/product/*.pem"
	(ret,output)=eu().runcmd(session,cmd,"remove current product cert")

	cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%(ee().get_env(params)["pid"])
	(ret,output)=eu().runcmd(session,cmd,"copying specific product cert to cert dir")
	rindex = 0
	

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]	
		eu().sub_register(session,username,password)   
		
		#generate custom facts
		cmd="""echo '{"cpu.cpu_socket(s)":4}' > /etc/rhsm/facts/custom.facts"""
		(ret,output)=eu().runcmd(session,cmd,"generate custom facts")

		#update facts of cpu.cpu_sockets
		cmd="subscription-manager facts --update"
		(ret,output)=eu().runcmd(session,cmd,"update custom facts")

		#list available entitlement pools
		productid = ee().get_env(params)["productid"]
		productidME = ee().get_env(params)["productidME"]
		productname = ee().get_env(params)["productname"]
		availpoollist = eu().sub_listallavailpools(session,productid)

		#get an available multi-entitlement pool with a stacking id
		length = len(availpoollist)
		for index in range(0, length):
			if availpoollist[index]["SKU"] == productidME:
				rindex=index
				break
		poolid=availpoollist[rindex]["PoolId"]

		#subscribe to the pool with 2 quantities
		sub_subscribetopool(session,poolid)

		#check the compliance of installed product should be Partially Subscribed
		cmd="subscription-manager list"
		(ret,output)=eu().runcmd(session,cmd,"list installed product")

		if ret == 0 and productname in output and "Partially Subscribed" in output:
			logging.info("It's successful to display the compliance status of Partially Subscribed.")
		else:
			raise error.TestFail("Test Failed - Failed to display the compliance status of Partially Subscribed.")

		#change healing frequancy
		cmd="subscription-manager config --rhsmcertd.healfrequency=1"
		(ret,output)=eu().runcmd(session,cmd,"change healfrequency to be 1 min")

		cmd="service rhsmcertd restart"
		(ret,output)=eu().runcmd(session,cmd,"restart rhsmcerts to make it work")

		#Check compliance status after healing
                time.sleep(90)
		cmd="subscription-manager list"
		(ret,output)=eu().runcmd(session,cmd,"list installed product")

		if ret == 0 and productname in output and "Partially" not in output and "Not" not in output and "Subscribed" in output:
			logging.info("It's successful to display the compliance status of Subscribed.")
		else:
			raise error.TestFail("Test Failed - Failed to display the compliance status of Subscribed.")

		cmd="subscription-manager list --consumed"
		(ret,output)=eu().runcmd(session,cmd,"list consumed subscriptions")

		cmd="subscription-manager list --consumed|grep \"%s\" |wc -l" %productname
		(ret,output)=eu().runcmd(session,cmd,"check healed subscription")

		if ret == 0 and int(output) >= 2:
			logging.info("It's successful to heal when compliance status is broken.")
		else:
			raise error.TestFail("Test Failed - Failed to heal when compliance status is broken.")
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do heal for broken compliance status:"+str(e))
	finally:
		eu().runcmd(session, 'rm -f /etc/rhsm/facts/custom.facts', "")
		eu().runcmd(session, 'subscription-manager facts --update', "")
		eu().sub_unregister(session)
		cmd="rm -f /etc/pki/product/*.pem"
		(ret,output)=eu().runcmd(session,cmd,"remove current product cert")
		cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%ee.pidcc
		(ret,output)=eu().runcmd(session,cmd,"copying default product cert to cert dir")
		cmd="subscription-manager config --rhsmcertd.healfrequency=1440"
		(ret,output)=eu().runcmd(session,cmd,"change healfrequency to be 1 day")
		cmd="service rhsmcertd restart"
		(ret,output)=eu().runcmd(session,cmd,"restart rhsmcerts to make it work")

		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def sub_subscribetopool(session,poolid):
	cmd="subscription-manager subscribe --pool=%s --quantity=2"%(poolid)
	(ret,output)=eu().runcmd(session,cmd,"subscribe")

	if ret == 0:
		if "Successfully " in output:
			logging.info("It's successful to subscribe.")
		else:
			raise error.TestFail("Test Failed - The information shown after subscribing is not correct.")
	else:
		raise error.TestFail("Test Failed - Failed to subscribe.")
