import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
def run_tc_ID147117_verify_product_cert_validity(test, params, env):

        session,vm=eu().init_session_vm(params,env)

        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
        try:
                
                cmd='for i in $(ls /etc/pki/product/*); do openssl x509 -text -noout -in $i; done | grep -A 3 "Validity"'
                (ret,output)=eu().runcmd(session,cmd,"check product's cert validity!")

                if ret == 0 and ("Not Before" and "Not After" in output):

                        GMT_FORMAT = '%b %d %H:%M:%S %Y GMT'
                        cert_start_gmt=output[output.find('Not Before')+len('Not Before')+2:output.find('GMT')+3]
                        cert_end_gmt1=output[output.find('Not After ')+len('Not After ')+2:output.find('Subject')]
                        cert_end_gmt=cert_end_gmt1[:cert_end_gmt1.find('\n')]

                        # convert GMT time to datetime
                        cert_start_datetime=datetime.datetime.strptime(cert_start_gmt,GMT_FORMAT)
                        cert_end_datetime=datetime.datetime.strptime(cert_end_gmt,GMT_FORMAT)         
                        logging.info('Product cert validity is from %s to %s' %(cert_start_datetime,cert_end_datetime))

                        # get current datetime
                        date_today=datetime.datetime.today()
                        logging.info('current date is %s ' %date_today)
 
                        #compare time
                        if date_today>cert_start_datetime and date_today<cert_end_datetime:
                            logging.info('%s > current date < %s ' %(cert_start_datetime,cert_end_datetime))
                            logging.info("Test Successful - It's successful to verify product's cert validity.") 
                        else:
                            raise error.TestFail("Test Failed - Failed to verify product's cert validity.")
                else:
                        raise error.TestFail("Test Failed - Failed to get product's cert validity.")
        except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened when do product's cert validity"+str(e))
        finally:
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
