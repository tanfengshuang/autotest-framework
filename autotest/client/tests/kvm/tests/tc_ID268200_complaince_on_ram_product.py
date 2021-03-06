import sys, os, subprocess, commands, random, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID268200_complaince_on_ram_product(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#prepare product cert
	cmd="rm -f /etc/pki/product/*.pem"
	(ret,output)=eu().runcmd(session,cmd,"remove current product cert")

	cmd="cp -rf \"/etc/pki/product/tmp/801.pem\" \"/etc/pki/product/\""
	(ret,output)=eu().runcmd(session,cmd,"copying specific product cert to cert dir")
	oldtime = ""
	rindex = 0

	try:   
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]	
		eu().sub_register(session,username,password)
		
		factsupdate(session, "memory.memtotal","8000000")
		
		#list available entitlement pools
		#productid=ee.productid2cc
		productid = ee().get_newproduct("ram")["productidstack"]
		productname = ee().get_newproduct("ram")["productname"]
		availpoollist = eu().sub_listallavailpools(session,productid)

		#get an available pool
		length = len(availpoollist)
		for index in range(0, length):
			if (availpoollist[index]["SKU"] == productid):
				rindex = index
				break
		poolid = availpoollist[rindex]["PoolID"]

		#subscribe to the pool
		eu().sub_subscribetopool(session,poolid)
		
		checkstatus(session, "Insufficient")
		checkinstalled(session, "Partially Subscribed")
		
		eu().sub_subscribetopool(session,poolid)
		checkstatus(session, "Current")
		checkinstalled(session, "Subscribed")
		
		factsupdate(session, "memory.memtotal","12000000")
		checkstatus(session, "Insufficient")
		checkinstalled(session, "Partially Subscribed")		
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do heal for expiration:"+str(e))
	finally:
		cmd="rm -f /etc/pki/product/*.pem"
		(ret,output)=eu().runcmd(session,cmd,"remove current product cert")
		cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%ee.pidcc
		(ret,output)=eu().runcmd(session,cmd,"copying default product cert to cert dir")
		factsupdate(session, "", "")
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		

def factsupdate(session, facts, data):
	if facts and data:		
		cmd = "echo '{\"%s\":\"%s\"}'  > /etc/rhsm/facts/custom.facts" %(facts, data)
		(ret, output) = eu().runcmd(session,cmd,"echo custom.facts")
		if ret == 0:
			logging.info("It's successful to echo custom.facts.")
		else:
			raise error.TestFail("Test Failed - Failed to echo custom.facts.")
			
		cmd = "subscription-manager facts --update"
		(ret,output)=eu().runcmd(session,cmd,"update system facts")
		if ret == 0 and "Successfully updated the system facts" in output:
			logging.info("It's successful to update system facts.")
		else:
			raise error.TestFail("Test Failed - Failed to echo custom.facts.")
	else:
		cmd = "rm -f /etc/rhsm/facts/custom.facts"
		(ret, output) = eu().runcmd(session,cmd,"clean custom.facts")
		if ret == 0:
			logging.info("It's successful to clean custom.facts.")
		else:
			raise error.TestFail("Test Failed - Failed to clean custom.facts.")
		cmd = "subscription-manager facts --update"
		(ret,output)=eu().runcmd(session,cmd,"update system facts")
		if ret == 0 and "Successfully updated the system facts" in output:
			logging.info("It's successful to update system facts.")
		else:
			raise error.TestFail("Test Failed - Failed to echo custom.facts.")

def checkstatus(session, status):
	cmd = "subscription-manager status"
	(ret, output) = eu().runcmd(session, cmd, "list system status")
	if ret ==0 and status in output:
		logging.info("It successful to check the system status")
	else:
		raise error.TestFail("Test Failed - Failed to check the system status")
			
def checkinstalled(session, status):
	cmd = "subscription-manager list --installed"
	(ret, output) = eu().runcmd(session, cmd, "list system installed products")
	if ret ==0:
		if "Partially" in status and status in output:
			logging.info("It successful to check the system installed products")
		elif status in output and "Partially" not in output:
			logging.info("It successful to check the system installed products")
		else:
			raise error.TestFail("Test Failed - Failed to check the system installed products")
	else:
		raise error.TestFail("Test Failed - Failed to check the system installed products")
