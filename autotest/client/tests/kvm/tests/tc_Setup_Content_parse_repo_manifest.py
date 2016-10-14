import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_Setup_Content_parse_repo_manifest(test, params, env):

        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
	        try:
	                kvm_test_dir = os.path.join(os.environ['AUTODIR'], 'tests/kvm/tests')
	                content_script_path = os.path.join(kvm_test_dir, 'contenttest/manifest_metadata')
			json_download = 'package-manifest.json'
			json_download_path = os.path.join(content_script_path, json_download)
			xml_download = 'rhel_manifest.xml'
			xml_download_path = os.path.join(content_script_path, xml_download)
	
			# get json file
			url = params.get('manifest_url')
			if url != None:
				cmd = 'wget %s -O %s' % (url, json_download_path)
				(ret, output) = eu().runcmd(None, cmd, "wget manifest file with given url")

				cmd = "file %s" % json_download_path
				(ret, output) = eu().runcmd(None, cmd, "ascertain the manifest file type")

				if "XML" in output:
					cmd = "mv %s %s" % (json_download_path, xml_download_path)
					(ret, output) = eu().runcmd(None, cmd, "rename manifest")
					if ret == 0 :
						logging.info("It's successful to download manifest file")
						return True
					else:
						raise error.TestFail("Test Failed - Failed to download manifest file")
				else:
					cmd = "cat /etc/redhat-release"
					(ret, output) = eu().runcmd(None, cmd, "host release version")

					if ret == 0 and ('5' in output or '7' in output) and (not '.5' in output or '.7' in output):
						logging.error("There is on json model on RHEL5 and RHEL7, please give it one manifest file of xml type directly")
						raise error.TestFail("No JSON model on 5RHEL OS!")
			else:
				raise error.TestFail("Test Failed - Failed to get params : manifest_url")

			## install kobo, koji, kobo-rpmlib
			## packages kobo* koji is not related to the variants and arch(*.el6.noarch.rpm), so can install pkgs for 6Server-x86_64 into all arches(x86_64, i386) of all RHEL6 variants(6Server, 6Client and 6Workstation)
			install_kobo_rpms(None, params, env)

			serverURL = params.get("serverURL")
			if serverURL == None:
				cmd = "python %s/parse_json_to_xml.py %s %s/rhel_manifest.xml cdn" % (content_script_path, json_download_path, content_script_path)
			else:
				cmd = "python %s/parse_json_to_xml.py %s %s/rhel_manifest.xml rhn" % (content_script_path, json_download_path, content_script_path)

			(ret,output) = eu().runcmd(None, cmd, "content testing for parse repo manifest")
			
	
	                if ret == 0 and "successfully" in output:
				logging.info("It's successful to parse repo manifest.\n")
	                else:
	                        raise error.TestFail("Test Failed - Faild to do content testing.\n")
	
	        except Exception, e:
	                logging.error(str(e))
	                raise error.TestFail("Test Failed - error happened when do content testing:" + str(e))
        finally:
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)


def install_kobo_rpms(session, params, env):
        # config repo and then yum install kobo, kobo-rpmlib, koji                           

	# repo_url = "http://mirrors.ustc.edu.cn/fedora/epel/6/x86_64/"
	repo_url = "http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/epel/6/x86_64/"
        input_repo = """[epel]
name=Fedora epel
failovermethod=priority
baseurl=%s
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$basearch
""" % (repo_url)
	
	eu().write_proxy_to_rhsm_conf(session, params, env)	
        repo_file_path = '/etc/yum.repos.d/epel.repo'
        repo_file = open(repo_file_path,'w')
        repo_file.write(input_repo)
        repo_file.close()
	
        #yum install -y kobo, kobo-rpmlib, koji
        cmd = "yum install -y kobo kobo-rpmlib koji"
        (ret, output) = eu().runcmd(None,cmd,"install packages for parsing rpm package NVRA")
        if ret == 0 and ("Complete!" in output or "already installed" in output):
                logging.info("It's successful to install the three packages required.\n")
        else:
                raise error.TestFail("Test Failed - Faild to install the three packages required.\n")

