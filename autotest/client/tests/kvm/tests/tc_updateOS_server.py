import sys, os, subprocess, commands, random, re
import logging
import time
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_prod import ent_prod as ep
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_updateOS_server(test, params, env):
        session,vm=eu().init_session_vm(params,env)
        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        try:
                try:
                        #[A]Prepare test data

                        content_level=params.get("content_level")
                        baseurl=params.get("baseurl")
                        hostname=params.get("hostname")
                        samhostip=params.get("samhostip")
                        if ("stage" in hostname):
                                username=ee().get_env(params)["username"]
                                password=ee().get_env(params)["password"]
                                sku=ee().get_env(params)["productid"]
                                #productid='69'
                        else:
                                if ("https://samserv.redhat.com" in baseurl) and (samhostip != None):
                                        username="admin"
                                        password="admin"
                                else:
                                        username=ee.username_qa
                                        password=ee.password_qa
                                sku="SYS0395"
                                #productid='69,83,85,90,92'
                        productid_cont='69'

			release_list = params.get('release_list')

                        #[B]Run the test
                        (prodsku, basesku)=ep().cnt_get_prodsku_and_basesku(sku)
			refer_redhat_release = 'Red Hat Enterprise Linux Server release 6.4 (Santiago)'
			refer_kernel_version = 'kernel-2.6.32-358.2.1.el6'
			cmd='gconftool-2 --set /apps/gnome-packagekit/update-icon/frequency_get_updates --type=int 0'
			
			ep().cnt_updateOS_test(session, params, vm, env, username, password, prodsku, basesku, productid_cont, "", release_list, refer_redhat_release, refer_kernel_version)
                except Exception, e:
                        logging.error(str(e))
                        raise error.TestFail("Test Failed - error happened when do rhel upgrade testing:"+str(e))
        finally:
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)


