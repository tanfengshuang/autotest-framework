import sys, os, subprocess, commands, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129549_import_one_manifest_to_two_organizations(test, params, env):

	session,vm=eu().init_session_vm(params,env)

        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        try:
                #create two orgs
                orgname1 = ee.org1 + time.strftime('%Y%m%d%H%M%S')
                eu().sam_create_org(session, orgname1)
		orgname2 = orgname1 + "1"
		eu().sam_create_org(session, orgname2)

                #import a manifest to the org1
                manifest="/tmp/samtest/%s"%ee.manifest1
                eu().sam_import_manifest_to_org(session, manifest, orgname1, ee.default_provider)

                #import the manifest to another org
                cmd="headpin -u admin -p admin provider import_manifest --org=%s --name='%s' --file=%s"%(orgname2, ee.default_provider, manifest)
		(ret,output)=eu().runcmd(session,cmd,"import manifest")

        except Exception, e:

                if "Timeout expired while waiting for shell command to complete:" in str(e):

                        if "This distributor has already been imported by another owner" in str(e):
				logging.info(str(e))
                                logging.info("It's successful to verify that one manifest can't be imported to two orgs.")
                        else:
				logging.error(str(e))
                                raise error.TestFail("Test Failed - One manifest shouldn't be imported to two orgs.")
                else:
			logging.error(str(e))
                        raise error.TestFail("Test Failed - error happened when do import one manifest to two orgs:"+str(e))
        finally:
                eu().sam_delete_org(session, orgname1)
                eu().sam_delete_org(session, orgname2)
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
