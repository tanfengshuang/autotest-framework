import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID191587_progress_spinner_during_gui_sla_autobind(test,params,env):
        session, vm = eu().init_session_vm(params, env)
        logging.info("========== Begin of Running Test Case %s ==========" % __name__)
        try:
                username = ee().get_env(params)["username"]
                password = ee().get_env(params)["password"]


                egu().open_subscription_manager(session)
                egu().click_register_button()
                egu().click_dialog_next_button()
                egu().input_username(username)
                egu().input_password(password)
                #during registeration to check progressbar
                egu().click_button("register-dialog", "dialog-register-button")
                if egu().check_object_exist('register-dialog','register-progressbar'):
                        logging.info("It's successful to check progress_spinners_exist_throughout_the_autobind_halfly !")
                else:
                        raise error.TestFail("Test Faild - Failed to check progress_spinners_exist_throughout_the_autobind_halfly")

                #during attachment to check progressbar 
                egu().wait_until_button_enabled("register-dialog", "dialog-register-button")
                egu().click_button("register-dialog", "dialog-register-button")
                if egu().check_object_exist('register-dialog','register-progressbar'):
                        logging.info("It's successful to check progress_spinners_exist_throughout_the_autobind_totally !")
                else:
                        raise error.TestFail("Test Faild - Failed to check progress_spinners_exist_throughout_the_autobind_totally"
)
        except Exception, e:
                logging.error(str(e))
                raise error.TestFail("error happened to check progress_spinners_exist_throughout_the_autobind:"+str(e))
        finally:
                egu().capture_image("progress_spinners_throughout_autobind")
                egu().restore_gui_environment(session)
                logging.info("===============End of Running Test Case: %s"%__name__)

