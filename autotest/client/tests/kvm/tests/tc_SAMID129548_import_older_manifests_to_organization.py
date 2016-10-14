import sys, os, subprocess, commands, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129548_import_older_manifests_to_organization(test, params, env):

	session,vm=eu().init_session_vm(params,env)

        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        try:
                #create an org
                orgname = ee.org1 + time.strftime('%Y%m%d%H%M%S')
                eu().sam_create_org(session, orgname)

                #import a manifest to the org
                manifest="/tmp/samtest/%s"%ee.manifest2
                eu().sam_import_manifest_to_org(session, manifest, orgname, ee.default_provider)

                #import an older manifest to the org
                manifest="/tmp/samtest/%s"%ee.manifest1
                cmd="headpin -u admin -p admin provider import_manifest --org=%s --name='%s' --file=%s --force"%(orgname, ee.default_provider, manifest)
		(ret,output)=eu().runcmd(session,cmd,"import manifest")

        except Exception, e:

                if "Timeout expired while waiting for shell command to complete:" in str(e):

                        if "Import is older than existing data" in str(e):
				logging.info(str(e))
                                logging.info("It's successful to verify that older manifest can't be imported to org.")
                        else:
				logging.error(str(e))
                                raise error.TestFail("Test Failed - Older manifest shouldn't be imported to org.")
                else:
			logging.error(str(e))
                        raise error.TestFail("Test Failed - error happened when do import an older manifest to an org:"+str(e))
        finally:
                eu().sam_delete_org(session, orgname)
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
