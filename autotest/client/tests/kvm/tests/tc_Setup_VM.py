import sys, os, subprocess, commands, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests import pexpect

def run_tc_Setup_VM(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		try:
			#upgrade some expected packages
			'''
			 pkg_url example:
			 if there is 1 platforms at the same job, take 32 platform as example:
			 "http://, http://" or "http:// http://" or "32-http:// http://" or "32-http://,32-http://"
		
			 if there are 2 platforms at the same job, for example:
			 32-http:// http://, 64-http:// http://, 32-http://, http://
		
			 if runcasein == "host", for example:
			 "http://, http://"
			'''
			_samhostip=params.get("samhostip")	
			if _samhostip==None:
				eu().write_proxy_to_rhsm_conf(session, params, env)

			pkgurl=params.get("pkg_url")
			if pkgurl != '' and pkgurl != None:
				targeturl=""
				urllist = pkgurl.split(',')
				imagename = params.get("image_name")
				runcasein = params.get("runcasein")
				if runcasein == "guest":
					if "32" in imagename:
						for item in urllist:
							i=item.strip()
							if i[0:2] != '64':
								if i[0:2] == '32':
									targeturl = targeturl + " " + i[3:]
								else: 
									targeturl = targeturl + " " + i
						
					elif "64" in imagename:
						for item in urllist:
							i=item.strip()
							if i[0:2] != '32':
								if i[0:2] == '64':
									targeturl = targeturl + " " + i[3:]
								else: 
									targeturl = targeturl + " " + i
				elif runcasein == "host":
					for item in urllist:
						targeturl = targeturl + " " + item.strip()

				cmd="rpm -Uvh %s" %targeturl
			       	(ret,output)=eu().runcmd(session,cmd,"upgrade all expected packages.")

				if ret == 0:
			        	logging.info("It's successful to upgrade all expected packages:%s" %targeturl)
				else:
			        	raise error.TestFail("Test Failed - Failed to upgrade all expected packages:%s" %targeturl)

			#upgrade subscription-manager packages
			'''
			 pkg_sm example:
			 Input all package names (subscription-manager* and python-rhsm*) seperated by comma, such as:
			 "1.0.17/1.el5/[i386,x86_64]/[subscription-manager,firstboot,gui,migration,debuginfo]:1.0.7/1.el5/[i386,x86_64]/[python-rhsm]"
			'''             
			pkgsm = params.get("pkg_sm")
			imagename = params.get("image_name")
			baseurl = "http://download.devel.redhat.com/brewroot/packages/"
			if pkgsm != '' and pkgsm != None:
				targeturl = ""
				typelist = pkgsm.split(':')
				for item in typelist:
					dirlist = item.strip().split('/')
					dir = dirlist[0].strip() + "/" + dirlist[1].strip() + "/"
					if "32" in imagename and "i386" in dirlist[2].strip() :
						arch = "i386"
					elif "64" in imagename and "x86_64" in dirlist[2].strip() :
						arch = "x86_64"
					else :
						arch = dirlist[2].strip()[1:len(dirlist[2].strip()) - 1]
					for item1 in dirlist[3].strip()[1:len(dirlist[3].strip()) - 1].split(','):
						pkg = item1.strip()
						if pkg == "subscription-manager" or pkg == "python-rhsm":
							package = pkg + "-" + dirlist[0] + "-" + dirlist[1] + "." + arch + ".rpm"
							targeturl = targeturl + " " + baseurl + pkg + "/" + dir + arch + "/" + package
						if pkg == "firstboot" or pkg == "gui" or pkg == "migration" or pkg == "debuginfo":
							package = "subscription-manager" + "-" + pkg + "-" + dirlist[0] + "-" + dirlist[1] + "." + arch + ".rpm"
							targeturl = targeturl + " " + baseurl + "subscription-manager" + "/" + dir + arch + "/" + package		
				cmd = "rpm -Uvh %s" % targeturl
				(ret, output) = eu().runcmd(session, cmd, "upgrade all expected packages.")

				if ret == 0:
				    logging.info("It's successful to upgrade all expected packages:%s" % targeturl)
				else:
				    raise error.TestFail("Test Failed - Failed to upgrade all expected packages:%s" % targeturl)

			# install ldtp for gui automaiton
			testtype = params.get("testtype")
			if testtype == "gui":
				runcasein = params.get("runcasein")
				eu().set_os_release(session)
				os_release = eu().get_os_release()
				if runcasein == "guest":
					virtual_machine_ip = eu().get_virtual_machine_ip(session)
					eu().copy_ldtp_to_virtual_machine(vm, os_release[0])
					eu().install_ldtp_in_guest(session, os_release[0])
					eu().install_ldtp_in_host(os_release[0])
					eu().start_ldtp_remote_server(session, os_release[0], virtual_machine_ip)
				elif runcasein == "host":
					eu().install_ldtp_in_host(os_release[0])
					#eu().start_ldtp_remote_server(None, os_release[0], "127.0.0.1")

			#configure server hostname 
			runcasein = params.get("runcasein")
			hostname=params.get("hostname")
			cmd="subscription-manager config --server.hostname=%s"%(hostname)
			if runcasein=='guest':
				(ret,output)=eu().runcmd(session,cmd,"config hostname")
			else:
				ret = subprocess.call(cmd, shell=True)
		        if ret == 0:
		        	logging.info("It's successful to configure the system as %s."%hostname)
		        else:
		        	raise error.TestFail("Test Failed - Failed to configure the system as %s."%hostname)

		        #configure rhsm baseurl
		        baseurl=params.get("baseurl")
		        cmd="subscription-manager config --rhsm.baseurl=%s"%(baseurl)
			if runcasein=='guest':
			       	(ret,output)=eu().runcmd(session,cmd,"config baseurl")
			else:
				ret = subprocess.call(cmd, shell=True)
		                if ret == 0:
		                        logging.info("It's successful to configure the system as %s."%baseurl)
		                else:
		                        raise error.TestFail("Test Failed - Failed to configure the system as %s."%baseurl)

		        #for sam configuaration
			#configure hostname as SAM server hostname and add ip in /etc/hosts
			samhostname=params.get("samhostname")
			samhostip=params.get("samhostip")
			if samhostname != None and samhostip != None and baseurl == 'https://%s:8088'%samhostname:
				#add sam hostip and hostname in /etc/hosts
				cmd="sed  -i '/%s/d' /etc/hosts"%samhostname
				(ret,output)=eu().runcmd(session,cmd,"removing old sam hostip and hostname")

				cmd="echo '%s %s' >> /etc/hosts"%(samhostip, samhostname)
				(ret,output)=eu().runcmd(session,cmd,"adding sam hostip and hostname")

				if ret == 0:
					logging.info("It's successful to add sam hostip %s and hostname %s."%(samhostip, samhostname))
				else:
					raise error.TestFail("Test Failed - Failed to add sam hostip %s and hostname %s."%(samhostip, samhostname))

				#config hostname, prefix, port, baseurl and repo_ca_crt by installing candlepin-cert
				cmd="rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm"%(samhostip,samhostname)
				(ret,output)=eu().runcmd(session,cmd,"install candlepin cert and config system")

				if ret == 0:
					logging.info("It's successful to install candlepin cert and configure the system as %s."%samhostip)
				else:
					raise error.TestFail("Test Failed - Failed to install candlepin cert and configure the system as %s."%samhostip)

			#for local candlepin configuaration
			#configure hostname as candlepin server hostname and add ip in /etc/hosts
			candlepinhostname=params.get("candlepinhostname")
			candlepinhostip=params.get("candlepinhostip")
			if candlepinhostname != None and candlepinhostip != None and baseurl == 'https://%s:8443'%candlepinhostname:
				#clean env data
				p = pexpect.spawn('rm -rf /root/.ssh/known_hosts')

				cmd ="rm -rf /etc/rhsm/ca/candlepin-local.pem"
			       	(ret,output)=eu().runcmd(session,cmd,"deleting the file '/etc/rhsm/ca/candlepin-local.pem' if exists")

				cmd ="rm -rf /etc/rhsm/ca/candlepin-ca.crt"
			       	(ret,output)=eu().runcmd(session,cmd,"deleting the file '/etc/rhsm/ca/candlepin-ca.crt' if exists")

				#copy candlepin-ca.crt from candlepin to test host machine's dir: autotest/client/tests/kvm/tests/
				kvm_test_dir = os.path.join(os.environ['AUTODIR'],'tests/kvm/tests/')
				sam_script_path=os.path.join(kvm_test_dir,'samtest')
				p = pexpect.spawn('scp root@%s:/etc/candlepin/certs/candlepin-ca.crt %s'% (candlepinhostip, sam_script_path))
				p.expect("Are you sure you want to continue connecting (yes/no)?")
				p.sendline('yes')
				p.expect("root@%s's password:"% candlepinhostip)
				p.sendline('redhat')

				#copy candlepin-ca.crt from test host machine's dir: autotest/client/tests/kvm/tests/
				kvm_test_dir = os.path.join(os.environ['AUTODIR'],'tests/kvm/tests/')
				sam_script_path=os.path.join(kvm_test_dir,'samtest/candlepin-ca.crt')
				for i in range(200): #check if the cert file exists
					if os.path.isfile(sam_script_path):
						break
				else:
					time.sleep(3)

				eu().copyfiles(vm,sam_script_path,"/etc/rhsm/ca/",cmddesc="copying candlepin-ca.crt from the dir: %s"%(kvm_test_dir+"/samtest"))

				#cp candlepin-ca.crt as candlepin-local.pem on vm
				cmd="cp /etc/rhsm/ca/candlepin-ca.crt /etc/rhsm/ca/candlepin-local.pem"
			       	(ret,output)=eu().runcmd(session,cmd,"copying candlepin-ca as candlepin-local")

				if ret == 0:
					logging.info("It's successful to copy candlepin-ca cert as candlepin-local.")
				else:
					raise error.TestFail("Test Failed - Failed to copy candlepin-ca cert as candlepin-local.")

		                #add candlepin hostip and hostname in /etc/hosts
				cmd="echo '%s %s' >> /etc/hosts"%(candlepinhostip, candlepinhostname)
			       	(ret,output)=eu().runcmd(session,cmd,"adding candlepin hostip and hostname")

				if ret == 0:
					logging.info("It's successful to add candlepin hostip %s and hostname %s."%(candlepinhostip, candlepinhostname))
				else:
					raise error.TestFail("Test Failed - Failed to add candlepin hostip %s and hostname %s."%(candlepinhostip, candlepinhostname))

				#config hostname, prefix, port, baseurl and repo_ca_crt
				cmd="subscription-manager config --server.hostname=%s --server.prefix='/candlepin' --server.port=8443 --rhsm.repo_ca_cert='/etc/rhsm/ca/candlepin-local.pem'"%(candlepinhostname)
			       	(ret,output)=eu().runcmd(session,cmd,"configuring candlepinhostname")

				if ret == 0:
					logging.info("It's successful to configure the system as %s."%candlepinhostname)
				else:
					raise error.TestFail("Test Failed - Failed to configure the system as %s."%candlepinhostname)

				#prepare product cert used against local candlepin
				cmd="mkdir -p /etc/pki/product/tmp"
			       	(ret,output)=eu().runcmd(session,cmd,"create a tmp dir to restore prodcut certs")

				cmd="mv -f /etc/pki/product/*.pem /etc/pki/product/tmp"
			       	(ret,output)=eu().runcmd(session,cmd,"move original product cert to to tmp dir")
			
				kvm_taest_dir = os.path.join(os.environ['AUTODIR'],'tests/kvm/tests/')
		                candlepin_cert_path=os.path.join(kvm_test_dir,'candlepin_certs/*')
		                
		                eu().copyfiles(vm, candlepin_cert_path, "/etc/pki/product/tmp",cmddesc="copying product certs to tmp dir")

			        cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%ee.pid1cc
			        (ret,output)=eu().runcmd(session,cmd,"copying default product cert to cert dir")

				if ret == 0:
					logging.info("It's successful to prepare product cert.")
				else:
					raise error.TestFail("Test Failed - Failed to prepare prodcut cert.")

		except Exception, e:
			logging.error(str(e))
			raise error.TestFail("Test Failed - error happened when do configuration:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

