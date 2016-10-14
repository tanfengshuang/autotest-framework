import sys, os, subprocess, commands, string, re, random, pexpect, time
import logging
import ConfigParser
import yum
from autotest_lib.client.common_lib import error


class ent_utils:


        # ========================================================
        #       0. 'Basic' Common Functions
        # ========================================================

        def init_session_vm(self, params, env):
                if env != None:
                        vm = env.get_vm(params["main_vm"])
                        vm.verify_alive()
                        timeout = int(params.get("login_timeout", 360))
                        session = vm.wait_for_login(timeout=timeout)
                else:
                        session = None
                        vm = None

                return session, vm

        def runcmd(self, session, cmd, cmddesc = "", timeout = ""):
                if session != None:
                        if timeout == "":
                                (ret, output) = session.get_command_status_output(cmd)
                        else:
                                (ret, output) = session.get_command_status_output(cmd, timeout=int(timeout))

                        if len(cmd) > 47:
                                outputlines = output.splitlines(True)
                                if len(outputlines) > 0 and (cmd[:47] in outputlines[0]):
                                        output = "".join(outputlines[1:])
                else:
                        if timeout == "":
                                (ret, output) = commands.getstatusoutput(cmd)
                        else:
				if "|" in cmd or ">" in cmd or ">>" in cmd:
					cmd = "bash -c '%s'" % cmd
                                (output, ret) = pexpect.run(cmd, withexitstatus=1, timeout=int(timeout))

                if cmddesc != "":
                        cmddesc = " of " + cmddesc
                logging.info("command%s: %s" % (cmddesc, cmd))
                logging.info("result%s: %s" % (cmddesc, str(ret)))
                logging.info("output%s:" % (cmddesc))

                if len(output.splitlines()) > 100:
	                logging.info("<< Note: since the output of the command is too long(greater than 100 lines) here, logged it as debug info. >>")
	                logging.debug("%s"%(str(output)))
                else:
	                logging.info("%s"%(str(output)))

                return ret, output

        def runcmd_remote(self, remoteIP, username, password, cmd):
                """ Remote exec function via pexpect """
                user_hostname = "%s@%s" % (username, remoteIP)
                child = pexpect.spawn("/usr/bin/ssh", [user_hostname, cmd], timeout=60, maxread=2000, logfile=None)
                while True:
                        index = child.expect(['(yes\/no)', 'password:', pexpect.EOF, pexpect.TIMEOUT])
                        if index == 0:
                                child.sendline("yes")
                        elif index == 1:
                                child.sendline(password)
                        elif index == 2:
                                child.close()
                                return child.exitstatus, child.before
                        elif index == 3:
                                child.close()


        def copyfiles(self, vm, sourcepath, targetpath, cmddesc=""):
                if vm != None:
                        vm.copy_files_to(sourcepath, targetpath)
                else:
                        cmd="cp -rf %s %s"%(sourcepath, targetpath)
                        (ret, output)=self.runcmd(None, cmd, cmddesc)

        def write_proxy_to_yum_conf(self, session, params, env):
                logging.info("Add proxy to /etc/yum.conf")
                proxy_eng = "squid.corp.redhat.com:3128"

                # get proxy_eng value
                if proxy_eng=='':
                        pass
                else:
                        usrname=params.get("guest_name")
                        rel=usrname.split('.')[0]
                        proxy_head='proxy'

                        cmd="cat /etc/yum.conf|grep 'proxy'"
                        (ret, output)=self.runcmd(session, cmd, "list proxy in /etc/yum.conf")
                        if (ret == 0 ):
                                pass
                        else:
                                input_proxy_eng=('%s=https://%s' %(proxy_head, proxy_eng))
                                cmd="echo %s >>/etc/yum.conf" %input_proxy_eng
                                (ret, output)=self.runcmd(session, cmd, "cat proxy to /etc/yum.conf")
                                if (ret == 0):
                                        logging.info("It is success to write %s to /etc/yum.conf" %input_proxy_eng)
                                else:
                                        logging.error("It is failed to write %s to /etc/yum.conf" %input_proxy_eng)
                                        return False

	def write_proxy_to_rhsm_conf(self, session, params, env):
                logging.info("Add proxy to /etc/rhsm/rhsm.conf")
		proxy_hostname = "squid.corp.redhat.com"
		proxy_port = "3128"

		(ret, output) = self.runcmd(session, "ifconfig", "get IP")
		if "10.66" in output and proxy_hostname != "":
			cmd = "cat /etc/rhsm/rhsm.conf | grep 'squid'"
			(ret, output)=self.runcmd(session, cmd, "check proxy setting in /etc/rhsm/rhsm.conf")
                        if (ret == 0 ):
                                pass
                        else:
				cmd = "sed -i 's/proxy_hostname =/proxy_hostname = squid.corp.redhat.com/' /etc/rhsm/rhsm.conf"
				(ret, output)=self.runcmd(session, cmd, "set proxy_hostname")
				if (ret == 0):
                                        logging.info("It is success to set proxy_hostname to /etc/rhsm/rhsm.conf")
                                else:
                                        logging.error("It is failed to set proxy_hostname to /etc/rhsm/rhsm.conf")
                                        return False

				cmd = "sed -i 's/proxy_port =/proxy_port = 3128/' /etc/rhsm/rhsm.conf"
				(ret, output)=self.runcmd(session, cmd, "set proxy_port")
				if (ret == 0):
                                        logging.info("It is success to set proxy_port to /etc/rhsm/rhsm.conf")
                                else:
                                        logging.error("It is failed to set proxy_port to /etc/rhsm/rhsm.conf")
                                        return False

	def is_file(self, session, file_path):
                  # confirm the file is existing or not
       		cmd = "(if [ -s '%s' ];then echo \"SUCCESS to find file %s\";else  echo \"FAIL to find file %s\"; fi)" %(file_path, file_path, file_path)
        	(ret, output)=self.runcmd(session, cmd, "find the file")

       		if ret == 0 and 'SUCCESS' in output:
                	return True
              	else:
                     	return False

        # ========================================================
        #       1. 'Acceptance' Test Common Functions
        # ========================================================

        def sub_configplatform(self, session, hostname):
                cmd="subscription-manager config --server.hostname=%s"%(hostname)
                (ret, output)=self.runcmd(session, cmd, "configuring the system")

                if ret == 0:
                        logging.info("It's successful to configure the system as %s."%hostname)
                else:
                        raise error.TestFail("Test Failed - Failed to configure the system as %s."%hostname)

        def sub_register(self, session, username, password, subtype=""):
                if subtype == "":
                        cmd = "subscription-manager register --username=%s --password='%s'"%(username, password)
                else:
                        cmd = "subscription-manager register --type=%s --username=%s --password='%s'"%(subtype, username, password)

                if self.sub_isregistered(session):
                        logging.info("The system is already registered, need to unregister first!")

                        cmd_unregister = "subscription-manager unregister"
                        (ret, output) = self.runcmd(session, cmd_unregister, "unregister")

                        if ret == 0:
                                if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                                        logging.info("It's successful to unregister.")
                                else:
                                        logging.info("The system is failed to unregister, try to use '--force'!")
                                        cmd += " --force"

                (ret, output) = self.runcmd(session, cmd, "register")
                if ret == 0:
                        if ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
                                logging.info("It's successful to register.")
                        else:
                                raise error.TestFail("Test Failed - The information shown after registered is not correct.")
                else:
                        raise error.TestFail("Test Failed - Failed to register.")

        def sub_get_consumerid(self, session):
                consumerid=''
                if self.sub_isregistered(session):
                        cmd="subscription-manager identity"
                        (ret, output)=self.runcmd(session, cmd, "get consumerid")
                        if ret==0 and "system identity:" in output:
                                consumerid_gain=output.split('\n')
                                consumerid_line_split=(consumerid_gain[0]).split(":")
                                consumerid=(consumerid_line_split[1]).strip()
                                logging.info("consumerid is gained successfully!")
                        else:
                                raise error.TestFail("Test Failed - Failed to get subscription-manager identity")
                return consumerid

        def sub_get_poolid(self, session):
                poolid=''
                if self.sub_isregistered(session):
                        cmd="subscription-manager list --consumed"
                        (ret, output)=self.runcmd(session, cmd, "get poolid")
                        if ret==0 and "Pool ID:" in output:
                                poolid_gain=output.split('\n')
                                poolid_line_split=(poolid_gain[0]).split(":")
                                poolid=(poolid_line_split[1]).strip()
                                logging.info("poolid is gained successfully!")
                        else:
                                raise error.TestFail("Test Failed - Failed to get subscription-manager poolid")
                return poolid

        def sub_listavailpools(self, session, productid):
                cmd="subscription-manager list --available"
                (ret, output)=self.runcmd(session, cmd, "listing available pools")

                if ret == 0:
                        if "no available subscription pools to list" not in output.lower():
                                if productid in output:
                                        logging.info("The right available pools are listed successfully.")
                                        pool_list = self.parse_listavailable_output(output)
                                        return pool_list
                                else:
                                        raise error.TestFail("Not the right available pools are listed!")

                        else:
                                logging.info("There is no Available subscription pools to list!")
                                return None
                else:
                        raise error.TestFail("Test Failed - Failed to list available pools.")

        def sub_listinstalledpools(self, session):
                cmd = "subscription-manager list --installed"
                (ret, output) = self.runcmd(session, cmd, "listing installed pools")
                if ret == 0:
                        logging.info("The right installed pools are listed successfully.")
                        pool_list = self.parse_listavailable_output(output)
                        return pool_list
                else:
                        raise error.TestFail("Test Failed - Failed to list installed pools.")

        def sub_listconsumedpools(self, session):
                cmd = "subscription-manager list --consumed"
                (ret, output) = self.runcmd(session, cmd, "listing consumed pools")
                if ret == 0:
                        logging.info("The right consumed pools are listed successfully.")
                        pool_list = self.parse_listavailable_output(output)
                        return pool_list
                else:
                        raise error.TestFail("Test Failed - Failed to list consumed pools.")

        def sub_listallavailpools(self, session, productid):
                cmd="subscription-manager list --available --all"
                (ret, output)=self.runcmd(session, cmd, "listing available pools")

                if ret == 0:
                        if "no available subscription pools to list" not in output.lower():
                                if productid in output:
                                        logging.info("The right available pools are listed successfully.")
                                        pool_list = self.parse_listavailable_output(output)
                                        return pool_list
                                else:
                                        raise error.TestFail("Not the right available pools are listed!")

                        else:
                                logging.info("There is no Available subscription pools to list!")
                                return None
                else:
                        raise error.TestFail("Test Failed - Failed to list all available pools.")

        def parse_listavailable_output(self, output):
                datalines = output.splitlines()
                data_list = []

                # split output into segmentations for each pool
                data_segs = []
                segs = []
                tmpline = ""

                for line in datalines:
                        if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                                 tmpline = line
                        elif line and ":" not in line:
                                tmpline = tmpline + ' ' + line.strip()
                        elif line and ":" in line:
                                segs.append(tmpline)
                                tmpline = line
                        if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line) or ("SystemType:" in line):
                                segs.append(tmpline)
                                data_segs.append(segs)
                                segs = []

                for seg in data_segs:
                        data_dict = {}
                        for item in seg:
                                keyitem = item.split(":")[0].replace(' ','')
                                valueitem = item.split(":")[1].strip()
                                data_dict[keyitem] = valueitem
                        data_list.append(data_dict)

                return data_list

        def parse_listconsumed_output(self, output):
                datalines = output.splitlines()
                data_list = []

                # split output into segmentations
                data_segs = []
                segs = []
                tmpline = ""

                '''
                for line in datalines:
                if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                        segs.append(line)
                elif segs:
                        segs.append(line)
                if ("Expires:" in line) or ("Ends:" in line):
                        data_segs.append(segs)
                        segs = []
                '''
                                #new way
                for line in datalines:
                        if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                                 tmpline = line
                        elif line and ":" not in line:
                                tmpline = tmpline + ' ' + line.strip()
                        elif line and ":" in line:
                                segs.append(tmpline)
                                tmpline = line
                        if ("Expires:" in line) or ("Ends:" in line):
                                segs.append(tmpline)
                                data_segs.append(segs)
                                segs = []

                '''# handle item with multi rows
                for seg in data_segs:
                        length = len(seg)
                        for index in range(0, length):
                                if ":" not in seg[index]:
                                        seg[index-1] = seg[index-1] + " " + seg[index].strip()
                        for item in seg:
                                if ":" not in item:
                                        seg.remove(item)
                '''
                # parse detail information
                for seg in data_segs:
                        data_dict = {}
                for item in seg:
                        keyitem = item.split(":")[0].replace(' ','')
                        valueitem = item.split(":")[1].strip()
                        data_dict[keyitem] = valueitem
                data_list.append(data_dict)

                return data_list

        def sub_subscribetopool(self, session, poolid):
                cmd = "subscription-manager subscribe --pool=%s"%(poolid)
                (ret, output) = self.runcmd(session, cmd, "subscribe")

                if ret == 0:
                        #Note: the exact output should be as below:
                        #For 6.2: "Successfully subscribed the system to Pool"
                        #For 5.8: "Successfully consumed a subscription from the pool with id"
                        if "Successfully " in output:
                                logging.info("It's successful to subscribe.")
                        else:
                                raise error.TestFail("Test Failed - The information shown after subscribing is not correct.")
                else:
                        raise error.TestFail("Test Failed - Failed to subscribe.")

        def check_rct(self, session):
                cmd = "rct cat-cert --help"
                (ret, output) = self.runcmd(session, cmd, "check rct cat-cert command")
                if ret == 0:
                        logging.info("rct cat-cert command can be used in the system")
                else:
                        logging.info("rct cat-cert command can not be used in the system")

                return ret

        def sub_checkentitlementcerts(self, session, productid):
                rctcommand=self.check_rct(session)
                if rctcommand==0:
                        cmd="for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do rct cat-cert /etc/pki/entitlement/$i; done | grep %s"%(productid)
                else:
                        cmd="for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i; done | grep %s"%(productid)
                (ret, output)=self.runcmd(session, cmd, "check entitlement certs")

                if ret == 0:
                        if productid in output:
                                logging.info("It's successful to check entitlement certificates.")
                        else:
                                raise error.TestFail("Test Failed - The information shown entitlement certificates is not correct.")
                else:
                        raise error.TestFail("Test Failed - Failed to check entitlement certificates.")

        def sub_isregistered(self, session):
                cmd="subscription-manager identity"
                (ret, output)=self.runcmd(session, cmd, "identity")

                if ret ==0:
                        logging.info("The system is registered to server now.")
                        return True
                else:
                        logging.info("The system is not registered to server now.")
                        return False

        def sub_unregister(self, session):
                if self.sub_isregistered(session):
                        cmd="subscription-manager unregister"
                        (ret, output)=self.runcmd(session, cmd, "unregister")

                        if ret == 0:
                            if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                                    logging.info("It's successful to unregister.")
                            else:
                                    raise error.TestFail("Test Failed - The information shown after unregistered is not correct.")
                        else:
                                raise error.TestFail("Test Failed - Failed to unregister.")
                else:
                        logging.info("The system is not registered to server now.")

        def sub_unsubscribe(self, session):
                cmd="subscription-manager unsubscribe --all"
                (ret, output)=self.runcmd(session, cmd, "unsubscribe")
                expectout = "This machine has been unsubscribed from"
                expectoutnew = "subscription removed from this system."
                expectout5101 = "subscription removed at the server."
                expectout5102 = "local certificate has been deleted."
                if ret == 0:
                        if output.strip() == "" or (((expectout5101 in output) and (expectout5102 in output)) \
							or expectout in output or expectoutnew in output):
                                logging.info("It's successful to unsubscribe.")
                        else:
                                raise error.TestFail("Test Failed - The information shown after unsubscribed is not correct.")
                else:
                        raise error.TestFail("Test Failed - Failed to unsubscribe.")

        def cnt_subscribe_product_with_specified_sku(self, session, prodsku):
                # subscribe with the specified prodsku
                dictlist = self.sub_listavailpools_of_sku(session, prodsku)
                odict = dictlist[0]
                prodpool = ''
                if odict.has_key('SKU'):
                        if odict.get('SKU') == prodsku:
                                if odict.has_key('Pool ID'):
                                        prodpool = odict.get('Pool ID')
                                elif odict.has_key('PoolId'):
                                        prodpool = odict.get('PoolId')
                                elif odict.has_key('PoolID'):
                                        prodpool = odict.get('PoolID')

                                self.sub_subscribetopool(session, prodpool)
                                return True
                else:
                        return False

        def sub_isconsumed(self, session, productname):
                cmd="subscription-manager list --consumed"
                (ret, output)=self.runcmd(session, cmd, "listing consumed subscriptions")
                output_join = " ".join(x.strip() for x in output.split())
                if (ret == 0) and (productname in output or productname in output_join):
                        logging.info("The subscription of the product is consumed.")
                        return True
                else:
                        logging.info("The subscription of the product is not consumed.")
                        return False

        def sub_checkproductcert(self, session, productid):
                rctcommand=self.check_rct(session)
                if rctcommand==0:
                        cmd="for i in /etc/pki/product/*; do rct cat-cert $i; done"
                else:
                        cmd="for i in /etc/pki/product/*; do openssl x509 -text -noout -in $i; done"
                (ret, output)=self.runcmd(session, cmd, "checking product cert")
                if ret == 0:
                        if ("1.3.6.1.4.1.2312.9.1.%s"%productid in output) or ("ID: %s"%productid in output and "Path: /etc/pki/product/%s.pem"%productid in output):
                                logging.info("The product cert is verified.")
                        else:
                                raise error.TestFail("Test Failed - The product cert is not correct.")
                else:
                        raise error.TestFail("Test Failed - Failed to check product cert.")

        def get_subscription_serialnumlist(self, session):
                cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
                (ret, output) = self.runcmd(session, cmd, "list all certificates in /etc/pki/entitlement/")

		if ret == 0:
                	ent_certs = output.splitlines()
                	serialnumlist = [line.replace('.pem',  '') for line in ent_certs]
		else:
			serialnumlist = []
                return serialnumlist

        def sub_checkidcert(self, session):
                cmd="ls /etc/pki/consumer/"
                (ret, output) = self.runcmd(session, cmd, "listing the files in /etc/pki/consumer/")

                if ret == 0 and "cert.pem" in output and "key.pem" in output:
                        logging.info("There are identity certs in the consumer directory.")
                        return True
                else:
                        logging.info("There is no identity certs in the consumer directory.")
                        return False

        def sub_autosubscribe(self, session, autosubprod):
                #cmd = "subscription-manager subscribe --auto"
                cmd = "subscription-manager attach --auto"
                (ret, output) = self.runcmd(session, cmd, "auto-subscribe")

                if ret == 0:
                    if ("Subscribed" in output) and ("Not Subscribed" not in output):
                            logging.info("It's successful to auto-subscribe.")
                    else:
                            raise error.TestFail("Test Failed - Failed to auto-subscribe correct product.")
                else:
                        raise error.TestFail("Test Failed - Failed to auto-subscribe.")

        def sub_getcurrentversion(self, session, guestname):
                platform = guestname.split('-')[1].strip()
                version = guestname.split('-')[2].strip().split('.')[0].strip()
                currentversion = version + platform
                return currentversion

        def sub_getcurrentversion2(self, guestname):
                os_version = guestname.split('-')[-1].strip()
                return os_version

        def sub_set_servicelevel(self, session, service_level):
                #set service-level
                cmd="subscription-manager service-level --set=%s" %service_level
                (ret,output)=self.runcmd(session,cmd,"set service-level as %s" %service_level)

                if ret == 0 and "Service level set to: %s" %service_level in output:
                        logging.info("It's successful to set service-level as %s" %service_level)
                else:
                        raise error.TestFail("Test Failed - Failed to set service-level as %s" %service_level)

        # ========================================================
        #       2. 'Content' Test Common Functions
        # ========================================================
        # ----------------------------------------------
        #       'Content' Refactoring Functions
        # ----------------------------------------------

        def cnt_get_content_script_path(self):
                kvm_test_dir = os.path.join(os.environ['AUTODIR'], 'tests/kvm/tests')
                content_script_path=os.path.join(kvm_test_dir, 'contenttest')
                return content_script_path

	def cnt_command_params_content(self, params):
                # Get and print params of python command for content test

                python_command = "# python ConfigLoop.py"
                white_list = ["runcasein", "hostname", "baseurl", "serverURL", "category", "platform", "guestname", "content_level", "release_list", "blacklist", "manifest_url", "pkg_sm", "pkg_url"]
                for param in white_list:
                        param_value = params.get(param)
                        if param_value != None and param_value != '':
                                sub_command = "--%s=%s" % (param, param_value)
                                python_command += " %s" % sub_command

                for key in params.keys():
                        if "_url" in key and key != "manifest_url":
                                url_value = params[key]
                                if url_value != None and url_value != "None" and url_value != '':
                                        sub_command = "--%s=%s" % (key, url_value)
                                        python_command += " %s" % sub_command

                logging.info("*********** The params of executed command for content *********** \n%s" % python_command)
                logging.info("*"*66)

        def cnt_get_prodsku_and_basesku(self, sku):
                #get prodsku and basesku from the sku string, sku example: sku="RH1149049,RH0103708", or sku="RH0838656"

                if sku == "":
                        raise error.TestFail("Test Failed - Failed to get prodsku and basesku from the sku string which is empty.")

                prodsku=""
                basesku=""

                skulist=sku.split(',')
                skunum=len(skulist)
                if skunum == 1:
                        prodsku=skulist[0]
                        basesku=""

                elif skunum > 1:
                        if skunum == 2:
                                prodsku=skulist[0]
                                basesku=skulist[1]
                        else:
                                #Note, code here will handle the sku number is greater than 2
                                pass

                return prodsku, basesku

	def cnt_set_config_file(self, session, release, config_file):
		cmd = '''sed -i "s/yumvars\['releasever'\] = /yumvars\['releasever'\] = '%s' # /" %s''' % (release, config_file)
		(ret, output) = self.runcmd(session, cmd, "modify config.py to set the release of system")
		cmd = '''cat %s | grep "yumvars\['releasever'\]"''' % config_file
		(ret, output) = self.runcmd(session, cmd, "check the setting in config.py")
		if release in output:
			logging.info("It's successful to set release of system.")
			return True
		else:
			logging.error("Test Failed - Failed to set release of system." )
			return False

        def cnt_set_release(self, session, release):
                '''set release of system by executing command 'subscription-manager release --set=%s' % release'''

		cmd = "cat /etc/redhat-release"
                (ret, output) = self.runcmd(session, cmd, "get the version of system")
                if '5.' in output:
			os_version = '5'
			config_file = "/usr/lib/python2.4/site-packages/yum/config.py"
		elif '6.' in output:
			os_version = '6'
			config_file = "/usr/lib/python2.6/site-packages/yum/config.py"
		else:
			os_version = '6'
                        config_file = "/usr/lib/python2.7/site-packages/yum/config.py"

                cmd="subscription-manager release --set=%s" % release
                (ret,output) = self.runcmd(session, cmd, "set release of system")

		if ret == 0 and 'Release set to' in output:
                        logging.info("It's successful to set release of system.")
                        cmd = "subscription-manager release"
                        (ret, output) = self.runcmd(session, cmd, "list the release of system")
                        return True
                elif ret == 0 and 'Usage: subscription-manager' in output:
			return self.cnt_set_config_file(session, release, config_file)
		elif 'No releases match' in output:
			if os_version == '5':
				return self.cnt_set_config_file(session, release, config_file)
			else:
				return False
		else:
                        logging.error("Test Failed - Failed to set release of system." )
                        return False

        def cnt_cmp_arrays(self, array1, array2):
                # cmp two arrays, get the data in array1 but not in array2

                list_not_in_array2 = []
                for i in array1:
                        if i not in array2:
                                list_not_in_array2.append(i)
                return list_not_in_array2

        def cnt_get_two_arrays_diff(self, array1, array2):
                # get the two cmp results.

                ret1_not_in2 = []
                ret2_not_in1 = []
                ret1_not_in2 = self.cnt_cmp_arrays(array1, array2)
                ret2_not_in1 = self.cnt_cmp_arrays(array2, array1)
                return ret1_not_in2, ret2_not_in1

        def cnt_print_list(self, listtoprint):
                for i in listtoprint:
                        logging.info('%s' %i)

        def cnt_yum_repolist(self, session):
                # get repolist

                cmd = 'yum repolist'
                (ret, output) = self.runcmd(session, cmd, "yum repolist", timeout="1200")
                if (ret == 0):
                        logging.info("It's successful to yum repolist")
                else:
                        raise error.TestFail("Test Failed - Failed to yum repolist")

        def cnt_yum_repolist_all(self, session, blacklist, cur_release, releasever_set):
                # enable all repos to check if there are broken repos

		target_file = ""
		if session == None:
		        target_file = "/etc/yum.repos.d/redhat.repo"
		else:
		        ## Get content of file redhat.repo on guest and prepare it on host
		        cmd = "cat /etc/yum.repos.d/redhat.repo"
		        (ret, output) = self.runcmd(session, cmd, "get the content of file redhat.repo on guest", timeout="18000")

		        target_file = "/tmp/redhat.repo"
		        f = open(target_file, 'w')
		        f.write(output)
		        f.close()

                src_str = ""
                dest_str = ""
                disablerepo_str = ''
                ET = False
                Error_list = []

                basearch = self.cnt_get_os_base_arch(session)
		config = ConfigParser.ConfigParser()
		config.read(target_file)

                while ET == False:
                        if len(disablerepo_str) >= 1:
                                if blacklist == 'Beta':
                                        cmd = "yum repolist --enablerepo=* --enablerepo=*beta* --disablerepo=%s %s" % (disablerepo_str.strip(), releasever_set)
                                elif blacklist == 'HTB':
                                        cmd = "yum repolist --enablerepo=* --enablerepo=*htb* --disablerepo=%s %s" % (disablerepo_str.strip(), releasever_set)
                                else:
                                        cmd = "yum repolist --enablerepo=* --disablerepo=%s %s" % (disablerepo_str.strip(), releasever_set)
                        else:
                                if blacklist == 'Beta':
                                        cmd = "yum repolist --disablerepo=* --enablerepo=*beta* %s" % releasever_set
                                elif blacklist == 'HTB':
                                        cmd = "yum repolist --disablerepo=* --enablerepo=*htb* %s" % releasever_set
                                else:
                                        cmd = "yum repolist --enablerepo=* %s" % releasever_set

                        (ret, output) = self.runcmd(session, cmd, "yum repolist repos*", timeout="18000")

                        repo_url = ''
                        if ret == 0 and "ERROR" in output or "Error" in output:
                                sp = output.index("http")
                                error_url = output[sp:output.index("Trying other mirror")-1]

                                error_dict = {}
                                error_dict['url'] = error_url

                                ep = output.index("/repodata/repomd.xml")
                                repo_url = output[sp:ep]

                                for s in config.sections():
                                        for i in config.items(s):
                                                if i[0] == "baseurl":
							if i[1].count("$") == 2:
								src_str = "%s/%s" % (cur_release, basearch)
								dest_str = "$releasever/$basearch"
							elif i[1].count("$") == 1:
								src_str = basearch
								dest_str = "$basearch"

							base_url = repo_url.replace(src_str, dest_str)

                                                        if i[1].find(base_url) >= 0:
                                                                error_dict['repo'] = s
                                                                if disablerepo_str == "":
                                                                        disablerepo_str += s
                                                                else:
                                                                        disablerepo_str = disablerepo_str + ',' + s

                                Error_list.append(error_dict)
                        else:
                                ET = True

                                if len(Error_list) == 0:
                                        logging.info("It's successful to do yum repolist --enablerepo=*.")
                                        return True
                                else:
                                        logging.info("=========================Summary of repos and baseurls=======================================")
                                        logging.error("Here are the error repos (total: %s) " % len(Error_list))
                                        for i in Error_list:
                                                logging.info("repo: %s" % i['repo'])
                                                logging.info("      %s" % i['url'])

                                        logging.error("Failed to do yum repolist --enablerepo=*.")
                                        return False

        def cnt_yum_repolist_enabled(self, session, blacklist, cur_release, releasever_set):
                # check all enabled repos to see if there are broken repos

		target_file = ""
		if session == None:
		        target_file = "/etc/yum.repos.d/redhat.repo"
		else:
		        ## Get content of file redhat.repo on guest and prepare it on host
		        cmd = "cat /etc/yum.repos.d/redhat.repo"
		        (ret, output) = self.runcmd(session, cmd, "get the content of file redhat.repo on guest", timeout="18000")

		        target_file = "/tmp/redhat.repo"
		        f = open(target_file, 'w')
		        f.write(output)
		        f.close()

                src_str = ""
                dest_str = ""
                disablerepo_str = ''
                ET = False
                Error_list = []

                basearch = self.cnt_get_os_base_arch(session)
		config = ConfigParser.ConfigParser()
		config.read(target_file)

                while ET == False:
                        if len(disablerepo_str) >= 1:
                                if blacklist == 'Beta':
                                        cmd = "yum repolist --disablerepo=* --enablerepo=*beta* --disablerepo=%s %s" % (disablerepo_str.strip(), releasever_set)
                                elif blacklist == 'HTB':
                                        cmd = "yum repolist --disablerepo=* --enablerepo=*htb* --disablerepo=%s %s" % (disablerepo_str.strip(), releasever_set)
                                else:
                                        cmd = "yum repolist --disablerepo=%s %s" % (disablerepo_str.strip(), releasever_set)
                        else:
                                if blacklist == 'Beta':
                                        cmd = "yum repolist --disablerepo=* --enablerepo=*beta* %s" % releasever_set
                                elif blacklist == 'HTB':
                                        cmd = "yum repolist --disablerepo=* --enablerepo=*htb* %s" % releasever_set
                                else:
                                        cmd = "yum repolist %s" % releasever_set

                        (ret, output) = self.runcmd(session, cmd, "run yum repolist to check all enabled repos", timeout="18000")

                        repo_url = ''
                        if ret == 0 and "ERROR" in output or "Error" in output:
                                sp = output.index("http")
                                error_url = output[sp:output.index("Trying other mirror")-1]

                                error_dict = {}
                                error_dict['url'] = error_url

                                ep = output.index("/repodata/repomd.xml")
                                repo_url = output[sp:ep]

                                for s in config.sections():
                                        for i in config.items(s):
                                                if i[0] == "baseurl":
							if i[1].count("$") == 2:
								src_str = "%s/%s" % (cur_release, basearch)
								dest_str = "$releasever/$basearch"
							elif i[1].count("$") == 1:
								src_str = basearch
								dest_str = "$basearch"

							base_url = repo_url.replace(src_str, dest_str)

                                                        if i[1].find(base_url) >= 0:
                                                                error_dict['repo'] = s
                                                                if disablerepo_str == "":
                                                                        disablerepo_str += s
                                                                else:
                                                                        disablerepo_str = disablerepo_str + ',' + s

                                Error_list.append(error_dict)
                        else:
                                ET = True

                                if len(Error_list) == 0:
                                        logging.info("It's successful to do yum repolist.")
                                        return True
                                else:
                                        logging.info("=========================Summary of repos and baseurls=======================================")
                                        logging.error("Here are the error repos (total: %s) " % len(Error_list))
                                        for i in Error_list:
                                                logging.info("repo: %s" % i['repo'])
                                                logging.info("      %s" % i['url'])

                                        logging.error("Failed to do yum repolist.")
                                        return False

        def cnt_yum_clean_cache(self, session, releasever_set):
                # get repolist
                cmd = 'yum clean all --enablerepo=* %s'  % releasever_set
                (ret, output) = self.runcmd(session, cmd, "yum clean cache", timeout="2400")
                if (ret == 0):
                        logging.info("It's successful to yum clean cache")
                else:
                        raise error.TestFail("Test Failed - Failed to yum clean cache")

        def cnt_run_curl(self, session, cert_fullpath, key_fullpath, target_url, to_file=None):
                #get content from target url

		_proxy_eng="squid.corp.redhat.com:3128"
                if cert_fullpath == "" and key_fullpath == "":

                        if _proxy_eng == '':
                                if to_file == None:
                                        cmd="curl -s -o -k %s" %(target_url)
                                else:
                                        cmd="curl -s -o -k %s -o %s" %(target_url,to_file)
                        else:
                                if to_file == None:
                                        cmd="curl -s -o -k --proxy http://%s  %s" %(_proxy_eng, target_url)
                                else:
                                        cmd="curl -s -o -k --proxy http://%s  %s -o %s" %(_proxy_eng, target_url, to_file)
                else:
                        if _proxy_eng == '':
                                if to_file == None:
                                        cmd="curl -s --cert %s --key %s -k %s && echo" %(cert_fullpath, key_fullpath, target_url)
                                else:
                                        cmd="curl -s --cert %s --key %s -k %s -o %s" %(cert_fullpath, key_fullpath, target_url, to_file)
                        else:
                                if to_file == None:
                                        cmd="curl -s --cert %s --key %s -k --proxy http://%s %s && echo" %(cert_fullpath, key_fullpath,_proxy_eng, target_url)
                                else:
                                        cmd="curl -s --cert %s --key %s -k --proxy http://%s %s -o %s" %(cert_fullpath, key_fullpath,_proxy_eng, target_url, to_file)
                if session != None :
                        (ret, output)=self.runcmd(session, cmd, "get content from the url '%s'"%target_url, timeout="18000")
                else:
                       	(ret, output)=self.runcmd(session, cmd, "get content from the url '%s'"%target_url)

                if (ret == 0 or ret == 6):
                        logging.info("It's successful to get content from the url '%s'."%target_url)
                        return output
                else:
			return False

        def cnt_get_os_release_version(self, session):
                # get release version of current system

		#if self.cnt_get_os_base_arch(session) == 'aarch64':
		#	return "1.5"

                cmd='''python -c "import yum; yb = yum.YumBase(); print(yb.conf.yumvar)['releasever']"'''
                (ret, output)=self.runcmd(session, cmd, "get current release version")
                if (ret==0 and "Loaded plugins" in output):
                        logging.info(" It's successful to get current release version.")
                        prog = re.compile('(\d+\S+)\s*')
                        result = re.findall(prog, output)
                        logging.info("Release version for current system is %s." %result[0])
                        return result[0]
                else:
                        raise error.TestFail("Test Failed - Failed to get current release version.")

        def cnt_get_os_base_arch(self, session):
                # get base arch of current system

                cmd='''python -c "import yum; yb = yum.YumBase(); print(yb.conf.yumvar)['basearch']"'''
                (ret, output)=self.runcmd(session, cmd, "get current base arch")
                if (ret==0 and "Loaded plugins" in output):
                        logging.info(" It's successful to get current base arch.")
                        #prog = re.compile("(\S+\d+.*)\s+")
                        #result = re.search(prog, output)
                        if "ppc64le" in output:
                                base_arch="ppc64le"
			elif "ppc64" in output:
				base_arch="ppc64"
                        elif "ppc" in output:
                                base_arch="ppc"
                        elif "i386" in output:
                                base_arch="i386"
                        elif "x86_64" in output:
                                base_arch="x86_64"
                        elif "s390x" in output:
                                base_arch="s390x"
                        elif "ia64" in output:
                                base_arch="ia64"
                        elif "aarch64" in output:
                                base_arch="aarch64"
                        else:
                                logging.info("No base arch could get from current system.")
                                raise error.TestFail("Test Failed - Failed to get current base arch.")

                        logging.info("Base arch for current system is %s." %base_arch)
                        return base_arch
                else:
                        raise error.TestFail("Test Failed - Failed to get current base arch.")



        def cnt_get_pkgurl_from_repofile_Old(self, session, repoid, current_rel_version, relver, arch):
        #This function is deprecated since it's affected by the format of the redhat.repo file.
        #Instead, please use the later function cnt_get_pkgurl_from_repofile()

                #get pkgurl from repofile /etc/yum.repos.d/redhat.repo

                cmd="cat /etc/yum.repos.d/redhat.repo"
                (ret, output)=self.runcmd(session, cmd, "get information of /etc/yum.repos.d/redhat.repo")
                if (ret == 0):
                        logging.info("It's successful to get information of /etc/yum.repos.d/redhat.repo." )
                        datalines = output.split('\n')
                else:
                        raise error.TestFail("Test Failed - Failed to get information of /etc/yum.repos.d/redhat.repo.")

                for index, line in enumerate(datalines):
                        if "[%s]"%repoid in line:
                                org_url = datalines[index+2].split("=")[1].strip()

                                if "$releasever" in org_url:
                                        if relver == 'None':
                                                relver = current_rel_version
                                        pkgurl = org_url.replace("$releasever", relver).replace("$basearch", arch)
                                else:
                                        pkgurl = org_url.replace("$basearch", arch)

                                if "SRPMS" in pkgurl:
                                        pkgurl = pkgurl+'/'
                                else:
                                        pkgurl = pkgurl+'/Packages/'

                                return pkgurl

        def cnt_get_pkgurl_from_repofile(self, session, repoid, current_rel_version, relver, arch):
                #get pkgurl from repofile /etc/yum.repos.d/redhat.repo

	        ## Get content of file redhat.repo on guest and prepare it on host
                target_file = "/tmp/redhat.repo"

                cmd="cat /etc/yum.repos.d/redhat.repo"
                (ret, output)=self.runcmd(session, cmd, "get information of /etc/yum.repos.d/redhat.repo")
                if (ret == 0):
		        f = open(target_file, 'w')
		        f.write(output)
		        f.close()

                        logging.info("It's successful to get information of /etc/yum.repos.d/redhat.repo." )

                else:
                        raise error.TestFail("Test Failed - Failed to get information of /etc/yum.repos.d/redhat.repo.")

                cf=ConfigParser.ConfigParser()
                cf.read(target_file)

                val_baseurl=cf.get(repoid,"baseurl")

                if "$releasever" in val_baseurl:
                        if relver == 'None':
                                relver = current_rel_version
                        pkgurl = val_baseurl.replace("$releasever", relver).replace("$basearch", arch)
                else:
                        pkgurl = val_baseurl.replace("$basearch", arch)

                if "SRPMS" in pkgurl:
                        pkgurl = pkgurl+'/'
                else:
                        pkgurl = pkgurl+'/Packages/'

                return pkgurl

        def cnt_is_releasever_in_baseurl_from_repofile(self, session, repoid):
                #Judge if the "$releasever" is in baseurl from repofile /etc/yum.repos.d/redhat.repo

	        ## Get content of file redhat.repo on guest and prepare it on host
                target_file = "/tmp/redhat.repo"

                cmd="cat /etc/yum.repos.d/redhat.repo"
                (ret, output)=self.runcmd(session, cmd, "get information of /etc/yum.repos.d/redhat.repo")
                if (ret == 0):
		        f = open(target_file, 'w')
		        f.write(output)
		        f.close()

                        logging.info("It's successful to get information of /etc/yum.repos.d/redhat.repo." )

                else:
                        raise error.TestFail("Test Failed - Failed to get information of /etc/yum.repos.d/redhat.repo.")

                cf=ConfigParser.ConfigParser()
                cf.read(target_file)

                val_baseurl=cf.get(repoid,"baseurl")

                if "$releasever" in val_baseurl:
	                return True
                else:
	                return False

        def cnt_get_repourl_from_repofile_Old(self, session, repoid, current_rel_version, relver, arch):
        #This function is deprecated since it's affected by the format of the redhat.repo file.
        #Instead, please use the later function cnt_get_repourl_from_repofile()

                #get repourl from repofile /etc/yum.repos.d/redhat.repo

                cmd="cat /etc/yum.repos.d/redhat.repo"
                (ret, output)=self.runcmd(session, cmd, "get information of /etc/yum.repos.d/redhat.repo")
                if (ret == 0):
                        logging.info("It's successful to get information of /etc/yum.repos.d/redhat.repo." )
                        datalines = output.split('\n')
                else:
                        raise error.TestFail("Test Failed - Failed to get information of /etc/yum.repos.d/redhat.repo.")

                for index, line in enumerate(datalines):
                        if "[%s]"%repoid in line:
                                org_url = datalines[index+2].split("=")[1].strip()
                                if "$releasever" in org_url:
                                        if relver == 'None':
                                                relver = current_rel_version
                                        repourl = org_url.replace("$releasever", relver).replace("$basearch", arch)
                                else:
                                        repourl = org_url.replace("$basearch", arch)

                                return repourl

        def cnt_get_repourl_from_repofile(self, session, repoid, current_rel_version, relver, arch):
                #get repourl from repofile /etc/yum.repos.d/redhat.repo

	        ## Get content of file redhat.repo on guest and prepare it on host
                target_file = "/tmp/redhat.repo"

                cmd="cat /etc/yum.repos.d/redhat.repo"
                (ret, output)=self.runcmd(session, cmd, "get information of /etc/yum.repos.d/redhat.repo")
                if (ret == 0):
		        f = open(target_file, 'w')
		        f.write(output)
		        f.close()

                        logging.info("It's successful to get information of /etc/yum.repos.d/redhat.repo." )

                else:
                        raise error.TestFail("Test Failed - Failed to get information of /etc/yum.repos.d/redhat.repo.")

                cf=ConfigParser.ConfigParser()
                cf.read(target_file)

                val_baseurl=cf.get(repoid,"baseurl")

                if "$releasever" in val_baseurl:
                        if relver == 'None':
                                relver = current_rel_version
                        repourl = val_baseurl.replace("$releasever", relver).replace("$basearch", arch)
                else:
                        repourl = val_baseurl.replace("$basearch", arch)

                return repourl

        def cnt_remove_non_redhat_repo(self, session):
                # delete rhn debuginfo repo to remove affection

                cmd = 'rm -f $(ls /etc/yum.repos.d/* | grep -v  "redhat.repo")'
                (ret, output) = self.runcmd(session, cmd, "delete rhn debuginfo repo to remove affection")

        def cnt_stop_rhsmcertd(self, session):
                #stop rhsmcertd because healing(autosubscribe) will run 2 mins after the machine is started, then every 24 hours after that, which will influence our content test.
                cmd = 'service rhsmcertd status'
                (ret, output) = self.runcmd(session, cmd, "check rhsmcertd service status")
                if 'stopped' in output or 'Stopped' in output:
                        return

                cmd = 'service rhsmcertd stop'
                (ret, output) = self.runcmd(session, cmd, "stop rhsmcertd service")
                if (ret == 0):
                        cmd = 'service rhsmcertd status'
                        (ret, output) = self.runcmd(session, cmd, "check rhsmcertd service status")
                        if 'stopped' in output or 'Stopped' in output:
                                logging.info("It's successful to stop rhsmcertd service.")
                        else:
				logging.error("Failed to stop rhsmcertd service.")
                else:
			logging.error("Failed to stop rhsmcertd service.")

	def cnt_stop_yum_updatesd(self, session, current_rel_version):
		#stop the yum_updatesd service in RHEL5.9 in order to avoid the yum lock issue

		if "5" in current_rel_version and ".5" not in current_rel_version:
			cmd = 'service yum-updatesd status'
			(ret, output) = self.runcmd(session, cmd, "check yum-updatesd service status")
			if ('stopped' in output or "yum-updatesd: unrecognized service" in output):
				return

			cmd = 'service yum-updatesd stop'
			(ret, output) = self.runcmd(session, cmd, "stop yum-updatesd service")
			if (ret == 0):
				cmd = 'service yum-updatesd status'
	                        (ret, output) = self.runcmd(session, cmd, "check yum-updatesd service status")
	                        if 'stopped' in output:
	                                logging.info("It's successful to stop yum-updatesd service.")
	                        else:
					logging.error("Failed to stop yum-updatesd service.")
	                else:
				logging.error("Failed to stop yum-updatesd service.")
		else:
			pass

        def cnt_ntpdate_redhat_clock(self, session):
                #ntpdate clock of redhat.com as a workaround for time of some systems are not correct, which will result in no info dislaying with "yum repolist" or "s-m repos --list"
                cmd = 'ntpdate clock.redhat.com'
                (ret, output) = self.runcmd(session, cmd, "ntpdate system time with clock of redhat.com")
                if (ret == 0) or ("the NTP socket is in use, exiting" in output):
                        logging.info("It's successful to ntpdate system time with clock of redhat.com.")
                else:
                        raise error.TestFail("Test Failed - Failed to ntpdate system time with clock of redhat.com.")

	def cnt_enable_testrepos(self, session, repolist):
		#enable all the test repos in repolist, the parameter repolist is a list of repos

		logging.info("--------------- Begin to enable test repos ---------------")
		for repo in repolist:
			cmd = "subscription-manager repos --enable=%s" % repo
			(ret, output)=self.runcmd(session, cmd, "enable repo %s in /etc/yum.repos.d/redhat.repo" % repo)
			if (ret == 0):
				logging.info("It's successful to enable repo %s in /etc/yum.repos.d/redhat.repo" % repo)
			else:
				raise error.TestFail("Test Failed - Failed to enable repo %s /etc/yum.repos.d/redhat.repo." % repo)
                logging.info("--------------- End to enable test repos ---------------")

	def cnt_disable_testrepos(self, session, repolist):
		logging.info("-----------------------Disabling test repos-----------------------")
		for repo in repolist:
			cmd = "subscription-manager repos --disable=%s" % repo
			(ret, output)=self.runcmd(session, cmd, "disable repo %s in /etc/yum.repos.d/redhat.repo" % repo)
			if (ret == 0):
                                logging.info("It's successful to disable repo %s in /etc/yum.repos.d/redhat.repo" % repo)
                        else:
                                raise error.TestFail("Test Failed - Failed to disable repo %s /etc/yum.repos.d/redhat.repo." % repo)
		logging.info("-----------------------End of disable test repos-------------------------")

	def cnt_enable_baserepo(self, session, baserepo):
		#enable the base repo

		logging.info("--------------- Begin to enable base repo ---------------")
		cmd = "subscription-manager repos --enable=%s" % baserepo
		(ret, output)=self.runcmd(session, cmd, "enable base repo %s in /etc/yum.repos.d/redhat.repo" % baserepo)
		if (ret == 0):
			logging.info("It's successful to enable base repo %s in /etc/yum.repos.d/redhat.repo" % baserepo)
		else:
			raise error.TestFail("Test Failed - Failed to enable base repo %s /etc/yum.repos.d/redhat.repo." % baserepo)
                logging.info("--------------- End to enable base repo ---------------")

        def cnt_enable_testrepos_bk(self, session, repolist):
                #enable all the test repos in repolist, the parameter repolist is a list of repos

		logging.info("--------------- Begin to enable all the test repos ---------------")
                cmd="""for i in $(echo "%s" | awk -F',' '{for(j=1;j<=NF;j++) print $j}'); do sed -i "$(($(grep -n "\[$i\]" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')+3)) s/0/1/" /etc/yum.repos.d/redhat.repo;done""" %','.join(repolist)

                (ret, output)=self.runcmd(session, cmd, "enable the '%d' repos in /etc/yum.repos.d/redhat.repo" %len(repolist))
                if (ret == 0):
                        logging.info("It's successful to enable the '%d' repos /etc/yum.repos.d/redhat.repo." %len(repolist))
                else:
                        raise error.TestFail("Test Failed - Failed to enable the '%d' repos /etc/yum.repos.d/redhat.repo." %len(repolist))
		logging.info("--------------- End to enable all the test repos ---------------")

	def cnt_change_gpgkey_for_testrepos(self, session, repolist):
		#change gpgkey for all the test repos in repolist, the parameter repolist is a list of repos

		logging.info("--------------- Begin to change gpgkey for test repos ---------------")
		for repo in repolist:
			cmd = "subscription-manager repo-override --repo %s --add=gpgkey:file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta,file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release" % repo
			(ret, output)=self.runcmd(session, cmd, "change gpgkey for repo %s in /etc/yum.repos.d/redhat.repo" % repo)
			if (ret == 0):
				logging.info("It's successful to change gpgkey for repo %s in /etc/yum.repos.d/redhat.repo" % repo)
			else:
				raise error.TestFail("Test Failed - Failed to change gpgkey for repo %s /etc/yum.repos.d/redhat.repo." % repo)
                logging.info("--------------- End to change gpgkey for test repos ---------------")

        def cnt_parse_entitlement_cert_with_rct(self, session, entitlement_cert_fullpath):
                # parse one entitlement cert with rct tool
                cmd = 'rct cat-cert %s' %entitlement_cert_fullpath
                (ret, output) = self.runcmd(session, cmd, "parse entitlement cert with rct")
                if (ret == 0):
                        logging.info("It's successful to parse entitlement cert %s with rct." %entitlement_cert_fullpath)
                        ent_cert_dict = {}
                        item_dict = {}
                        current_key = ''
			lines = output.splitlines()
			lines.append('')
                        for line in lines:
                                pattern = re.compile(r'^[A-Za-z]+(.*):')
                                #add the last 'condition' since sometimes there is no blank line between different items.
                                if (len(line.strip()) == 0) or (':' not in line) or (pattern.search(line)):
                                        if item_dict != {} and current_key != '':
                                                if isinstance(ent_cert_dict[current_key],list) == True:
                                                        ent_cert_dict[current_key].append(item_dict)
                                                else:
                                                        ent_cert_dict[current_key] = item_dict

                                                item_dict = {}

                                if (len(line.strip()) == 0) or (':' not in line):
                                        continue;

                                if (pattern.search(line)):
                                        current_key = line.strip(':\n')
                                        if (current_key in ent_cert_dict.keys()):
                                                if (isinstance(ent_cert_dict[current_key],list) == False):
                                                        ent_cert_dict[current_key] = [ent_cert_dict[current_key]]
                                        else:
                                                ent_cert_dict[current_key] = {}
                                else:
                                        key = line.strip('\t').strip('\n').split(':')[0].strip()
                                        value = line.strip('\t').strip('\n').split(':')[1:]
                                        if isinstance(value,list) == True:
                                                value = ":".join(value[:])
                                        item_dict[key] = value.strip()

                        return ent_cert_dict
                else:
                        return None


        def cnt_verify_productid_in_entitlement_cert(self, session, entitlement_cert_id, pid):
                # verify one product id in one entitlement cert
                entitlement_cert_fullpath = '/etc/pki/entitlement/%s.pem' %entitlement_cert_id
                entitlement_cert = self.cnt_parse_entitlement_cert_with_rct(session, entitlement_cert_fullpath)

                if None != entitlement_cert:
                        if isinstance(entitlement_cert['Product'],list) == False:
                                product_list = [entitlement_cert['Product']]
                        else:
                                product_list = entitlement_cert['Product']
                        productid_list = [item['ID'] for item in product_list ]

                        if pid in productid_list:
                                logging.info(" It's successful to verify product id %s in entitlement cert %s.pem." %(pid, entitlement_cert_id))
                                return
                        else:
                                raise error.TestFail("Test Failed - Failed to verify product id %s in entitlement cert %s.pem." %(pid, entitlement_cert_id))

                str='1.3.6.1.4.1.2312.9.1.'
                cmd='openssl x509 -text -noout -in /etc/pki/entitlement/%s.pem | grep --max-count=1 -A 1 %s%s' %(entitlement_cert_id, str, pid)
                (ret, output)=self.runcmd(session, cmd, "verify product id in entitlement cert")
                if (ret==0 and output!=''):
                        logging.info(" It's successful to verify product id %s in entitlement cert %s.pem." %(pid, entitlement_cert_id))
                else:
                        raise error.TestFail("Test Failed - Failed to verify product id %s in entitlement cert %s.pem." %(pid, entitlement_cert_id))

        def cnt_verify_sku_in_entitlement_cert(self, session, entitlement_cert_id, sku):
                # verify one sku id in one entitlement cert
                entitlement_cert_fullpath = '/etc/pki/entitlement/%s.pem' %entitlement_cert_id
                entitlement_cert = self.cnt_parse_entitlement_cert_with_rct(session, entitlement_cert_fullpath)

                if None != entitlement_cert:
                        order_sku = entitlement_cert['Order']['SKU']
                        if sku == order_sku:
                                logging.info(" It's successful to verify sku %s in entitlement cert %s.pem." %(sku, entitlement_cert_id))
                                return
                        else:
                                raise error.TestFail("Test Failed - Failed to verify product id %s in entitlement cert %s.pem." %(sku, entitlement_cert_id))

                cmd = 'openssl x509 -text -noout -in /etc/pki/entitlement/%s.pem | grep %s' %(entitlement_cert_id, sku)
                (ret, output) = self.runcmd(session, cmd, "verify sku in entitlement cert")
                if (ret == 0 and output != ''):
                        logging.info(" It's successful to verify sku %s in entitlement cert %s.pem." %(sku, entitlement_cert_id))
                else:
                        raise error.TestFail("Test Failed - Failed to verify sku %s in entitlement cert %s.pem." %(sku, entitlement_cert_id))

        def cnt_remove_packagekit(self, session):
                '''
                remove the PackageKit during content test in order to speed up the content test
                '''

                #check if the PackageKit exist in the system
                cmd_query_package = "rpm -q PackageKit"

                (ret, output)=self.runcmd(session, cmd_query_package, "query the PackageKit")
                if (ret == 0):
                        logging.info("PackageKit exist in the system now.")
                        cmd_remove = "yum remove -y %s" %output
                        (ret, output)=self.runcmd(session, cmd_remove, "remove the PackageKit!")
                        if (ret == 0) and ("Complete!" in output):
                                logging.info("It is successful to remove the PackageKit!")
                        else:
                                logging.error("Failed to remove the PackageKit!")
                else:
                        if (ret == 1) and ("package PackageKit is not installed" in output):
                                logging.info("PackageKit not exist, no need to remove it!")
                        else:
                                raise error.TestFail("Test Failed - Failed to query PackageKit!")


        def sub_listavailpools_of_sku(self, session, sku):
		time.sleep(5)
                cmd="subscription-manager list --available --all"
                (ret, output)=self.runcmd(session, cmd, "listing available pools")

                if ret == 0:
                        if "no available subscription pools to list" not in output.lower():
                                if sku in output:
                                        logging.info("The right available pools are listed successfully.")
                                        pool_list = self.parse_listavailable_output(output)
                                        pool_list_of_sku = []
                                        for prd in pool_list:
						if ("Pool ID" in prd.keys() and prd["Pool ID"] == sku) or \
						   ("SKU" in prd.keys() and prd["SKU"] == sku ) or \
						   ('ProductId' in prd.keys() and prd["ProductId"] == sku) or\
						   ('Product Id' in prd.keys() and prd["Product Id"] == sku):
                                                        pool_list_of_sku.append(prd)
                                        return pool_list_of_sku
                                else:
                                        raise error.TestFail("Not the right available pools are listed!")

                        else:
                                logging.info("There is no Available subscription pools to list!")
                                return None
                else:
                        raise error.TestFail("Test Failed - Failed to list available pools.")

        def sub_listavailpools_of_no_sku(self, session, sku):
                cmd="subscription-manager list --available"
                (ret, output)=self.runcmd(session, cmd, "listing available pools")

                if ret == 0:
                        if "no available subscription pools to list" not in output.lower():
                                if sku not in output:
                                        logging.info("The right available pools are listed successfully - sku %s is not in available pools."%sku)
                                        return None
                                else:
                                        raise error.TestFail("Not the right available pools are listed! - sku %s is in available pools."%sku)

                        else:
                                logging.info("There is no Available subscription pools to list!")
                                return None
                else:
                        raise error.TestFail("Test Failed - Failed to list available pools.")


        def cnt_check_kernel_version(self, session):
                logging.info(' ----- Begin to get kernel version -----')

                cmd="uname -r"
                (ret, output)=self.runcmd(session, cmd, 'get kernel information', timeout="18000")

                if ret == 0 :
                        current_kernel_version = 'kernel-%s' %output
                        logging.info("It's successfully to get kernel version: %s" %current_kernel_version)
                	logging.info(' ----- End to get kernel version -----')
                        return current_kernel_version

                else:
                        logging.error('Failed to get /etc/redhat-release file')
                	logging.info(' ----- End to get kernel version -----')
                        return False
                return False

        def cnt_check_redhat_release(self, session):
                logging.info(' ----- Begin to get redhat release ----- ')

                cmd='cat /etc/redhat-release'
                (ret, output)=self.runcmd(session, cmd, 'get redhat-release', timeout="18000")

                if ret == 0 :
                        logging.info("It's successfully to get %s from /etc/redhat-release" %output)
                	logging.info(' ----- End to get redhat release ----- ')
                        return output
                else:
                        logging.error('Failed to get information from /etc/redhat-release')
                	logging.info(' ----- End to get redhat release ----- ')
                        return False
                return False

        def cnt_number_elments_in_queue(self, mlist):
                ctr = 0
                tlen = len(mlist)

		if len(mlist) >= 100:
			logging.info("<< Note: since the output of the command is too long(greater than 100 lines) here, logged it as debug info. >>")

                for i in mlist:
                        ctr = ctr + 1
			if len(str(tlen)) == 4:
                        	logging.debug("[%4d/%d] %s" % (ctr, tlen, i))
			elif len(str(tlen)) == 3:
				logging.debug("[%3d/%d] %s" % (ctr, tlen, i))
			elif len(str(tlen)) == 2:
                                logging.info("[%2d/%d] %s" % (ctr, tlen, i))
			else:
				logging.info("[%d/%d] %s" % (ctr, tlen, i))

        def check_product_status(self, session, status):
            cmd = "subscription-manager list --installed | grep 'Status:'"
            (ret, output) = self.runcmd(session, cmd, "check --installed product status")
            if ret == 0 and status == output.split(":")[1].strip() :
                logging.info("It's successful to check --installed product status as: %s" % status)
            else:
                raise error.TestFail("Test Failed - failed to check --installed product status as: %s" % status)

        def check_product_status_details(self, session, status):
            cmd = "subscription-manager list --installed | grep 'Status Details:'"
            (ret, output) = self.runcmd(session, cmd, "check --installed product status details")
            if ret == 0 and status == output.split(":")[1].strip() :
                logging.info("It's successful to check --installed product status details as: %s" % status)
            else:
                raise error.TestFail("Test Failed - failed to check --installed product status details as: %s" % status)

        def check_status_overall(self, session, status):
            cmd = "subscription-manager status | grep 'Overall Status:'"
            (ret, output) = self.runcmd(session, cmd, "check subscription-manager status overall")
            if ret == 0 and status == output.split(":")[1].strip() :
                logging.info("It's successful to check subscription-manager status overall as: %s" % status)
            else:
                raise error.TestFail("Test Failed - failed to check subscription-manager status overall as: %s" % status)

        def restart_rhsmcertd(self, session):
            # restart rhsmcertd service
            cmd = "service rhsmcertd restart"
            (ret, output) = self.runcmd(session, cmd, "restart rhsmcertd service")
            if ret == 0:
                logging.info("It's successful to restart rhsmcertd service")
            else:
                raise error.TestFail("Test Failed - failed to restart rhsmcertd service")

        def clear_product_cert(self, session):
             # remove all product certs
            cmd = "rm -f *.pem"
            (ret, output) = self.runcmd(session, cmd, "remove all product certs")
            if ret == 0:
                logging.info("It's successful to remove all product certs")
            else:
                raise error.TestFail("Test Failed - failed to remove all product certs")

        def add_product_cert(self, session, cert_name):
            # add product cert
            cmd = "cp /etc/pki/product/tmp/%s /etc/pki/product/" % cert_name
            (ret, output) = self.runcmd(session, cmd, "add product certs: %s" % cert_name)
            if ret == 0:
                logging.info("It's successful to add product certs: %s" % cert_name)
            else:
                raise error.TestFail("Test Failed - failed to add product certs: %s" % cert_name)

        def remove_product_cert(self, session, cert_name):
            # remove product cert
            cmd = "rm -f /etc/pki/product/" % cert_name
            (ret, output) = self.runcmd(session, cmd, "remove product certs: %s" % cert_name)
            if ret == 0:
                logging.info("It's successful to remove product certs: %s" % cert_name)
            else:
                raise error.TestFail("Test Failed - failed to remove product certs: %s" % cert_name)

        # ========================================================
        #       3. 'SAM Server' Test Common Functions
        # ========================================================

        def sam_create_user(self, session, username, password, email):
                #create user with username, password and email address
                cmd="headpin -u admin -p admin user create --username=%s --password=%s --email=%s"%(username, password, email)
                (ret, output)=self.runcmd(session, cmd, "creating user")

                if (ret == 0) and ("Successfully created user" in output):
                        logging.info("It's successful to create user %s with password %s and email %s."%(username, password, email))
                else:
                        raise error.TestFail("Test Failed - Failed to create user %s with password %s and email %s."%(username, password, email))

        def sam_is_user_exist(self, session, username):
                # check a user exist or not
                cmd="headpin -u admin -p admin user list"
                (ret, output)=self.runcmd(session, cmd, "listing user")

                if (ret == 0) and (username in output):
                        logging.info("User %s exists."%(username))
                        return True
                else:
                        logging.info("User %s does not exist."%(username))
                        return False

        def sam_delete_user(self, session, username):
                #delete user with username
                if self.sam_is_user_exist(session, username):
                        cmd="headpin -u admin -p admin user delete --username=%s"%(username)
                        (ret, output)=self.runcmd(session, cmd, "deleting user")

                        if (ret == 0) and ("Successfully deleted user" in output):
                                logging.info("It's successful to delete user %s."%(username))
                        else:
                                raise error.TestFail("Test Failed - Failed to delete user %s."%(username))
                else:
                        logging.info("User %s to be deleted does not exist."%(username))

        def sam_create_org(self, session, orgname):
                #create organization with orgname
                cmd="headpin -u admin -p admin org create --name=%s"%(orgname)
                (ret, output)=self.runcmd(session, cmd, "creating organization")

                if ret == 0 and "Successfully created org" in output:
                        logging.info("It's successful to create organization %s."%orgname)
                else:
                        raise error.TestFail("Test Failed - Failed to create organization %s."%orgname )


        def sam_is_org_exist(self, session, orgname):
                #check an organization existing or not
                cmd="headpin -u admin -p admin org list"
                (ret, output)=self.runcmd(session, cmd, "list organization")

                if ret == 0 and orgname in output:
                        logging.info("Organization %s exists."%orgname)
                        return True
                else:
                        logging.info("Organization %s does not exist."%orgname)
                        return False

        def sam_delete_org(self, session, orgname):
                #delete an existing organization
                if self.sam_is_org_exist(session, orgname):
                        cmd="headpin -u admin -p admin org delete --name=%s"%(orgname)
                        (ret, output)=self.runcmd(session, cmd, "delete organization")

                        if ret == 0 and "Successfully deleted org" in output:
                                logging.info("It's successful to delete organization %s."%orgname)
                        else:
                                raise error.TestFail("Test Failed - Failed to delete organization %s."%orgname)
                else:
                        logging.info("Org %s to be deleted does not exist."%(orgname))

        def sam_remote_create_org(self, samserverIP, username, password, orgname):
                #create organization with orgname
                cmd="headpin -u admin -p admin org create --name=%s"%(orgname)
                (ret, output)=self.runcmd_remote(samserverIP, username, password, cmd)

                if ret == 0 and "Successfully created org" in output:
                        logging.info("It's successful to create organization %s."%orgname)
                else:
                        raise error.TestFail("Test Failed - Failed to create organization %s."%orgname )

        def sam_remote_is_org_exist(self, samserverIP, username, password, orgname):
                #check an organization existing or not
                cmd="headpin -u admin -p admin org list"
                (ret, output)=self.runcmd_remote(samserverIP, username, password, cmd)

                if ret == 0 and orgname in output:
                        logging.info("Organization %s exists."%orgname)
                        return True
                else:
                        logging.info("Organization %s does not exist."%orgname)
                        return False

        def sam_remote_delete_org(self, samserverIP, username, password, orgname):
                #delete an existing organization
                if self.sam_remote_is_org_exist(samserverIP, username, password, orgname):
                        cmd="headpin -u admin -p admin org delete --name=%s"%(orgname)
                        (ret, output)=self.runcmd_remote(samserverIP, username, password, cmd)

                        if ret == 0 and "Successfully deleted org" in output:
                                logging.info("It's successful to delete organization %s."%orgname)
                        else:
                                raise error.TestFail("Test Failed - Failed to delete organization %s."%orgname)
                else:
                        logging.info("Org %s to be deleted does not exist."%(orgname))


        def sam_create_env(self, session, envname, orgname, priorenv):
                ''' create environment belong to organizaiton with prior environment. '''

                cmd="headpin -u admin -p admin environment create --name=%s --org=%s --prior=%s"%(envname, orgname, priorenv)
                (ret, output)=self.runcmd(session, cmd, "create environment")

                if ret == 0:
                        logging.info("It's successful to create environment '%s' - belong to organizaiton '%s' with prior environment '%s'."%(envname, orgname, priorenv))
                else:
                        raise error.TestFail("Test Failed - Failed to create environment '%s' - belong to organizaiton '%s' with prior environment '%s'."%(envname, orgname, priorenv) )

        def sam_check_env(self, session, envname, orgname, priorenv, desc='None'):
                ''' check environment info. '''

                cmd="headpin -u admin -p admin environment info --name=%s --org=%s" %(envname, orgname)
                (ret, output)=self.runcmd(session, cmd, "check environment detail info")

                if (ret == 0) and (envname in output) and (orgname in output) and (priorenv in output) and (desc in output):
                        logging.info("It's successful to check environment detail info.")
                else:
                        raise error.TestFail("Test Failed - Failed to check environment detail info.")

        def sam_is_env_exist(self, session, envname, orgname):
                ''' check if an environment of one org existing or not. '''

                cmd="headpin -u admin -p admin environment list --org=%s" %orgname
                (ret, output)=self.runcmd(session, cmd, "list environment")

                if ret == 0 and envname in output:
                        logging.info("Environment %s exists."%envname)
                        return True
                else:
                        logging.info("Environment %s does not exist."%envname)
                        return False

        def sam_delete_env(self, session, envname, orgname):
                ''' delete an existing environment. '''

                if self.sam_is_env_exist(session, envname, orgname):
                        cmd="headpin -u admin -p admin environment delete --name=%s --org=%s"%(envname, orgname)
                        (ret, output)=self.runcmd(session, cmd, "delete environment")

                        if ret == 0 and "Successfully deleted environment" in output:
                                logging.info("It's successful to delete environment %s."%envname)
                        else:
                                raise error.TestFail("Test Failed - Failed to delete environment %s."%envname)
                else:
                        logging.info("Environment %s to be deleted does not exist."%(envname))

        def sam_create_activationkey(self, session, keyname, envname, orgname):
                #create an activationkey
                cmd="headpin -u admin -p admin activation_key create --name=%s --org=%s --env=%s"%(keyname, orgname, envname)
                (ret, output)=self.runcmd(session, cmd, "create activationkey")

                if ret == 0 and "Successfully created activation key" in output:
                        logging.info("It's successful to create activationkey %s belong to organizaiton %s environment %s."%(keyname, orgname, envname))
                else:
                        raise error.TestFail("Test Failed - Failed to create activationkey %s belong to organizaiton %s environment %s."%(keyname, orgname, envname))

        def sam_is_activationkey_exist(self, session, keyname, orgname):
                #check an activationkey of one org existing or not
                cmd="headpin -u admin -p admin activation_key list --org=%s" %orgname
                (ret, output)=self.runcmd(session, cmd, "list activationkey")

                if ret == 0 and keyname in output:
                        logging.info("Activationkey %s exists."%keyname)
                        return True
                else:
                        logging.info("Activationkey %s doesn't exist."%keyname)
                        return False

        def sam_delete_activationkey(self, session, keyname, orgname):
                #delete an existing activation key
                if self.sam_is_activationkey_exist(session, keyname, orgname):
                        cmd="headpin -u admin -p admin activation_key delete --name=%s --org=%s"%(keyname, orgname)
                        (ret, output)=self.runcmd(session, cmd, "delete activationkey")

                        if ret == 0 and "Successfully deleted activation key" in output:
                                logging.info("It's successful to delete activation key %s."%keyname)
                        else:
                                raise error.TestFail("Test Failed - Failed to delete activation key %s."%keyname)
                else:
                        logging.info("Activationkey %s to be deleted doesn't exist."%(keyname))

        def sam_save_option(self, session, optionname, optionvalue):
                ''' save an option. '''

                cmd="headpin -u admin -p admin client remember --option=%s --value=%s"%(optionname, optionvalue)
                (ret, output)=self.runcmd(session, cmd, "save option")

                if ret == 0 and "Successfully remembered option [ %s ]"%(optionname) in output:
                        logging.info("It's successful to save the option '%s'."%optionname)
                else:
                        raise error.TestFail("Test Failed - Failed to save the option '%s'."%optionname)

        def sam_remove_option(self, session, optionname):
                ''' remove an option. '''

                cmd="headpin -u admin -p admin client forget --option=%s"%optionname
                (ret, output)=self.runcmd(session, cmd, "remove option")

                if ret == 0 and "Successfully forgot option [ %s ]"%(optionname) in output:
                        logging.info("It's successful to remove the option '%s'."%optionname)
                else:
                        raise error.TestFail("Test Failed - Failed to remove the option '%s'."%optionname)

        def sam_add_pool_to_activationkey(self, session, orgname, keyname):
                #find a pool belonging to the key's org
                cmd="curl -u admin:admin -k https://localhost/sam/api/owners/%s/pools |python -mjson.tool|grep 'pools'|awk -F'\"' '{print $4}'"%(orgname)
                (ret, output)=self.runcmd(session, cmd, "finding an available pool")

                if ret == 0 and "pools" in output:
                        poollist=self.__parse_sam_avail_pools(session, output)

                        #get an available entitlement pool to subscribe with random.sample
                        poolid = random.sample(poollist, 1)[0]
                        logging.info("It's successful to find an available pool '%s'."%(poolid))

                        #add a pool to an activationkey
                        cmd="headpin -u admin -p admin activation_key update --org=%s --name=%s --add_subscription=%s"%(orgname, keyname, poolid)
                        (ret, output)=self.runcmd(session, cmd, "add a pool to an activationkey")

                        if ret == 0 and "Successfully updated activation key [ %s ]"%(keyname) in output:
                                #check whether the pool is in the key
                                cmd="headpin -u admin -p admin activation_key info --name=%s --org=%s"%(keyname, orgname)
                                (ret, output)=self.runcmd(session, cmd, "check activationkey info")

                                if ret == 0 and poolid in output:
                                        logging.info("It's successful to add pool '%s' to activationkey '%s'."%(poolid, keyname))
                                        return poolid
                                else:
                                        raise error.TestFail("It's failed to add a pool to activationkey '%s'."%keyname)
                        else:
                                raise error.TestFail("Test Failed - Failed to add a pool to activationkey '%s'."%keyname)
                else:
                        raise error.TestFail("Test Failed - Failed to find an available pool")

        def __parse_sam_avail_pools(self, session, output):
                datalines = output.splitlines()
                poollist = []
                # pick up pool lines from output
                data_segs = []
                for line in datalines:
                        if "/pools/" in line:
                                data_segs.append(line)

                # put poolids into poolist
                for seg in data_segs:
                        pool=seg.split("/")[2]
                        poollist.append(pool)
                return poollist

        def sam_import_manifest_to_org(self, session, filepath, orgname, provider):
                #import a manifest to an organization
                cmd="headpin -u admin -p admin provider import_manifest --org=%s --name='%s' --file=%s"%(orgname, provider, filepath)
                (ret, output)=self.runcmd(session, cmd, "import manifest")

                if ret == 0 and "Manifest imported" in output:
                        logging.info("It's successful to import manifest to org '%s'."%orgname)
                else:
                        raise error.TestFail("Test Failed - Failed to import manifest to org '%s'."%orgname)

        def sam_is_product_exist(self, session, productname, provider, orgname):
                #check whether a product is in the product list of an org
                cmd="headpin -u admin -p admin product list --org=%s --provider='%s'"%(orgname, provider)
                (ret, output)=self.runcmd(session, cmd, "list products of an organization")

                if ret == 0 and productname in output:
                        logging.info("The product '%s' is in the product list of org '%s'."%(productname, orgname))
                        return True
                else:
                        logging.info("The product '%s' isn't in the product list of org '%s'."%(productname, orgname))
                        return False

        def sam_create_system(self, session, systemname, orgname, envname):
                #get environment id of envname
                cmd="curl -u admin:admin -k https://localhost/sam/api/organizations/%s/environments/|python -mjson.tool|grep -C 2 '\"name\": \"%s\"'"%(orgname, envname)
                (ret, output)=self.runcmd(session, cmd, "get environment id")

                if ret == 0 and envname in output:
                        #get the env id from output
                        envid=self.__parse_env_output(session, output)

                        if envid != "":
                                #create a new system using candlepin api
                                cmd="curl -u admin:admin -k --request POST --data '{\"name\":\"%s\",\"cp_type\":\"system\",\"facts\":{\"distribution.name\":\"Red Hat Enterprise Linux Server\",\"cpu.cpu_socket(s)\":\"1\",\"virt.is_guest\":\"False\",\"uname.machine\":\"x86_64\"}}' --header 'accept: application/json' --header 'content-type: application/json' https://localhost/sam/api/environments/%s/systems|grep %s"%(systemname, envid, systemname)

                                (ret, output)=self.runcmd(session, cmd, "create a system")

                                if ret == 0 and systemname in output:
                                        logging.info("It's successful to create system '%s' in org '%s'."%(systemname, orgname))
                                else:
                                        raise error.TestFail("Test Failed - Failed to create system '%s' in org '%s'."%(systemname, orgname))
                        else:
                                raise error.TestFail("Test Failed - Failed to get envid of env '%s' from org '%s'."%(envname, orgname))
                else:
                        raise error.TestFail("Test Failed - Failed to get env info from org '%s'."%orgname)

        def __parse_env_output(self, session, output):
                datalines = output.splitlines()
                envid=""
                for line in datalines:
                        if "\"id\"" in line:
                                envid=line.split(":")[1].split(",")[0].strip()
                                break
                return envid

        def sam_list_system(self, session, orgname, systemname):
                ''' list system and then check system list. '''

                cmd="headpin -u admin -p admin system list --org=%s" %(orgname)
                (ret, output)=self.runcmd(session, cmd, "list system")

                if (ret == 0) and (systemname in output):
                        logging.info("It's successful to list system '%s'."%systemname)
                else:
                        raise error.TestFail("Test Failed - Failed to list system '%s'."%systemname)

        def sam_is_system_exist(self, session, orgname, systemname):
                ''' check if the system exists. '''

                cmd="headpin -u admin -p admin system list --org=%s" %(orgname)
                (ret, output)=self.runcmd(session, cmd, "list system")

                if (ret == 0) and (systemname in output):
                        logging.info("The system '%s' exists."%systemname)
                        return True
                else:
                        logging.info("The system %s does not exist."%systemname)
                        return False

        def sam_list_system_detail_info(self, session, systemname, orgname, envname, checkinfolist):
                ''' list system info. '''

                cmd="headpin -u admin -p admin system info --name=%s --org=%s --environment=%s" %(systemname, orgname, envname)
                (ret, output)=self.runcmd(session, cmd, "list system detail info")

                if (ret == 0):
                        for i in checkinfolist:
                                if i in output:
                                        logging.info("The info '%s' is in command output."%i)
                                else:
                                        raise error.TestFail("Test Failed - Failed to list system detail info - the info '%s' is not in command output."%i)

                        logging.info("It's successful to list system detail info.")
                else:
                        raise error.TestFail("Test Failed - Failed to list system detail info.")

        def sam_unregister_system(self, session, systemname, orgname):
                ''' unregister a system. '''

                if self.sam_is_system_exist(session, orgname, systemname):
                        cmd="headpin -u admin -p admin system unregister --name=%s --org=%s"%(systemname, orgname)
                        (ret, output)=self.runcmd(session, cmd, "register system")

                        if ret == 0 and "Successfully unregistered System [ %s ]"%systemname in output:
                                logging.info("It's successful to unregister the system '%s' - belong to organizaiton '%s'."%(systemname, orgname))
                        else:
                                raise error.TestFail("Test Failed - Failed to unregister the system '%s' - belong to organizaiton '%s'."%(systemname, orgname))
                else:
                        logging.info("System '%s' to be unregistered does not exist."%(systemname))

        def sam_listavailpools(self, session, systemname, orgname):
                ''' list available subscriptions. '''
                cmd="headpin -u admin -p admin system subscriptions --org=%s --name=%s --available"%(orgname, systemname)
                (ret, output)=self.runcmd(session, cmd, "list available pools")

                if ret == 0 and ("Pool" in output or "PoolId" in output):
                        logging.info("The available pools are listed successfully.")
                        pool_list = self.__parse_sam_avail_pools_cli(session, output)
                        return pool_list
                else:
                        raise error.TestFail("Test Failed - Failed to list available pools.")
                        return None

        def __parse_sam_avail_pools_cli(self, session, output):
                datalines = output.splitlines()
                pool_list = []
                # split output into segmentations for each pool
                data_segs = []
                segs = []
                for line in datalines:
                        if "Pool:" in line or "PoolId" in line:
                                segs.append(line)
                        elif segs:
                                segs.append(line)
                        if "MultiEntitlement:" in line:
                                data_segs.append(segs)
                                segs = []
                # parse detail information for each pool
                for seg in data_segs:
                        pool_dict = {}
                        for item in seg:
                                keyitem = item.split(":")[0].replace(' ','')
                                valueitem = item.split(":")[1].strip()
                                pool_dict[keyitem] = valueitem
                        pool_list.append(pool_dict)
                return pool_list

        def sam_subscribetopool(self, session, systemname, orgname, poolid):
                ''' subscribe to an available subscription. '''
                cmd="headpin -u admin -p admin system subscribe --name=%s --org=%s --pool=%s"%(systemname, orgname, poolid)
                (ret, output)=self.runcmd(session, cmd, "subscribe to a pool")

                if ret == 0 and "Successfully subscribed System" in output:
                        logging.info("The available pool is subscribed successfully.")
                else:
                        raise error.TestFail("Test Failed - Failed to subscribe to available pool %s."%poolid)

        def sam_listconsumedsubscrips(self, session, systemname, orgname, poolname):
                ''' list consumed subscriptions. '''
                cmd="headpin -u admin -p admin system subscriptions --org=%s --name=%s "%(orgname, systemname)
                (ret, output)=self.runcmd(session, cmd, "list consumed subscriptions")

                if ret == 0 and poolname in output:
                        logging.info("The consumed subscriptions are listed successfully.")
                        return True
                else:
                        logging.info("No consumed subscriptions are listed.")
                        return False

        # ========================================================
        #       3. LDTP GUI test Functions
        # ========================================================
        redhat_release_version = "6"
        def set_os_release(self, session):
                global redhat_release_version
                # figure out redhat release
                cmd = "cat /etc/redhat-release"
                (ret, output) = self.runcmd(session, cmd, "figure out redhat release")
                if ret == 0 and "release 6.4" in output:
                        logging.info("Redhat release version is : release 6.4")
                        redhat_release_version = "6.4"
                elif ret == 0 and "release 6.3" in output:
                        logging.info("Redhat release version is : release 6.3")
                        redhat_release_version = "6.3"
                elif ret == 0 and "release 5" in output:
                        logging.info("Redhat release version is : release 5")
                        redhat_release_version = "5"
                else:
                        raise error.TestFail("Test Failed - Failed to get Redhat release version.")

        def get_os_release(self):
                global redhat_release_version
                print "redhat_release_version is %s" % redhat_release_version
                # figure out redhat release
                return redhat_release_version

        def get_virtual_machine_ip(self, session):
                #get virtual machine ip
                cmd = "ifconfig | grep 'inet addr' | grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1 }'"
                (ret, output) = self.runcmd(session, cmd, "get virtual machine ip")
                if ret == 0:
                        logging.info("It's successful to get virtual machine ip.")
                        return output
                else:
                        raise error.TestFail("Test Failed - Failed to get virtual machine ip.")

        def install_ldtp_in_guest(self, session, os_release):
                self.__install_ldtp(session, os_release)

        def install_ldtp_in_host(self, os_release):
                kvm_test_dir = os.path.join(os.environ['AUTODIR'], 'tests/kvm/tests/')
                ldtp_packages_path = os.path.join(kvm_test_dir, 'ldtp_packages')
                cmd = "cp %s/%s /tmp/" % (ldtp_packages_path, self.__get_ldtp_package(os_release))
                self.runcmd(None, cmd, "copy ldtp into /tmp/")
                self.__install_ldtp(None, os_release)

        def start_ldtp_remote_server(self, session, os_release, virtual_machine_ip):
                self.__set_ldtp_remote_server(virtual_machine_ip)
                self.__enable_ForwardX11()
                # if self.__check_whether_ldtp_started(session):
                if os_release == "5":
                        cmd = "ldtp -s"
                elif os_release == "6":
                        cmd = "ldtp"
                # cmd = "export DISPLAY=:0.0 && /usr/bin/gnome-terminal -e %s &" % cmd
                # launch_cmd = "python /tmp/start_ldtp_service.py"
                # cmd = "echo '*/1 * * * * export DISPLAY=:0.0 && /usr/bin/gnome-terminal -e \"python /tmp/start_ldtp_server.py\"' > /var/spool/cron/root"
                cmd = "mkdir -p /root/.config/autostart;echo \"[Desktop Entry]\nType=Application\nExec=gnome-terminal -e '%s'\nHidden=false\nX-GNOME-Autostart-enabled=true\nName[en_US]=aaa-ldtpd\nName=ldtpd\nComment[en_US]=\nComment=\" > /root/.config/autostart/gnome-terminal.desktop;chkconfig vncserver on;init 3;sleep 10;init 5" % cmd
                (ret, output) = self.runcmd(session, cmd, "Start ldtp server", timeout="60")

        def copy_ldtp_to_virtual_machine(self, vm, os_release):
                kvm_test_dir = os.path.join(os.environ['AUTODIR'], 'tests/kvm/tests/')
                ldtp_packages_path = os.path.join(kvm_test_dir, 'ldtp_packages')
                ldtp_path = ldtp_packages_path + "/" + self.__get_ldtp_package(os_release)
                self.copyfiles(vm, ldtp_path, "/tmp/", cmddesc="copying ldtp source to virtual machine")

        def __get_ldtp_package(self, os_release):
                if os_release == "5":
                        return "ldtp.tar.gz"
                elif os_release == "6":
                        return "ldtp-3.0.0.tar.gz"

        def __install_ldtp(self, session, os_release):
                if not self.__check_whether_ldtp_installed(session, os_release):
                        if os_release == "5":
                                cmd = "cd /tmp;tar -zxvf ldtp.tar.gz;cd /tmp/ldtp/;./autogen.sh --prefix=/usr; make;make install"
                        elif os_release == "6":
                                cmd = "cd /tmp;tar -zxvf ldtp-3.0.0.tar.gz;cd /tmp/ldtp2/;python setup.py build;python setup.py install"
                        self.runcmd(session, cmd, "install ldtp")

        def __check_whether_ldtp_installed(self, session, os_release):
                if os_release == "5":
                        folder = "ldtp"
                elif os_release == "6":
                        folder = "ldtp2"
                cmd = "test -d /tmp/" + folder + "/ && echo presence || echo notexist"
                (ret, output) = self.runcmd(session, cmd, "check whether ldtp has been installed")
                if "presence" in output:
                        logging.info("ldtp has already been installed!")
                        return True
                elif "notexist" in output:
                        logging.info("ldtp has not been installed!")
                        return False

        def __set_ldtp_remote_server(self, virtual_machine_ip):
                #cmd = "export LDTP_SERVER_ADDR=%s" % virtual_machine_ip
                #(ret, output) = self.runcmd(None, cmd, "Set ldtp server")
                os.environ["LDTP_SERVER_ADDR"] = virtual_machine_ip
                cmd="sed -i '/export LDTP_SERVER_ADDR=/d' /etc/profile"
                (ret,output)= self.runcmd(None,cmd,"removing old export LDTP_SERVER_ADDR")

                cmd = 'echo "export LDTP_SERVER_ADDR=%s" >> /etc/profile' % virtual_machine_ip
                (ret, output) = self.runcmd(None, cmd, "Set ldtp server")

        def __enable_ForwardX11(self):
                cmd = "sed -i '/   ForwardX11 yes/d' /etc/ssh/ssh_config"
                (ret, output) = self.runcmd(None, cmd, "removing old ForwardX11 yes")
                cmd = "echo '   ForwardX11 yes' >> /etc/ssh/ssh_config"
                (ret, output) = self.runcmd(None, cmd, "enable ForwardX11")

        def __check_whether_ldtp_started(self, session):
                # check whether ldtp service has been start
                cmd = "ps -ef | grep -i ldtp | grep -v grep"
                (ret, output) = self.runcmd(session, cmd, "check whether ldtp service has been start")
                if ret == 0:
                        logging.info("LDTP service has already been started")
                        return True
                else:
                        logging.info("LDTP service has not been started yet")
                        return False






