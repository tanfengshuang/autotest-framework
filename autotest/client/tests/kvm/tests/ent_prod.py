import sys, os, subprocess, commands, string, re, random, pexpect, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.tests.kvm.tests.ent_biz import ent_biz
import baserepo

class ent_prod(ent_biz):

        
        # ========================================================
        #       1. 'RHEL' Product Test - For CDN
        # ========================================================

        def cnt_rhel_test(self, session, vm, username, password, prodsku, basesku, testpids, content_level, subtype, release_list, blacklist = None):
                ''' This is the main function to do the content test of RHEL for CDN. '''

                logging.info("+++++++++++++++ Begin to Run CDN Content Test +++++++++++++++")
                try:    
                        try:                 
                                #[A] Content Test Preparation
                                #Get some base data
                                content_script_path = self.cnt_get_content_script_path()
                                metadata_path = os.path.join(content_script_path, 'manifest_metadata')
                                manifest_file = os.path.join(metadata_path, 'rhel_manifest.xml')
				repo_blacklist_file = os.path.join(metadata_path, 'rhel_data.xml')
				other_repo_file = os.path.join(metadata_path, 'rhel_repo.xml')

                                current_rel_version = self.cnt_get_os_release_version(session)
                                current_arch = self.cnt_get_os_base_arch(session)
		

				if not os.path.exists(manifest_file):
					raise error.TestFail("Not found rhel_manifest.xml")	
					
				self.cnt_check_kernel_version(session)
			        self.cnt_check_redhat_release(session)

                                #(1)Remove non-redhat repo, stop rhsmcertd and synchronize system time with clock.redhat.com
                                self.cnt_remove_non_redhat_repo(session)
                                #stop rhcertd because headling(autosubscribe) will run 2 mins after the machine is started, then every 24 hours after that, which will influence our test.
                                self.cnt_stop_rhsmcertd(session)

				#stop service yum-updatesd on RHEL5 in order to solve the yum lock issue
                                self.cnt_stop_yum_updatesd(session, current_rel_version)

                                #synchronize system time with clock.redhat.com, as a workaround when system time is not correct, which will result in no info display with "yum repolist" or "s-m repos --list"
                                self.cnt_ntpdate_redhat_clock(session)
                                                       
                               #(2)Register
                                self.sub_register(session, username, password, subtype)

				# get product pid and base pid
				basepid_cont = ''
				productid_conts = ''
				if ',' in testpids:
					pidnum = testpids.count(',')
					basepid_cont = testpids.split(',')[pidnum]
					productid_conts = testpids[0:len(productid_conts) - len(basepid_cont) - 1]
				else:
					productid_conts = testpids

				logging.info("The base pid %s will be checked in entitlement cert" %basepid_cont)
				logging.info("The product pid(s) %s will be checked in entitlement cert" %productid_conts)

                                #list available entitlement pools
                                availpoollist_prod=[]
                                if current_arch == 'i386' and (("92" in productid_conts) or ("94" in productid_conts) or ("132" in productid_conts) or ("146" in productid_conts)):
                                        #products SF, SAP, HPN are not supported on i386, and keep them pass currently.
                                        #availpoollist_prod = self.sub_listavailpools_of_no_sku(session, prodsku)
                                        logging.info("Product %s could not be supported on arch i386." % productid_conts)
                                        return
                                else:
                                        availpoollist_prod = self.sub_listavailpools_of_sku(session, prodsku)
                                
                                if len() == 0 or availpoollist_prod == None:
                                        logging.info("no SKU=%s available, so exist content test now. To confirm, run subscription-manager list --available"%prodsku)
                                        return
                                
                                #(3)Subscribe product
                                entitlement_cert_id_of_prod = self.cnt_subscribe_product_by_pool(session, prodsku, productid_conts, availpoollist_prod)
                                cert_fullpath_of_prod = "/etc/pki/entitlement/"+entitlement_cert_id_of_prod+".pem"
                                key_fullpath_of_prod = "/etc/pki/entitlement/"+entitlement_cert_id_of_prod+"-key.pem"
                       		 
                                # Subscribe base product                                
                                if basesku != "":
                                        availpoollist_baseprod = self.sub_listavailpools_of_sku(session, basesku)

                                        entitlement_cert_id_of_baseprod = self.cnt_subscribe_product_by_pool(session, basesku, basepid_cont, availpoollist_baseprod)
                         
                                        cert_fullpath_of_baseprod = "/etc/pki/entitlement/"+entitlement_cert_id_of_baseprod+".pem"
                                        key_fullpath_of_baseprod = "/etc/pki/entitlement/"+entitlement_cert_id_of_baseprod+"-key.pem"
				
                                # Main: Do Content Test for each product of the subscription, including:
                                #    verify repomanifest, verify_arch, verify_magic_listing_files, verify_treeinfo, verify_package_consistency, 
                                #    verify_productcert_installation, verify_packages_full_installation

				# when leave the release_list on web page empty, the value of release_list will be None(<type 'NoneType'>).
				# when set the release_list on web page None, the value of release_list will be "None"(<type 'str'>)
                                if release_list == None:
                                        release_list = current_rel_version      
					logging.info("release list to be tested: %s" % release_list)

				testresult = True
				releasever_set = ''
                                for cur_release in release_list.split(','):           
                                        if release_list != current_rel_version and release_list != "None":
                                                if not self.cnt_set_release(session, cur_release):
							if '6.' in cur_release or '7.' in cur_release:
								releasever_set = '--releasever=%s' % release_list
								logging.info("It's successfully to set variable --releasever=%s." % release_list)
							else:
								logging.error("Test Failed - Failed to set release of system." )

                                        #clean yum cache
                                        self.cnt_yum_clean_cache(session, releasever_set)

                                        #Do yum repolist with enabling all repos in /etc/yum.repo.d/redhat.repo
                                        #Disabled this test point since even find error repos rcm will not fix it since they think the error repos should not be available at the moment, in addition, the repos needed to test will be actually tested in following testing, so it should be okay to disable this test point.
					#if "level1" in content_level:
	                                #        testresult &= self.cnt_yum_repolist_all(session, blacklist, cur_release, releasever_set)

                                        for pid in productid_conts.split(','):
                                                # get repolist
                                                repolist = self.cnt_get_repolist_from_manifest(session, manifest_file, pid, current_arch, cur_release)

                                                #set to quit content test when repolist is empty currently
                                                if len(repolist) <= 0:
							logging.error("Repo list is empty!")
                                                        logging.error("Test Failed - There is no repolist for pid %s in release %s." % (pid, cur_release))
                                                        testresult &= False
						
						else:
							# Enable all testrepos
							self.cnt_enable_testrepos(session, repolist)
							
							# Change gpgkey for all testrepos for rhel snapshot testing against qa cdn
							if blacklist == 'GA':
								self.cnt_change_gpgkey_for_testrepos(session, repolist)

							# enable all the other needed repos which are not enabled by default
							self.cnt_enable_otherrepos(session, other_repo_file, pid, current_rel_version, current_arch)
							# if testing is blocked by some repos which are default enabled, please add them into file rhel_data.xml
							repo_black_list = self.cnt_get_repo_blacklist(session, repo_blacklist_file, current_rel_version, cur_release, current_arch)
							if len(repo_black_list) >= 1:
								self.cnt_disable_repos(session, repo_black_list)
							

							if "level1" in content_level:
                                        			# do yum repolist to check all enabled repos in /etc/yum.repo.d/redhat.repo
	                                		        testresult &= self.cnt_yum_repolist_enabled(session, blacklist, cur_release, releasever_set)

                                                	if "level1" in content_level:
                                                	        #[B] Do support repomanifest verification test.]
                                                	        testresult &= self.cnt_verify_repomanifest(session, repolist, manifest_file, pid, current_rel_version, current_arch, cur_release)
                                                	        #[C] Do support arch verification test.]
                                                	        testresult &= self.cnt_verify_arch(session, manifest_file, cert_fullpath_of_prod, pid, cur_release, "/%s" %pid)

                                                	logging.info("Below are all the repos to be tested:")
                                                	self.cnt_print_list(repolist)

                                                	#[D] Do content validation for each effective repo for pid $pid Start
                                                	checklisting_dist = 0
                                                	checklisting_beta = 0
                                                	checktreeinfo = 0

                                                	for repoid in repolist:
                                                		if ("level1" in content_level) or ("level2" in content_level):
		                                        	        pkgurl = self.cnt_get_pkgurl_from_repofile(session, repoid, current_rel_version, cur_release, current_arch)
									if type(pkgurl) == str:
										repodata_url = pkgurl.replace("Packages","repodata")
 
                                                	        if "level1" in content_level:
									release_black_list=['listing', '6.0', '5.0', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6']
                                                	                if checklisting_dist == 0 and "/dist/" in pkgurl:
										if blacklist != None:
											release_black_list.append(release_list)

                                                	                        testresult &= self.cnt_verify_magic_listing_files(session, vm, \
                                                	                                        cert_fullpath_of_prod, key_fullpath_of_prod, pkgurl, cur_release, current_arch, release_black_list, repoid) 
                                                	                
                                                	                        checklisting_dist = 1

                                                	                if checklisting_beta == 0 and "/beta/" in pkgurl:
										if blacklist != None and release_list != "6.7":
                                                                                        release_black_list.append(release_list)

                                                	                        testresult &= self.cnt_verify_magic_listing_files(session, vm, \
                                                	                                        cert_fullpath_of_prod, key_fullpath_of_prod, pkgurl, cur_release, current_arch, release_black_list, repoid) 
                                                	                
                                                	                        checklisting_beta = 1
                                                	                        
                                                	                if checktreeinfo == 0 and "/dist/" in pkgurl: 
										## treeinfo file will be under:
                								#example1:/content/dist/rhel/client/6/6Client/x86_64/os/
                								#example2:/content/dist/rhel/client/6/6Client/x86_64/kickstart/
                                                	                        os_url = re.sub("%s.*$" % current_arch, "%s/os" % current_arch, pkgurl)
										kickstart_url = os.path.join(os.path.split(os_url)[0],"kickstart")
										treeinfo_file_father_urls= [str(kickstart_url), str(os_url)]
										#treeinfo_file_father_urls= [str(os_url), str(kickstart_url)]
                                                	                        baseprod_ids = ['68', '69', '71', '72', '74', '76', '279', '294']
                                                	                        pidlist = productid_conts.split(',')
                                                	                        p_dir = '/mnt'
                                                	                        checksum_type = 'sha256sum'

                                               	                        	if len(list(set(baseprod_ids) & set(pidlist))) > 0:
                                               	                        	        if basesku != "":
                                               	                        	                testresult &= self.cnt_verify_treeinfo(session, cert_fullpath_of_baseprod, \
                                               	                        	                                        key_fullpath_of_baseprod, treeinfo_file_father_urls, p_dir, checksum_type, current_arch)
                                               	                        	        else:
                                               	                        	                testresult &= self.cnt_verify_treeinfo(session, cert_fullpath_of_prod, \
                                               	                        	                                        key_fullpath_of_prod, treeinfo_file_father_urls, p_dir, checksum_type, current_arch)
                                               	                        	        checktreeinfo = 1

									testresult &= self.cnt_verify_repo_relativeurl(session, repoid, current_rel_version, current_arch, manifest_file, pid, cur_release)

									testresult &= self.cnt_verify_package_consistency(session, cert_fullpath_of_prod, key_fullpath_of_prod,\
															 manifest_file, pid, current_arch, repoid, pkgurl, cur_release, releasever_set)
                                                	
                                                	        if "level2" in content_level:
									testresult &= self.cnt_verify_productcert_installation(session, repoid, releasever_set, blacklist,\
                                                                                                                              cert_fullpath_of_prod, key_fullpath_of_prod, repodata_url,															       manifest_file, pid, current_arch, cur_release)
							
							repohandled = False
							for repoid in repolist:
                                                	        if 'level3' in content_level:
									baserepoid =str(baserepo.baserepo().process())
									if blacklist == 'Beta':
										baserepoid = baserepoid.replace("-rpms","-beta-rpms")
									elif blacklist == 'HTB':
										baserepoid = baserepoid.replace("-rpms","-htb-rpms")

									if pid in ['68', '69', '71', '72', '74', '76', '279', '261', '294', '135', '155']:
									    #Handle repos: disable all repo and enable the base repo
									    if not repohandled:
									    
									        #Disable all repo
									    	self.cnt_disable_allrepo(session)
									
									        #Enable the base repo
                                                                	        self.cnt_enable_baserepo(session, baserepoid)

									    	repohandled = True

									    #Enable the test repo
									    self.cnt_enable_testrepos(session, [repoid])
									
									    #Start level3 testing with the base repo and test repo enabled
									    newrepologic = True
                                                	                    testresult &= self.cnt_verify_packages_full_installation(session, manifest_file, pid, repoid, current_arch, cur_release, releasever_set, blacklist, newrepologic)

                                                	                    #Disable the test repo but not disable the base repo
									    if baserepoid == repoid:
									        logging.info("Not disabling the test repo: %s, since it is the base repo." %baserepoid)
									    else:
									        self.cnt_disable_testrepos(session, [repoid])
									    
									else:
									    #Handle repos: enable the base repo
									    if not repohandled:
                                                                	    	self.cnt_enable_baserepo(session, baserepoid)
                                                                	    	repohandled = True

									    #No Need to use repo enable and disable
									    newrepologic = False
									    testresult &= self.cnt_verify_packages_full_installation(session, manifest_file, pid, repoid, current_arch, cur_release, releasever_set, blacklist, newrepologic)

                                if not testresult:
                                        raise error.TestFail("Test Failed - Failed to do main cdn content test.")
                                                
                        except Exception, e:
                                logging.error(str(e))
                                raise error.TestFail("Test Failed - error happened when do the cdn content test of RHEL:" + str(e))
                finally:
                        self.sub_unregister(session)
                        logging.info('+++++++++++++++ End to Run CDN Content Test +++++++++++++++')

        def cnt_subscribe_product_by_pool(self, session, prodsku, productid, availpoollist):
                '''subscribe a product by pool id which is got by the product's sku,
                   and then check the sku in the entitlement cert
                '''
                
                #get an available entitlement pool to subscribe with random.sample
                availpool = random.sample(availpoollist, 1)[0]
                if availpool.has_key('PoolID'):
                        poolid = availpool["PoolID"]
                elif availpool.has_key('PoolId'):
                        poolid = availpool["PoolId"]

                #get serialnumlist before subscription
                serialnumlist_pre = self.get_subscription_serialnumlist(session)
                
                #subscribe to the pool
                self.sub_subscribetopool(session, poolid)

                #get serialnumlist after subscription
                serialnumlist_post = self.get_subscription_serialnumlist(session)
                
                #get serial number of the entitlement cert id file
                entitlement_cert_id = self.cnt_cmp_arrays(serialnumlist_post, serialnumlist_pre)

                #check whether entitlement certificates generated and productid in them or not
                if len(entitlement_cert_id) != 0:
                        self.cnt_verify_sku_in_entitlement_cert(session, entitlement_cert_id[0], prodsku)
                        if productid != "":
                                for pid in productid.split(','):
                                      self.cnt_verify_productid_in_entitlement_cert(session, entitlement_cert_id[0], pid)  
                                #self.cnt_verify_productid_in_entitlement_cert(session, entitlement_cert_id[0], productid.split(',')[0])
                        return entitlement_cert_id[0]
                else:
                        raise error.TestFail("Test Failed - Failed to subscribe product by the sku %s" %prodsku)


        # ========================================================
        #       2. 'RHEL' OS upgrade - For CDN
        # ========================================================

        def cnt_updateOS_test(self, session, params, vm, env, username, password, sku, subtype, refer_redhat_release, refer_kernel_version, os_url, variant):
                #'''upgrade the os test'''
                logging.info("+++++++++++++++ Begin to Run RHEL Update OS Test +++++++++++++++")
                try:
                        try:
                                #[A] update os Test Preparation
                                #Get some base data
                                current_rel_version = self.cnt_get_os_release_version(session)
                                current_arch = self.cnt_get_os_base_arch(session)

                                # return value set to True
                                testresult = True

                                # Part1 - Get flavors and create repos files 
                                reponame_list = self.cnt_generate_repos_for_flavors(session, os_url, variant)

                                # Part2 - Get all packages from created repos
                                pkgs = self.cnt_repoquey_pkg_from_repo(session, reponame_list, 'NotInstalled')

                                # Part3 - Install all packages from created repos
                                self.cnt_install_group_pkgs(session, pkgs)

                                # Part4 - Register and subscribe 
                                self.sub_register(session, username, password, subtype)
                                
                                if self.cnt_subscribe_product_with_specified_sku(session, sku):
                                        if self.sub_isconsumed(session, sku):
                                                logging.info("It's successfully to subscribe pool with specified sku: %s" %sku)
                                                testresult = True
                                        else:
                                                logging.error("Failed - Failed to subscribe pool with specified sku: %s" %sku)
                                                testresult = False

				releasever_set = ''
	                        # clean yum cache
	                        self.cnt_yum_clean_cache(session, releasever_set)

 				###### Get redhat release ######
				old_redhat_release = self.cnt_check_redhat_release(session).strip()
				if old_redhat_release:
					logging.info('Current redhat release : %s' %old_redhat_release)

 				###### Get kernel version ######
				_old_kernel_version = self.cnt_check_kernel_version(session).strip()
				old_kernel_version ="%s.%s" %(_old_kernel_version, current_arch)
				if old_kernel_version:
					logging.info('Current kenel version : %s' %old_kernel_version)

				logging.info(' ----- Begin to Yum Update ----- ')

				# part6 - yum update
				if not self.cnt_updateOS_yum_update(session):
					testresult = False
		                # part7 - reboot code
				if not self.cnt_updateOS_reboot(session):
					testresult = False
		                # part8 - sleep code
		                logging.info('Sleep 300s now....')
		                time.sleep(300)
		                # part9 - get new session
		                logging.info('End of sleep!')
		                session,vm = self.init_session_vm(params,env)
				logging.info(' ----- End to Yum Update ----- ')

 				###### Check update ######
				if not self.cnt_updateOS_check_yum_status(session):
					testresult = False
				###### Check network ######
				if not self.cnt_updateOS_check_network(session):
					testresult = False
 				###### Check redhat release ######
				if not self.cnt_updateOS_cmp_redhat_release(session, refer_redhat_release):
					testresult = False
 				###### Check kernel version ######
	                        if not self.cnt_updateOS_cmp_kernel_version(session, current_arch, refer_kernel_version):
		                        testresult = False

                                if not testresult:
                                        raise error.TestFail("Test Failed - Failed to do update test.")

                        except Exception, e:
                                logging.error(str(e))
                                raise error.TestFail("Test Failed - error happened when do the update test of RHEL:"+str(e))
                finally:
#                        self.sub_unregister(session)
                        logging.info('+++++++++++++++ End to Run RHEL Update OS Test +++++++++++++++')



        # ========================================================
        #       3. 'RHEL' Product Test - For RHN
        # ========================================================

        def cnt_rhn_test(self, session, vm, username, password, server_url, content_level):
                ''' This is the main function to do the content test of RHEL for RHN. '''

                logging.info("+++++++++++++++ Begin to Run RHN Content Test +++++++++++++++")

                try: 
			try:                    
		                #[A] Content Test Preparation
		                #Get some base data
		                content_script_path = self.cnt_get_content_script_path()
		                metadata_path = os.path.join(content_script_path, 'manifest_metadata')
		                manifest_file = os.path.join(metadata_path, 'rhel_manifest.xml')

		                current_rel_version = self.cnt_get_os_release_version(session)
		                current_arch = self.cnt_get_os_base_arch(session)
				variant = self.cnt_get_variant_rhn(session, current_rel_version)
	
				if not os.path.exists(manifest_file):
					raise error.TestFail("Not found rhel_manifest.xml")

				self.cnt_register_rhn(session, username, password, server_url)

				testresult = True

				channel_list = self.cnt_get_channels_from_manifest_rhn(manifest_file, current_arch, variant)
				logging.info('Expected channel list got from packages manifest:')
				self.cnt_print_list(channel_list)

				if len(channel_list) == 0:
					logging.error("Got 0 channel from packages manifest")
				        raise error.TestFail("Test Failed - Got 0 channel from packages manifest.")

				if "level1" in content_level:
					# for now, this function can be only tested on RHEL6, as there is no param --available-channels on RHEL5
					if '6.5' in current_rel_version or "5" not in current_rel_version:
						testresult &= self.cnt_verify_channels_rhn(session, manifest_file, username, password, current_arch, variant)

				self.cnt_add_channels_rhn(session, username, password, channel_list)

				for channel in channel_list:
					if "level1" in content_level:
						testresult &= self.cnt_package_consistency_rhn(session, manifest_file, channel)

					if "level3" in content_level:
						testresult &= self.cnt_rhn_installation_rhn(session, manifest_file, channel)

				if not testresult:
					raise error.TestFail("Test Failed - Failed to do main rhn content test.")
					


                        except Exception, e:
                                logging.error(str(e))
                                raise error.TestFail("Test Failed - error happened when do the rhn content test of RHEL:" + str(e))
                finally:
			self.cnt_remove_channels_rhn(session, username, password)
                        self.cnt_unregister_rhn(session)
                        logging.info('+++++++++++++++ End to Run RHN Content Test +++++++++++++++')



	def cnt_get_variant_rhn(self, session, current_rel_version):
		# this function is used for >= RHEL6.2 | >= RHEL5.7
		# please modify this function if need to test other RHEL versions

		cmd = "ls /etc/pki/product/"
		(ret, output) = self.runcmd(session, cmd, "check /etc/pki/product/")
		productid_pems = output.splitlines()

		if ret != 0:
			raise error.TestFail("Failed to get variant from /etc/pki/product/")

		if '69.pem' in productid_pems:
			return "server"
		elif '68.pem' in productid_pems:
			return "client"
		elif '71.pem' in productid_pems:
			if '5' in current_rel_version and not '6.5' in current_rel_version:
				raise error.TestFail("Test Failed - It's no need to do rhn content test on 5Workstation.")
			else:
				return "workstation"
		elif '76.pem' in productid_pems:
			return "hpc-node"
		elif '72.pem' in productid_pems:
			return "server"
		elif '74.pem' in productid_pems:
			return "server"
		





















