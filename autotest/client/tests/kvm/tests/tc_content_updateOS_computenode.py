import sys, os, subprocess, commands, random, re
import logging
import time
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_prod import ent_prod as ep
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_content_updateOS_computenode(test, params, env):
        session, vm = eu().init_session_vm(params, env)
        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        try:
                try:
                        # Get and print params of python command for content test
                        eu().cnt_command_params_content(params)

                        #[A]Prepare test data
                        guestname = params.get("guest_name")
                        if 'RHEL-ComputeNode-6.4' in guestname:
                                refer_redhat_release = 'Red Hat Enterprise Linux ComputeNode release 6.5 (Santiago)'
                                refer_kernel_version = 'kernel-2.6.32-358.2.1.el6'
                        elif 'RHEL-ComputeNode-5.9' in guestname:
                                refer_redhat_release = 'Red Hat Enterprise Linux ComputeNode release 5.10 (Tikanga)'
                                refer_kernel_version = 'kernel-2.6.18-348.el5'
			else:
				refer_redhat_release = 'Red Hat Enterprise Linux ComputeNode release 6.5 (Santiago)'
                                refer_kernel_version = 'kernel-2.6.32-358.2.1.el6'

                        baseurl = params.get("baseurl")
                        hostname = params.get("hostname")

                        platform = params.get("platform")
                        # guestname'RHEL-Server-6.4-64'
                        # dkey     'RHEL-Server-6.4_64_url'
                        dkey = '%s_%s_url' %(guestname[:len(list(guestname)) - len(guestname.split('-')[-1]) -1], platform)
                        # get os url 'http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.4/Server/x86_64/os/'
                        os_url = params.get(dkey)
                        variant = 'Workstation'

                        if ("stage" in hostname):
                                username = ee().get_env(params)["username"]
                                password = ee().get_env(params)["password"]
                                sku = ee().get_env(params)["productid"]
                        else:
                                username = ee.username_qa
                                password = ee.password_qa
                                sku = "RH0604852"
			
                        #[B]Run the test
			ep().cnt_updateOS_test(session, params, vm, env, username, password, sku, '', refer_redhat_release, refer_kernel_version , os_url, variant)

                except Exception, e:
                        logging.error(str(e))
                        raise error.TestFail("Test Failed - error happened when do rhel upgrade testing:" + str(e))
        finally:
                logging.info("=========== End of Running Test Case: %s ===========" % __name__)


