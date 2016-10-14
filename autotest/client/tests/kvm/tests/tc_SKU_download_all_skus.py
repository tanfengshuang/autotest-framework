import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.skutest.skutest import *
from autotest_lib.client.tests.kvm.tests.skutest.download_all_skus import *

def run_tc_SKU_download_all_skus(test, params, env):
	session,vm=eu().init_session_vm(params,env)
	
	logging.info("=========================== Begin of Running Test Case: %s ========================="%__name__)

	try:         
                # sku testing
		stage_url = "https://subscription.rhn.stage.redhat.com/subscription/products/"	
		download_path = "/tmp/sku_download"
		download_all_skus(session, params, stage_url, download_path, 'redhat')
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do sku testing:"+str(e))
	finally:
		logging.info("========================= End of Running Test Case: %s ========================="%__name__)

