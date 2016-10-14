import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115188_stacking_in_one_step(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
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

		#prepare product cert
		cmd="rm -f /etc/pki/product/*.pem"
		(ret,output)=eu().runcmd(session,cmd,"remove current product cert")

		cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%(ee().get_env(params)["pid"])
		(ret,output)=eu().runcmd(session,cmd,"copying specific product cert to cert dir")

		#list available entitlement pools
		productid = ee().get_env(params)["productid"]
		productname = ee().get_env(params)["productname"]
		productidME = ee().get_env(params)["productidME"]
		availpoollist = eu().sub_listallavailpools(session,productid)

		#get an available multi-entitlement pool with a stacking id
		length = len(availpoollist)
		for index in range(0, length):
			if availpoollist[index]["SKU"] == productidME:
				rindex=index
				break
		poolid=availpoollist[rindex]["PoolID"]

		#subscribe to the pool with 4 quantities
		sub_subscribetopool(session,poolid)

		#check the compliance of installed product should be Subscribed
		cmd="subscription-manager list"
		(ret,output)=eu().runcmd(session,cmd,"list installed product")

		if ret == 0 and productname in output and "Partially" not in output and "Not" not in output and "Subscribed" in output:
			logging.info("It's successful to display the compliance status of Subscribed.")
		else:
			raise error.TestFail("Test Failed - Failed to display the compliance status of Subscribed.")
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do stack in one step:"+str(e))
	finally:
		eu().runcmd(session,'rm -f /etc/rhsm/facts/custom.facts', "")
		eu().runcmd(session,'subscription-manager facts --update', "")
		eu().sub_unregister(session)
		cmd="rm -f /etc/pki/product/*.pem"
		(ret,output)=eu().runcmd(session,cmd,"remove current product cert")
		cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%ee.pidcc
		(ret,output)=eu().runcmd(session,cmd,"copying default product cert to cert dir")
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def sub_subscribetopool(session,poolid):
	cmd="subscription-manager subscribe --pool=%s --quantity=4"%(poolid)
	(ret,output)=eu().runcmd(session,cmd,"subscribe")

	if ret == 0:
		if "Successfully " in output:
			logging.info("It's successful to subscribe.")
		else:
			raise error.TestFail("Test Failed - The information shown after subscribing is not correct.")
	else:
		raise error.TestFail("Test Failed - Failed to subscribe.")
