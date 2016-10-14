import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115163_registerwithconsumerid(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		
		#auto-subscribe a subscription
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		#get serialnumlist before remove local subscription data
		serialnumlist_pre = eu().get_subscription_serialnumlist(session)

		#get uuid of consumer
		cmd="subscription-manager identity | grep identity"
		(ret,output) = eu().runcmd(session, cmd, "get the current identity")
		uuid=output.split(':')[1].strip()

		#remove all local consumer and subscription data
		cmd="subscription-manager clean"
		(ret,output) = eu().runcmd(session,cmd,"clean local consumer and subscription data")

		if ret == 0 and "All local data removed" in output:
			#register with consumerid 
			cmd="subscription-manager register --consumerid=%s --username=%s  --password=%s"%(uuid, username, password)
			(ret,output) = eu().runcmd(session,cmd,"register with consumerid")
			successregister1 = "The system has been registered with id: %s" %uuid
			successregister2 = "The system has been registered with ID: %s" %uuid
			if ret == 0 and ((successregister2 in output) or (successregister1 in output)):
				logging.info("It's successful to register with consumerid")
				#get serialnumlist after register with consumerid
				serialnumlist_post = eu().get_subscription_serialnumlist(session)
				if len(serialnumlist_post) == len(serialnumlist_pre) and (serialnumlist_post.sort() == serialnumlist_pre.sort()):
					logging.info("It's successful to download consumed subscription data")
				else:
					raise error.TestFail("Test Failed - Failed to download consumed subscription.")
			else:
				raise error.TestFail("Test Failed - Failed to register with consumerid.")
		else:
			raise error.TestFail("Test Failed - Failed to remove all local data.")

        except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened when do register with consumerid:"+str(e))
        finally:
                eu().sub_unregister(session)
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
