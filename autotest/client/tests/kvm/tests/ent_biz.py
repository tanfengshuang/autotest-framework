import sys, os, subprocess, commands, string, re, random, pexpect
import logging
import time
from autotest_lib.client.common_lib import error
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils
from autotest_lib.client.tests.kvm.tests import pexpect
import ConfigParser
from sgmllib import SGMLParser

try:
        from xml.etree import ElementTree
except:
        from elementtree import ElementTree

class ent_biz(ent_utils):

        # ================================================
        #       1. Verify arch
        # ================================================

        def cnt_verify_arch(self, session, manifest_file, cert_fullpath, pid, cur_release, arch_father_path):
                # verify arch
                # cur_release example: cur_release='6Server'

                logging.info("--------------- Begin to verify arch for the product '%s' ---------------" % pid)

                entitlement_cert = self.cnt_parse_entitlement_cert_with_rct(session, cert_fullpath)
                if None != entitlement_cert:
                        if isinstance(entitlement_cert['Product'],list) == False:
                                product_list = [entitlement_cert['Product']]
                        else:
                                product_list = entitlement_cert['Product']

                        certarchlist_original = [item['Arch'].split(',') for item in product_list if item['ID'] == pid][0]
                else:
                        ent_str = '1.3.6.1.4.1.2312.9.1.%s.3:' % pid

                        cmd = 'openssl x509 -text -noout -in %s | grep "%s" -A 2' % (cert_fullpath, ent_str)
                        (ret, output) = self.runcmd(session, cmd, "verify arch in entitlement cert")

                        if (ret != 0 or output.find(ent_str) <= 0):
                                logging.error("--------------- End to verify arch for the product '%s': FAIL ---------------" % pid)
                                return False

                        dataline = output.splitlines()
                        t = []
                        for i in dataline:
                                if i.find(":") >= 0:
                                        t.append(i)
                        dataline = list(set(dataline) - set(t))

                        datastr = "".join(dataline).strip()
                        datastr = re.sub("\.", "", datastr)
                        certarchlist_original = datastr.strip().split(',')
                        certarchlist_original = [arch.strip() for arch in certarchlist_original]

                cert_arch_list = []
                for arch in certarchlist_original:
                        if arch == 'x86':
                                cert_arch_list.append('i386')
                        elif arch == 'ppc' and cur_release.find('6') >= 0:
                                cert_arch_list.append('ppc64')
                        elif arch == 'ppc64' and cur_release.find('5') >= 0:
                                cert_arch_list.append('ppc')
                        elif arch == 's390':
                                cert_arch_list.append('s390x')
                        elif arch == 'ia64' and cur_release.find('6') >= 0:
                                continue
                        else:
                                cert_arch_list.append(arch)
                logging.info('Supported arch in entitlement cert are: %s' % cert_arch_list)

                # get reference arch list from the manifest file which is generated from the output of parse_json.py
                # arch_father_path example : arch_father_path='/69' (in xml file)
                # return example: ['x86_64','x86']
		# soliu debug
                #exp_arch_list = parse_manifest_xml().get_element_list(manifest_file, arch_father_path)
		exp_arch_list = parse_manifest_xml().get_arch_list(manifest_file, arch_father_path, cur_release)

		if 'ERROR' in exp_arch_list:
			logging.error("Fail - Failed to get arch from package manifest: %s" % arch_father_path)
			logging.error("--------------- End to verify arch for the product '%s': FAIL ---------------" % pid)
			return False
		else:
                	if pid in ['92', '132', '146']:
                	        if 'i386' in exp_arch_list:
                	                exp_arch_list.remove('i386')

                	logging.info('\n')
                	logging.info('Expected supported arch are: %s' % exp_arch_list)
			list1 = self.cnt_cmp_arrays(exp_arch_list, cert_arch_list)
                	if len(list1) > 0:
                	        logging.error("The arch verification test FAILED for the product '%s':" % pid)

                	        logging.info('Below are arches in expected support arch list but not in entitlement cert:')
                	        self.cnt_print_list(list1)
                	        logging.error("--------------- End to verify arch for the product '%s': FAIL ---------------" % pid)
                	        return False
                	else:
                	        logging.info("--------------- End to verify arch for the product '%s': PASS ---------------" % pid)
                	        return True


        # ================================================
        #       2. Verify repo manifest
        # ================================================

        def cnt_verify_repomanifest(self, session, repolist_expected, manifest_file, productid, current_rel_version, current_arch, release):
                # verify repomanifest

                logging.info("--------------- Begin to verify repo manifest ---------------")

                logging.info('get repoid from yum repolist all:' )
                repolist_all = self.cnt_get_repolist_by_yum_repolist_all(session)
                repolist_totest = list(set(repolist_all))

                logging.info('\nRepo list to test:')
                self.cnt_print_list(repolist_totest)

                logging.info('Repo list expected:')
                self.cnt_print_list(repolist_expected)

                #update for single comparison currently till certv3 could get repos for one eng-product
                list1 = self.cnt_cmp_arrays(repolist_expected, repolist_totest)

                if len(list1) > 0: #or len(list2) > 0:
                        logging.error("The repo manifest test FAILED:")

                        logging.error('Below are repos in expected repo manifest but not in yum repolist:')
                        self.cnt_print_list(list1)
                        logging.error("--------------- End to verify repo manifest: FAIL ---------------")
			raise error.TestFail("Test Failed - Failed to verify repo manifest.")
                else:
			logging.info("Expected repos are all existing in test list!")
                        logging.info("--------------- End to verify repo manifest: PASS ---------------")
			return True

        def cnt_get_repolist_by_yum_repolist_all(self, session):
                # get repoid list from the result of yum repolist all

                cmd = 'yum repolist all'
                repolist = []
                isrepo = 0
                (ret, output) = self.runcmd(session, cmd, "yum repolist all", timeout = "2400")
                if (ret == 0):
                        yumdatalist = output.splitlines()
                        for dataline in yumdatalist:
                                dataline_head = dataline.split(' ', 1)[0]

                                # delete the last line preceded with "repolist:" and only get the real repo id list
                                if isrepo == 1 and dataline_head.find(':')<0:
					if dataline_head.find('/') >= 0:
						dataline_head = dataline_head.split('/')[0]
					if dataline_head.find('!') >= 0:
						dataline_head = dataline_head.split('!')[1]
                                        repolist.append(dataline_head)

                                if dataline_head == 'repo':
                                        isrepo = 1

                                if dataline_head == 'repolist':
                                        isrepo = 0

                        logging.info("It's successful to get repoid from yum repolist all")
                        return repolist
                else:
                        raise error.TestFail("Test Failed - Failed to get repoid from yum repolist all")

        def cnt_get_repolist_from_manifest(self, session, manifest_file, productid, cur_arch, release):
                # get repo id list from the repo manifest generated from the output of parse_json.py
                # productid example: '69,138,73'

                repolist = []
                plist = []
                pidlist = productid.split(',')
                for pid in pidlist:
                        repo_father_path = '/%s/%s' % (pid, cur_arch)

                        if release == "None":
                                plist = parse_manifest_xml().get_element_list(manifest_file, repo_father_path)

				if 'ERROR' in plist:
					logging.info("Not found this path in rhel_data.xml file: %s" % repo_father_path)
                                	return []
				else:
                                	repolist = plist + repolist
                        else:
                                repoid_ele = parse_manifest_xml().get_repoidElement(manifest_file, repo_father_path)
				if 'ERROR' in repoid_ele:
                                        logging.info("Not found this path in rhel_data.xml file: %s" % repo_father_path)
                                        return []
				else:
                                	for cur_repoid in repoid_ele:
                                	        if cur_repoid.get("releasever") == release:
                                	                repolist.append(cur_repoid.get("value"))

                return repolist

        def cnt_get_repo_blacklist(self, session, xmlfile, rel_version, release, arch):
                # get repo black list from xml file.
                if release == "None":
                        release = rel_version

		cmd = "grep '5-workstation' /etc/yum.repos.d/redhat.repo > /dev/null"
                (ret, output) = self.runcmd(session, cmd, "check whether there is 5Workstation in /etc/yum.repos.d/redhat.repo" )
                if (ret == 0):
                        rel_version = "5Workstation"

                tag_path = '/repoblacklist/%s/%s/%s' % (rel_version, release, arch)
		logging.info('tag_path = %s' % tag_path)

                blacklist = parse_manifest_xml().get_oneleaf(xmlfile, tag_path, "repoid")

		if 'ERROR' in blacklist:
			logging.info("Not found this path in rhel_data.xml file: %s" % tag_path)
			return []
		else:
			logging.info('Get black list from rhel_data.xml:')
			if len(blacklist) == 0:
				logging.info("Not found any black repos in this path in rhel_data.xml file: %s" % tag_path)
			else:
				for repo in blacklist:
			                logging.info('%s' % repo)
			return blacklist

	def cnt_disable_repos(self, session, black_list):
                # disable all the invaild repos in order to ensure the testing can go through smoothly
		for repo in black_list:
			cmd = "subscription-manager repos --disable=%s" % repo
			(ret, output) = self.runcmd(session, cmd, "disable repo %s in /etc/yum.repos.d/redhat.repo" % repo)
			if (ret == 0):
				logging.info("It's successful to disable repo %s in /etc/yum.repos.d/redhat.repo" % repo)
			else:
				raise error.TestFail("Test Failed - Failed to disable repo %s in /etc/yum.repos.d/redhat.repo" % repo)


	def cnt_disable_repos_bk(self, session, black_list):
		# disable all the invaild repos in order to ensure the testing can go through smoothly

		cmd = """for i in $(echo "%s" | awk -F',' '{for(j=1;j<=NF;j++) print $j}'); do sed -i "$(($(grep -n "\[$i\]" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')+3)) s/1/0/" /etc/yum.repos.d/redhat.repo;done""" % ','.join(black_list)

                (ret, output) = self.runcmd(session, cmd, "disable the '%d' repos in /etc/yum.repos.d/redhat.repo" % len(black_list))

                if (ret == 0):
                        logging.info("It's successful to disable the '%d' repos /etc/yum.repos.d/redhat.repo." % len(black_list))
                else:
                        raise error.TestFail("Test Failed - Failed to disable the '%d' repos /etc/yum.repos.d/redhat.repo." % len(black_list))


	def cnt_enable_otherrepos(self, session, other_repo_file, pid, current_rel_version, current_arch):
		# get other needed repos and enable them

		tag_path = '/otherrepos/%s/%s/%s' % (pid, current_rel_version, current_arch)
		logging.info('tag_path = %s' % tag_path)

		repo_list = parse_manifest_xml().get_oneleaf(other_repo_file, tag_path, "repoid")

		if 'ERROR' in repo_list:
                        logging.info("Not found this path in rhel_repo.xml file: %s" % tag_path)
                        return []
                else:
                        logging.info('Get all the other needed repos list from rhel_repo.xml:')
			if len(repo_list) == 0:
				logging.info("Not found any other needed repos in this path in rhel_repo.xml file: %s" % tag_path)
			else:
				for repo in repo_list:
					logging.info('%s' % repo)
					cmd = "subscription-manager repos --enable=%s" % repo
					(ret, output) = self.runcmd(session, cmd, "enable other needed repo %s in /etc/yum.repos.d/redhat.repo" % repo)
					if (ret == 0):
						logging.info("It's successful to enable other needed repo %s in /etc/yum.repos.d/redhat.repo" % repo)
					else:
						logging.error("Test Failed - Failed to enable other needed repo %s in /etc/yum.repos.d/redhat.repo" % repo)


#			cmd = """for i in $(echo "%s" | awk -F',' '{for(j=1;j<=NF;j++) print $j}'); do sed -i "$(($(grep -n "\[$i\]" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')+3)) s/0/1/" /etc/yum.repos.d/redhat.repo;done""" % ','.join(repo_list)
#
#	                (ret, output) = self.runcmd(session, cmd, "enable the other needed '%d' repos in /etc/yum.repos.d/redhat.repo" % len(repo_list))
#
#	                if (ret == 0):
#        	                logging.info("It's successful to enable the other needed '%d' repos /etc/yum.repos.d/redhat.repo." % len(repo_list))
#                	else:
#                        	logging.error("Test Failed - Failed to enable the '%d' repos /etc/yum.repos.d/redhat.repo." % len(repo_list))

	def cnt_disable_allrepo(self, session):
		# Disabling all default enabled repos
		cmd = "subscription-manager repos --disable=*"
		(ret, output) = self.runcmd(session, cmd, "Disabling all default enabled repos")
		if (ret == 0):
			logging.info("sucessfully disabled all repos")
		else :
			logging.error("test Failed - Failed to diable default enabled repo")





        # ================================================
        #       3. Verify package consistency
        # ================================================

        # ---------- Package consistency verification for RHEL Product ----------

        def cnt_verify_package_consistency(self, session, cert_fullpath, key_fullpath, manifest_file, pid, cur_arch, repoid, pkgurl, release, releasever_set):
                # verify package consistency

                logging.info("--------------- Begin to verify package consistency for the repo '%s' of the product '%s' ---------------" % (repoid, pid))

                checkresult = True

                #[1] verify packages in 'package manifest' and 'repo metadata'
                checkresult &= self.cnt_verfiy_pkgs_between_pkgmanifest_and_repometadata(session, manifest_file, pid, cur_arch, repoid, release, releasever_set)

                #[2] verify packages in 'package directory' and 'repo metadata'
                checkresult &= self.cnt_verify_pkgs_between_pkgdir_and_repometadata(session, cert_fullpath, key_fullpath, repoid, pkgurl, releasever_set)

                if checkresult:
                        logging.info("--------------- End to verify package consistency for the repo '%s' of the product '%s': PASS ---------------" % (repoid, pid))
                else:
                        logging.error("--------------- End to verify package consistency for the repo '%s' of the product '%s': FAIL ---------------" % (repoid, pid))

                return checkresult

        def cnt_verfiy_pkgs_between_pkgmanifest_and_repometadata(self, session, manifest_file, pid, cur_arch, repoid, release, releasever_set):
                # [1] compare packages between 'package manifest' and 'repo metadata'.

                logging.info("Begin to compare packages between 'package manifest' and 'repo metadata' for the repo '%s'."% repoid)

                # get package list from 'repo metadata'
		# execute repoquery using --qf '%{name}-%{arch}'
                #fstr = '%{name}-%{arch}'#Don't Remove Line
		# execute repoquery using --qf '%{name}-%{version}-%{release}.%{arch}'
		fstr = '%{name}-%{version}-%{release}.%{arch}' #New Instead Line
                metadata_pkglist = self.cnt_get_pkgs_from_repo_metadata(session, repoid, fstr, releasever_set)
		if 'beta' in repoid:
                        repoid_dist = repoid.replace('-beta', '')
                        metadata_pkglist += self.cnt_get_pkgs_from_repo_metadata(session, repoid_dist, fstr, releasever_set)

                # make sure name-arch unique
                metadata_pkglist = list(set(metadata_pkglist))
                if metadata_pkglist == False:
                        return False

                # get package list from 'package manifest'
                repomanifest_pkglist = self.cnt_get_pkgs_from_package_manifest(manifest_file, pid, cur_arch, repoid, release)

                logging.info("There are '%d' packages in 'repo metadata' and there are '%d' packages in 'package manifest'." \
                        % (len(metadata_pkglist), len(repomanifest_pkglist)))

                #(list1, list2) = self.cnt_get_two_arrays_diff(metadata_pkglist, repomanifest_pkglist)
                #update for single comparison currently
                list1 = self.cnt_cmp_arrays(repomanifest_pkglist, metadata_pkglist)
                if len(list1) > 0: # or len(list2) > 0:
                	logging.error("Totally, there are '%d' packages in 'package manifest' but there are just '%d' of them existing in 'repo metadata' after check." % (len(repomanifest_pkglist), len(repomanifest_pkglist) - len(list1)))

                        logging.error("The package consistency test between 'package manifest' and 'repo metadata' FAILED for the repo '%s':" % repoid)

                        # print the list1 pkg
                        #logging.info("Below '%d' pkgs in 'repo metadata' could not be found in 'package manifest':" % len(list1))
                        #self.cnt_print_list(list1)
                        #logging.info('\n')

                        # print the list1 pkg
                        logging.error("Below '%d' pkgs in 'package manifest' could not be found in 'repo metadata':" % len(list1))
                        self.cnt_print_list(list1)

                        return False
                else:
                        logging.info("Verify package consistency between package manifest and repo metadata for the repo '%s': --- PASS" % repoid)
                        return True

        def cnt_verify_pkgs_between_pkgdir_and_repometadata(self, session, cert_fullpath, key_fullpath, repoid, pkgurl, releasever_set):
                # [2] compare packages between 'repo metadata' and 'package directory'.

                logging.info("Begin to compare packages between 'repo metadata' and 'package directory' for the repo '%s'." % repoid)

                fstr = '%{name}-%{version}-%{release}.%{arch}'
                metadata_pkglist = self.cnt_get_pkgs_from_repo_metadata(session, repoid, fstr, releasever_set)
                if metadata_pkglist == False:
                        return False

                pkg_dir_pkglist = self.cnt_get_pkgs_from_package_directory(session, cert_fullpath, key_fullpath, pkgurl)

		if not isinstance(pkg_dir_pkglist, bool):
	                logging.info("Totally, there are '%d' packages in 'repo metadata' and there are '%d' packages in 'package directory'" \
	                        % (len(metadata_pkglist), len(pkg_dir_pkglist)))

                (list1, list2) = self.cnt_get_two_arrays_diff(metadata_pkglist, pkg_dir_pkglist)
                if len(list1) > 0 or len(list2) > 0:
                        logging.error("The package consistency test between 'repo metadata' and 'package directory' FAILED for the repo '%s':" % repoid)

                        # print the list1 pkg
                        if len(list1) > 0:
		                logging.error("Below '%d' pkgs in 'repo metadata' could not be found in 'package directory':" % len(list1))
		                self.cnt_print_list(list1)
			else:
				logging.info("All packages pkgs in 'repo metadata' could be found in 'package directory'.")
			logging.info('\n')

                        # print the list2 pkg
                        if len(list2) > 0:
		                logging.error("Below '%d' pkgs in 'package directory' could not be found in 'repo metadata':" % len(list2))
		                self.cnt_print_list(list2)
			else:
				logging.info("All packages pkgs in 'package directory' could be found in 'repo metadata'.")

                        return False
                else:
                        logging.info("Verify package consistency between package directory and repo metadata for the repo '%s': --- PASS" % repoid)
                        return True

        def cnt_get_pkgs_from_package_manifest(self, manifest_file, pid, cur_arch, repoid, release):
                # get packages from manifest file
                #tag_path = '/%s/%s/%s' % (pid, cur_arch, repoid)
                tag_path = '/%s/%s' % (pid, cur_arch)
                tagname = 'packagename'

                plist = []
                pkgs_list = parse_manifest_xml().get_packagename(manifest_file, tag_path, repoid, release, tagname)

		if 'ERROR' in pkgs_list:
			logging.error("Fail - Failed to %s from rhel_manifest.xml" % tag_path)
			return []
		else:

                	for pkg in pkgs_list:
                	        pkgname_list = pkg.split(" ")
                	        pkgname = pkgname_list[0]
				# add the below 2 lines to get pkgs from manifest with format: "%{name}-%{version}-%{release}.%{arch}"
                	        pkgversion = pkgname_list[1]
                	        pkgrelease = pkgname_list[2]
                	        pkgarch = pkgname_list[3]

                	        #plist.append(pkgname + "-" + pkgarch) #Don't Remove Line
                	        plist.append(pkgname + "-" + pkgversion + "-" + pkgrelease + "." + pkgarch) #New Instead Line

                logging.info("It's successful to get '%d' packages from the package manifest under the repo of '%s/%s'. " % (len(plist),tag_path,repoid))
                return plist

        def cnt_get_pkgs_from_repo_metadata(self, session, repoid, fstr, releasever_set):
                # get pkglist with repoquery
                # fstr example: fstr = '%{name}-%{arch}'

                if repoid.find('source')>=0 or repoid.find('src')>=0:
			cmd = 'repoquery --show-dupes --all --repoid=%s --archlist=src --qf "%s" %s| sort -u' % (repoid, fstr, releasever_set)
                else:
			cmd = 'repoquery --show-dupes --all --repoid=%s --qf "%s" %s|sort -u' % (repoid, fstr, releasever_set)

                (ret, output) = self.runcmd(session, cmd, "get repolist with repoquery")

                if ret == 0:
			new_pkglist = []
                        pkglist = output.splitlines()
			for pkg in pkglist:
				if "Cannot retrieve repository metadata" not in pkg:
					new_pkglist.append(pkg)
                        logging.info("It's successful to get '%d' packages by repoquery for the repo '%s'." % (len(new_pkglist), repoid))
                        return new_pkglist
                else:
                        logging.error("Test Failed - Failed to get packages by repoquery for the repo '%s'." % (repoid))
                        return False

        def cnt_get_pkgs_from_package_directory(self, session, cert_fullpath, key_fullpath, pkgurl):
                # get rpm pkgs from packages directory.

                pkglist = []
                download_output=self.cnt_run_curl(session, cert_fullpath, key_fullpath, pkgurl)
		i=0
		while (i<10 and ((download_output == False) or ("An error occurred while processing your request" in download_output) or (str(download_output).strip() == ""))):
			time.sleep(10)
			logging.info("Faild to get rpm pkg list from packages directory %s, try again." % pkgurl)
			download_output=self.cnt_run_curl(session, cert_fullpath, key_fullpath, pkgurl)
			i+=1

		if (download_output == False) or ("An error occurred while processing your request" in download_output) or (str(download_output).strip() == ""):
			logging.error("Failed to get rpm pkg list from packages directory %s" % pkgurl)
			return False
		else:
			if "SRPMS" in pkgurl and "Packages/" in download_output:
				pkgurl = pkgurl+'Packages/'
				download_output=self.cnt_run_curl(session, cert_fullpath, key_fullpath, pkgurl)
				i=0
				while (i<10 and ((download_output == False) or ("An error occurred while processing your request" in download_output) or (str(download_output).strip() == ""))):
					time.sleep(10)
					logging.info("Failed to get rpm pkg list from packages directory %s, try again." % pkgurl)
					download_output=self.cnt_run_curl(session, cert_fullpath, key_fullpath, pkgurl)
					i+=1
				if (download_output == False) or ("An error occurred while processing your request" in download_output) or (str(download_output).strip() == ""):
					logging.error("Failed to get rpm pkg list from packages directory %s" % pkgurl)
					return False

			plist = []
			if '<HTML>' in download_output or '<html>' in download_output:
				pkgObj = PackageParser()
				pkgObj.feed(download_output)
				plist = pkgObj.obj
				pkgObj.close()
			else:
				plist = download_output.split('\n')
			for i in plist:
				if '.rpm' in i:
					pkg = re.sub('.rpm$', '', i)
					pkglist.append(pkg)
			logging.info("It's successful to get '%d' packages from the package directory '%s'."% (len(pkglist), pkgurl))
			return pkglist

        def cnt_get_pkgs_from_package_directory_old(self, session, cert_fullpath, key_fullpath, pkgurl):
                # get rpm pkgs from packages directory.

                pkglist = []
                download_output=self.cnt_run_curl(session, cert_fullpath, key_fullpath, pkgurl)
                if download_output == False:
                        logging.error("Faild to get rpm pkg list from packages directory %s" % pkgurl)
                        return False
                else:
                        if "SRPMS" in pkgurl and "Packages/" in download_output:
                                pkgurl = pkgurl+'Packages/'
                                download_output=self.cnt_run_curl(session, cert_fullpath, key_fullpath, pkgurl)
                                if download_output == False:
                                        logging.error("Faild to get rpm pkg list from packages directory %s" % pkgurl)
                                        return False

                        plist = []
                        if '<HTML>' in download_output or '<html>' in download_output:
                                pkgObj = PackageParser()
                                pkgObj.feed(download_output)
                                plist = pkgObj.obj
                                pkgObj.close()
                        else:
                                plist = download_output.split('\n')
                        for i in plist:
                                if '.rpm' in i:
                                        pkg = re.sub('.rpm$', '', i)
                                        pkglist.append(pkg)
                        logging.info("It's successful to get '%d' packages from the package directory '%s'."% (len(pkglist), pkgurl))
                        return pkglist

	def cnt_get_productid_from_repodata_directory(self, session, repoid, releasever_set, cert_fullpath, key_fullpath, repodata_url):

		fstr = "%{name}-%{version}-%{release}.%{arch}"
		cmd = "repoquery --show-dupes --all --repoid=%s --qf %s %s|sort -u" % (repoid, fstr, releasever_set)
		(ret, output) = self.runcmd(session, cmd, "get repolist with repoquery")

		pkglist = []
                if ret == 0:
			pkglist = output.splitlines()
			if len(pkglist) == 0:
				return True

                download_output=self.cnt_run_curl(session, cert_fullpath, key_fullpath, repodata_url)
                if download_output == False:
                        logging.error("Faild to get rpm pkg list from packages directory %s" %repodata_url)
                        return False
                else:
                        real_tree = []
                        if '<HTML>' in download_output or '<html>' in download_output:
				real_tree = []
                                lpr = ListParser()
                                lpr.feed(download_output)
                                real_tree = lpr.ret
                                logging.info('Repodata tree got from content url: %s' %real_tree)
                                lpr.close()
                        else:
				real_tree = ''
                                real_tree = download_output.split('\n')
                                print real_tree
                        if 'productid' in real_tree:
                                logging.info("It's successful to get productid from the repodata directory '%s'" %repodata_url)
                                return True
                        else:
                                logging.error("Failed to get productid from the repodata directory '%s'" %repodata_url)
                                return False



        # ================================================
        #       4. Verify treeinfo file
        # ================================================
        def cnt_verify_treeinfo(self, session, cert_fullpath, key_fullpath, treeinfo_father_urls, download_dir, checksum_type, current_arch):
                # verify treeinfo file

                logging.info("--------------- Begin to verify treeinfo file ---------------")
                ctr = 0
                for f in treeinfo_father_urls:
                        treeinfo_url = os.path.join(f,'treeinfo')
                        download_output = self.cnt_run_curl(session, cert_fullpath, key_fullpath, treeinfo_url)
                        if download_output == False or 'Unable to locate content' in download_output:
                                if ctr == 1:
                                        logging.error("--------------- End to verify treeinfo file: FAIL ---------------")
                                        return False
                                else:
                                        continue
                        else:
                                if '[general]' in download_output:
                                        logging.info("--------------- End to verify treeinfo file: PASS ---------------")
                                        # verify checksum
                                        if self.cnt_verify_checksum(session, f, cert_fullpath , key_fullpath, checksum_type , current_arch, download_dir):
                                                return True
                                        else:
                                                return False
                                else:
                                        logging.error("--------------- End to verify treeinfo file: FAIL ---------------")
                                        return False
                        ctr = ctr + 1

        def cnt_verify_checksum(self, session, treeinfo_fhr_url, cert_fullpath , key_fullpath, checksum_type , current_arch, download_dir):
                # verify files checksum in treeinfo url
                logging.info("--------------- Begin to verify CHECKSUM in treeinfo --------------")
                ret = self.cnt_generate_checksum(session, treeinfo_fhr_url, cert_fullpath, key_fullpath, checksum_type, current_arch, download_dir)
                if ret:
                        logging.info("--------------- End to verify CHECKSUM in treeinfo: PASS --------------")
                else:
                        logging.info("--------------- End to verify CHECKSUM in treeinfo: FAIL --------------")
		return ret

        def cnt_generate_checksum(self, session, treeinfo_father_url, cert_fullpath, key_fullpath, checksum_type, current_arch, download_dir):
                ## generate test checksum for files from treeinfo url
                logging.info("Begin to generate checksum file")

                child_dir = 'treeinfor_files_dir'
                download_files_dir = os.path.join(download_dir, child_dir)
                files_list = []

                if self.cnt_ready_directory(session, download_files_dir):
                        logging.info("It\'s successfully to ready directory for treeinfo checksum verify\n")
                else:
                        logging.error("Failed to ready directory for treeinfo checksum verify\n")
                        return False

		treeinfo_url = os.path.join(treeinfo_father_url,'treeinfo')

	        # get reference checksum file from treeinfo url
                rt = self.cnt_get_reference_checksum(session, treeinfo_url, cert_fullpath, key_fullpath, download_files_dir)
                rdict = dict(rt)

		#modify one key from "liveos/squashfs.img" to "LiveOS/squashfs.img" since the path has been changed
		if rdict.has_key("liveos/squashfs.img"):
        		rvalue = rdict["liveos/squashfs.img"]
        		rkey = "LiveOS/squashfs.img"
        		rdict[rkey] = rvalue
        		rdict.pop("liveos/squashfs.img")

                # tdict for all test checksum keys and values
                tdict = {}
                if len(rdict) >= 1:
                        logging.info("It\'s successfully to get reference checksum and wrote to dict %s\n" % rdict.items())
                        for f_name in rdict.keys():

                                # the download file url
                                target_file_url = os.path.join(treeinfo_father_url, f_name)
				s_name = f_name.split('/')[len(re.findall('/', f_name))]
                                save_file = os.path.join(download_files_dir, s_name)

                                # Estimated time of download
                                wtime = '5m'
                                if 'boot.iso' in f_name:
                                        wtime = '18m 49s'
                                if 'efidisk.img' in f_name :
                                        wtime = '3m 1s'
                                if 'initrd.img' in f_name:
                                        wtime = '2m 32s'
                                if 'install.img' in f_name:
                                        wtime = '10m 19s'
                                if 'efidisk.img' in f_name or 'efiboot.img' in f_name or 'product.img' in f_name:
                                        wtime = '< 1m'

                                logging.info('%s will be downloaded and will be saved as %s' % (f_name, save_file))
                                logging.info('Estimated time of download %s ...\n' % wtime)

                                # download with curl command
                                rt = self.cnt_run_curl(session, cert_fullpath, key_fullpath, target_file_url, save_file)

				if rt == False:
					logging.error("Failed to download %s from %s" % (save_file, target_file_url))
					continue
				else:
                                	# confirm the downloaded file
                                	cmd = "(if [ -s '%s' ];then echo \"SUCCESS to download file %s\";else  echo \"FAIL to download file %s\"; fi)" % (save_file, f_name, f_name)
                                	(ret, output) = self.runcmd(session, cmd, "find the generate file")
                                	if ret == 0 and 'SUCCESS' in output:
                                	        sig = self.cnt_write_Test_treeinfo_to_dict(session, download_files_dir, f_name, checksum_type, tdict)
                                	        logging.info("Finished to generate checksum for file %s" % f_name)
                                	        logging.info("It\'s successfully to generate checksum for %s \n" % f_name)

                                	else:
                                	        logging.info("Finished to generate checksum for file %s" % f_name)
                                	        logging.error("Failed to generate checksum for file %s\n" % save_file)

                        # compare two dict
                        rt = self.cnt_cmp_checksum(session, tdict, rdict)
                        if rt:
                                return True
                        else:
                                return False

                else:
                        logging.info("Not found [checksum] session in treeinfo file\n")
                        return True

        def cnt_write_Test_treeinfo_to_dict(self, session ,test_file_dir, target_file, hash_type, tdict):
                # generate checksums and write it to dict
                logging.info("Begin to write test checksum to dict")

		s_name = target_file.split('/')[len(re.findall('/', target_file))]

                # the file absolute path eg. /mnt/test/vmlinuz /mnt/test/product.img
                test_file_path = os.path.join(test_file_dir, s_name)
                cmd = '%s %s' %(hash_type, test_file_path)
                if ('initrd.img' in test_file_path) or ('vmlinuz' in test_file_path) or ('.img' in test_file_path) or ('.iso' in test_file_path):

                        logging.info('Ready to generate checksum for %s ' % test_file_path)
                        (ret, output) = self.runcmd(session, cmd, "Generate checksum", timeout = "2400")
                        if ret == 0 and len(output) > 32:
                                # Write Dict
                                tdict[target_file] = output.split(' ')[0]
                                logging.info("Write to Dict:key=%s, value=%s"  % (target_file,tdict[target_file]))
                                logging.info("Finished to write test checksum to dict\n")
                                return True
                        else:
                                logging.error("Finished to write None to dict\n")
                                return False
                return True

        def cnt_get_reference_checksum(self, session, url, cert_fullpath, key_fullpath, to_dir):
                # get reference checksum information
                # Example : checksum format
                #[checksums]
                #images/pxeboot/initrd.img = sha256:f9bfb54b1da1c5546fdffb486fb0493c14b9f60767b37a752e4c4fc65a7b7367
                #images/product.img = sha256:49ff22b99c8e382112b50a647c17e16b76ed3dc5f12149d63c8ef0c62267b55e
                #images/boot.iso = sha256:200cc29e435e4bcf64bcf311b4e330b1abf6b60d70b58983783b020c8216a8eb
                #images/pxeboot/vmlinuz = sha256:afd2d379da3e3bbad2a34adab1c430d263e329ebb1b24057c9147a961a92e793
                #images/install.img = sha256:491804c7516313db9a05576d4020c380e87352960398666f49bfe4441fc593bb

                logging.info("Begin to get reference checksum")

                to_file_name = 'reference_treeinfo_file'
                to_file = os.path.join(to_dir, to_file_name)

                # download reference file treeinfo with curl
                rt = self.cnt_run_curl(session, cert_fullpath, key_fullpath, url, to_file)
		if rt == False:
			logging.error("Failed to download reference file from %s" % url)
			return False

                # cat the file treeinfo text to output
                cmd = ("cat %s" % to_file)
                (ret, output) = self.runcmd(session, cmd, "get the file context", timeout = "2400")

                cmd = "(if [ -s '%s' ];then echo \"SUCCESS to download file %s\";else  echo \"FAIL to download file %s\"; fi)" % (to_file, to_file_name , to_file_name)
                (ret2, output2) = self.runcmd(session, cmd, "Check the download file")
                if ret2 == 0 and 'SUCCESS' in output2:
                        logging.info("It\'s successfully to download reference file %s\n"  % to_file_name)
                else:
                        logging.error("Failed to download reference file %s from %s\n" % (to_file_name, url))
                        return False

                # config parser
                config = ConfigParser.ConfigParser()
                myfile = 'tmpfile.cfg'
                logging.info("Write output information to file %s " % myfile)

                # write output text to file
                f = open(myfile, 'w')
                f.write(output)
                f.close()
                logging.info('Close file %s\n' % myfile)
                logging.info('Config Parser for file %s', myfile)
                config.read(myfile)
                mydict = {}

                # read config information to mydict
                if config.has_section('checksums'):
                        mydict = config.items('checksums')
                        logging.info('Write Config Parser information to Dict %s\n' % mydict)

                        if os.path.isfile(myfile):
                                os.remove(myfile)
                                logging.info('Remove file %s' % myfile)

                        return mydict
		#Note: since Config moudle is not sensitive to upper/lower word, so mydict is lower, and sometimes you need to modify the output
		else:
                        logging.info('Not found [checksums] in output')
			return mydict

        def cnt_cmp_checksum(self, session, Tdict, Rdict):
                # compare test checksum with reference
                logging.info("Begin to compare test checksum to reference checksum")
                logging.info('Test checksum dict %s\n' % Tdict.items())
                logging.info('Referenct checksum dict %s\n' % Rdict.items())
                fail_list = []
                succ_list = []
                sig = True
                for k in Tdict.keys():
                        tvalue = Tdict[k]

                        # find file name from reference information
                        if k in Rdict.keys():
                                rvalue = Rdict[k].split(':')[1]
                                logging.info("Test file checksum value = %s" % tvalue)
                                logging.info("Reference checksum value = %s" % rvalue)
                                if cmp(tvalue,rvalue) == 0:
                                        succ_list.append(k)
                                        logging.info("CHECKSUM(S) of %s are same\n" % k)
                                else:
                                        sig = False
                                        fail_list.append(k)
                                        logging.error("CHECKSUM(S) of %s are different\n" % k)

                        else:
                                logging.error("Failed to find %s in Reference treeinfo file" % k)
                if sig :
                        logging.info('CHECKSUMS of %d : %s --- PASS' % (len(succ_list), succ_list))
                        logging.info("It's successfully to comparate test checksum!\n")
                        return True
                else:
                        logging.info('CHECKSUMS of %d : %s --- FAIL' % (len(fail_list), fail_list))
                        logging.error("It's failed to compare test checksum\n")
                        return False

        def cnt_ready_directory(self, session, tdir):
                # Ready directory
                logging.info("Ready directory for test")

                cmd = "if [ ! -x %s ];then mkdir %s && echo \'Created Directory %s\';else rm -rf %s && mkdir %s && echo \'Removed and Created directory %s\';fi " % (tdir, tdir, tdir, tdir, tdir, tdir)
                (ret, output) = self.runcmd(session, cmd, "ready the directory")
                if ret == 0 :
                        return True
                else:
                        return False

        # ================================================
        #       5. Verify listing file
        # ================================================

        def cnt_verify_magic_listing_files(self, session, vm, cert_fullpath, key_fullpath, url, relver, arch, bklist, repoid):
                #verify release version and support arches listing files
                #url of having releasever: https://cdn.qa.redhat.com/content/dist/rhel/server/6/$releasever/$basearch/subscription-asset-manager/1/source/SRPMS
                #url without releasever: https://cdn.qa.redhat.com/content/dist/rhs/server/2.0/$basearch/source/SRPMS

		#no need to testing listing files for aarch64, for details please see the bug #1124975
		#listing files are only needed for URLs that have a variable in them (i.e. $releasever or $basearch).  Since we're not using variables in the aarch64 URLs, the listing files are not needed.
		if arch == "aarch64":
			logging.info("No need to verify listing file for aarch64 content testing.")
			return True

                logging.info("--------------- Begin to verify listing file ---------------")

                checkresult = True

                #verify release version listing file and sibling dirs
                if self.cnt_is_releasever_in_baseurl_from_repofile(session, repoid):
		        if relver != "None":
		                checkresult &= self.cnt_verify_listing_file(session, vm, cert_fullpath, key_fullpath, url, relver, arch, "release", bklist)
		        else:
		                relver = self.cnt_get_os_release_version(session)
		                if relver in url:
		                        checkresult &= self.cnt_verify_listing_file(session, vm, cert_fullpath, key_fullpath, url, relver, arch, "release", bklist)

                #verify support arches listing file and sibling dirs
                checkresult &= self.cnt_verify_listing_file(session, vm, cert_fullpath, key_fullpath, url, relver, arch, "arch", bklist)

                if checkresult:
                        logging.info("--------------- End to verify listing file: PASS ---------------")
                else:
                        logging.error("--------------- End to verify listing file: FAIL ---------------")

                return checkresult

        def cnt_verify_listing_file(self, session, vm, cert_fullpath, key_fullpath, url, relver, arch, option, black_list):
                #verify release version and support arches listing files
                #relver: release version of current system
                #option: two options, release or arch

                # copy debug cert and key to test machine
                debug_cert_path = os.path.join(self.cnt_get_content_script_path(), 'debug_cert')
                self.copyfiles(vm, os.path.join(debug_cert_path,"rcm-debug-20160209.crt"), "/tmp", cmddesc="copying content test debug cert")
                self.copyfiles(vm, os.path.join(debug_cert_path,"rcm-debug-20160209.key"), "/tmp", cmddesc="copying content test debug cert")

                if option == "release":
                        #get url of release version listing file
			print "*"*50
			if relver == "6.6":
				listing_url = re.sub("%s.*$" % "6\.6", "listing", url)
			else:
	                        listing_url = re.sub("%s.*$" % relver, "listing", url)
			print listing_url
                elif option == "arch":
                        #get url of support arch listing file
                        listing_url = re.sub("%s.*$" % arch, "listing", url)

		# Firstly - get the text from listing file of listing_url
                __tstr = self.cnt_run_curl(session, cert_fullpath, key_fullpath, listing_url)
                if __tstr == False:
                        logging.error("Faild to get text from %s" % listing_url)
                        return False

		text_in_file = __tstr.strip().split('\n')
		text_in_file.sort()
                logging.info('All %s listed in the listing file: %s' % (option, text_in_file))

                # Secondly - get sibling dirs from url
		dirs = []
                dirs_url = re.sub("listing", "", listing_url)

                dirs = self.cnt_run_curl(session, "/tmp/rcm-debug-20160209.crt", "/tmp/rcm-debug-20160209.key", dirs_url)

                if dirs == False:
                        logging.error("Faild to get sibling dirs of listing file %s" % dirs_url)
                        return False

		if 'HTML' in dirs:
			#download dirs is HTML code: <HTML>...</HTML>
			real_tree = []
			lpr = ListParser()
			lpr.feed(dirs)
			_real_tree = lpr.ret
               		logging.info('%s tree got from content url: %s' % (option, _real_tree))
			for i in _real_tree:
				if i.find('/') > 0:
					real_tree.append(i.replace('/', ''))
			lpr.close()
			black_list = black_list+['Parent Directory','Name', 'Last modified', 'Size']
		else:
			#download dirs is context: 6.0 6.1 6.2
			real_tree = ''
			real_tree = dirs.strip().split('\n')
               		logging.info('%s tree got from content url: %s' %(option, real_tree))

		# Remove the black_list from real_tree
               	logging.info("The black_list = %s" % (black_list))
                real_tree = list(set(real_tree) - set(black_list))
		real_tree.sort()
                logging.info("valid real tree %s: %s\n" % (option, real_tree))
                #release version list should be ascendent, but not for arch list.
                logging.info('%s in listing file : %s' % (option, text_in_file))
                logging.info('%s under url directory:%s' % (option, real_tree))

		if real_tree == text_in_file and '5.6' not in text_in_file:
                        logging.info("It's successful to verify listing file of %s: %s."% (option, listing_url))
                        return True
		else:
                        logging.error("Test Failed - Failed to verify listing file of %s : %s." % (option, listing_url))
                        return False

        # ================================================
        #       6. Verify productcert installation
        # ================================================

	def remove_none_base_productcert(self, session):
		# remove the none base product cert before installation the packages
		logging.info("------------------Begin to remove the none base product cert before install the packages-----------------------")

        	base_list = ['68.pem','69.pem','71.pem','72.pem','74.pem','76.pem', '279.pem', '226.pem', '227.pem','228.pem', '229.pem', '230.pem', '231.pem', '232.pem', '233.pem', '234.pem', '236.pem', '237.pem', '238.pem', '261.pem', '294.pem']
        	cmd = "ls /etc/pki/product"

        	(ret, output) = self.runcmd(session, cmd, "list product cert", timeout = "18000")

        	if ret == 0:
			product_list = output.split()
			if len(product_list) == 1 and product_list[0] in base_list:
				logging.info("There is only base product cert, no need to remove the none base product cert.")
                	else:
                        	for l in product_list:
                                	if l not in base_list:
                                        	cmd = "rm -f /etc/pki/product/%s" % l
                                        	(ret, output) = self.runcmd(session, cmd, "remove the none base product cert %s" % l, timeout = "18000")
                                        	if ret == 0:
                                                	logging.info("It is successful to remove the none base product cert: %s" % l)

		logging.info("--------------------End to remove the none product cert before install the packages-----------------------------")


        def cnt_verify_productcert_installation(self, session, repoid, releasever_set, blacklist, cert_fullpath_of_prod, key_fullpath_of_prod, repodata_url, manifest_file, pid, cur_arch, release):
                # smoke test for yum install one os package to verify product cert installation
		logging.info("--------------- Begin to verify productcert installation for the repo '%s' of the product '%s' ---------------"% (repoid, pid))

                checkresult = True
                if ("source" in repoid) or ("src" in repoid):
                        #yumdownloader source package
                        checkresult = self.cnt_yum_download_source_package(session, repoid, releasever_set, blacklist)
			return checkresult
                else:
                        #yum install one pkg and if the pkg is from os repoid then verify the product cert is installed successfully.
			#comment it for now, will improve this part after get more detailed info - https://hosted.englab.nay.redhat.com/issues/19076#note-20
			#if ("optional" not in repoid) and ("supplementary" not in repoid) and ("debug" not in repoid):
                        #	checkresult = self.cnt_get_productid_from_repodata_directory(session, repoid, releasever_set, cert_fullpath_of_prod, key_fullpath_of_prod, repodata_url)
                        #	if checkresult:
			#		logging.info("It's successfully to check product id for the repo '%s'"% (repoid))
                        #	else:
                        #        	logging.error("Failed to check product id for the repo '%s'"% (repoid))

			self.remove_none_base_productcert(session)
			checkresult &= self.cnt_yum_install_package(session, repoid, releasever_set, blacklist, manifest_file, pid, cur_arch, release)

			if checkresult:
				logging.info("--------------- End to verify productcert installation for the repo '%s' of the product '%s': PASS ---------------"% (repoid, pid))
			else:
				logging.error("--------------- End to verify productcert installation for the repo '%s' of the product '%s': FAIL -------------"% (repoid, pid))
			return checkresult

        def cnt_yum_install_package(self, session, repoid, releasever_set, blacklist, manifest_file, pid, cur_arch, release):
                #yum install one package from no-source repo

                formatstr = "%{name}"
                cmd = '''repoquery --pkgnarrow=available --all --repoid=%s --qf "%s" %s''' % (repoid, formatstr, releasever_set)
                (ret, output) = self.runcmd(session, cmd, "repoquery available packages", timeout = "2400")

                pkglist = []
                if ret == 0:
                        logging.info("It's successful to repoquery available packages for the repo '%s'."% repoid)

                        pkglist = output.strip().splitlines()
                        if len(pkglist) == 0:
                                logging.info("No available package for the repo '%s'."% repoid)
                                return True
                else:
                        logging.error("Test Failed - Failed to repoquery available packages for the repo '%s'."% repoid)
                        return False


		#get all packages list from packages manifest
		manifest_pkglist = []
		pkgs_list = self.cnt_get_package_list_from_manifest(session, manifest_file, pid, repoid, cur_arch, release)
		if len(pkgs_list) != 0:
			for pkg in pkgs_list:
				manifest_pkglist.append(pkg.split(" ")[0])
				logging.info(pkg.split(" ")[0])

		#get a available packages list which are uninstalled got from repoquery and also in manifest.
		avail_pkglist = []
		avail_pkglist = list(set(pkglist) & set(manifest_pkglist))

                #randomly get one package to install
		if len(manifest_pkglist) == 0:
			return True
		elif len(avail_pkglist) == 0:
			logging.error("There is no available packages for repo %s, as all packages listed in manifest have been installed before, please uninstall first, then re-test!" % repoid)
			return False
		else:
			pkgname = random.sample(avail_pkglist, 1)[0]

		if blacklist == 'Beta':
			cmd = "yum -y install --disablerepo=* --enablerepo=*beta* --skip-broken %s %s" % (pkgname, releasever_set)
		elif blacklist == 'HTB':
			cmd = "yum -y install --disablerepo=* --enablerepo=*htb* --skip-broken %s %s" % (pkgname, releasever_set)
		else:
			cmd = "yum -y install --skip-broken %s %s" % (pkgname, releasever_set)

                (ret, output) = self.runcmd(session, cmd, "yum install package '%s'" % pkgname, timeout = "18000")
                if ret == 0 and ("Complete!" in output or "Nothing to do" in output):
                        logging.info("It's successful to yum install package %s of repo %s." % (pkgname, repoid))
			checkresult = True
			if ("optional" not in repoid) and ("supplementary" not in repoid) and ("debug" not in repoid):
				if pid in ['68', '69', '71', '72', '74', '76', '279', '261', '294', '135', '155']:
					logging.info("For RHEL testing, skip to test the product cert since the rhel product cert will not be downloaded into '/etc/pki/product/' anew after install a rhel package and the default rhel product cert is located in the folder '/etc/pki/product-default/'.")
					checkresult = True
				else:
					checkresult = self.cnt_verify_productid_in_product_cert(session, pid)
                        return checkresult
                else:
                        logging.error("Test Failed - Failed to yum install package %s of repo %s." % (pkgname, repoid))
                        return False

        def cnt_yum_download_source_package(self, session, repoid, releasever_set, blacklist):
                #yum download one package from source repo

                formatstr = "%{name}-%{version}-%{release}.src"
                cmd = '''repoquery --pkgnarrow=available --all --repoid=%s --archlist=src --qf "%s" %s''' % (repoid, formatstr, releasever_set)

                (ret, output) = self.runcmd(session, cmd, "repoquery available source packages", timeout = "2400")

                #delete string "You have mail in /var/spool/mail/root" from repoquery output
                output = output.split("You have mail in")[0]

                pkglist = []
                if ret == 0:
                        logging.info("It's successful to repoquery available source packages for the repo '%s'." % repoid)

                        pkglist = output.strip().splitlines()
                        if len(pkglist) == 0:
                                logging.info("No available source package for the repo '%s'." % repoid)
                                return True
                else:
                        logging.error("Test Failed - Failed to repoquery available source packages for the repo '%s'." % repoid)
                        return False

                #randomly get one package to download
                pkgname = random.sample(pkglist, 1)[0]
		if blacklist == 'Beta':
			cmd = "yumdownloader --destdir /tmp --disablerepo=* --enablerepo=*beta* --source %s %s" % (pkgname, releasever_set)
		elif blacklist == 'HTB':
			cmd = "yumdownloader --destdir /tmp --disablerepo=* --enablerepo=*htb* --source %s %s" % (pkgname, releasever_set)
		else:
			cmd = "yumdownloader --destdir /tmp --source %s %s" % (pkgname, releasever_set)

                (ret, output) = self.runcmd(session, cmd, "yumdownloader source package '%s'" % pkgname, timeout = "18000")

                if ret == 0 and ("Trying other mirror" not in output):
                        cmd = "ls /tmp/%s*" % pkgname
                        (ret, output) = self.runcmd(session, cmd, "check source package '%s'" % pkgname)

                        if ret == 0 and pkgname in output:
                                logging.info("It's successful to yumdownloader source package %s of repo %s." % (pkgname, repoid))
                                return True
                        else:
                                logging.error("Test Failed - Failed to yumdownloader source package %s of repo %s." % (pkgname, repoid))
                                return False
                else:
                        logging.error("Test Failed - Failed to yumdownloader source package %s of repo %s." % (pkgname, repoid))
                        return False

	def list_product_cert_timer(self, session, pid):
		MAX = 37
		TM = 5

		logging.info("\n")
		logging.info("Ready for the product cert detection: %d times and once every %d seconds." % (MAX, TM))

		for i in range(1, MAX):# detect in 3 minutes
                	(ret, output) = self.runcmd(session, 'ls /etc/pki/product', 'list all the product cert')
			product_ids = output.split()

			if ret == 0 and '%s.pem' % pid in product_ids:
				logging.info("Timer:%d/%d - It's successfully to detect the /etc/pki/product/%s.pem file." % (i, MAX, pid))
				break
			else:
				logging.info("Timer:%d/%d - give %s more seconds to detect the /etc/pki/product/%s.pem file."% (i, MAX, TM, pid))
				time.sleep(TM)

		return product_ids

        def cnt_verify_productid_in_product_cert(self, session, pid):
                # verify product id
                pid_pem = "%s.pem" % pid
		str='1.3.6.1.4.1.2312.9.1.'
		base_list = ['68.pem', '69.pem', '71.pem', '72.pem', '74.pem', '76.pem', '279.pem', '294.pem']

		product_ids = self.list_product_cert_timer(session, pid)

		if pid_pem in product_ids:
			logging.info("It's successful to install the product cert %s!" % pid)

			cmd = 'openssl x509 -text -noout -in /etc/pki/product/%s.pem | grep %s%s' % (pid, str, pid)
                	(ret, output) = self.runcmd(session, cmd, "verify product id in product cert")

                	if (ret == 0 and output != ''):
                		logging.info(" It's successful to verify product id %s in product cert." % pid)
                		return True
			else:
				logging.error("Test Failed - Failed to verify product id %s in product cert." % pid)
				return False
		else:
			error_list = list(set(product_ids) - set(base_list))
			if len(error_list) == 0:
				logging.error("Test Failed - Failed to install the product cert %s.pem." % pid)
			else:
				logging.error("Test Failed - Failed to install the correct product cert %s, acutally the installed cert is %s." % (pid, error_list))
			return False

        # ================================================
        #       7. Verify packages full installation
        # ================================================

	# get packages needed to install from repoquery
        def cnt_get_pkglist_by_repoid(self,session,repoid, pkgname_format_nvra = ['name', 'version', 'release', 'arch']):
                #get pkglist of repoid by repoquery, name, version, release, arch need return or not, two choices: True|False
                #pkgname_format_nvra includes ['name', 'version', 'release', 'arch']

                formatstr = ""
                if 'name' in pkgname_format_nvra: formatstr = "%{name}"
                if 'version' in pkgname_format_nvra: formatstr += "-%{version}"
                if 'release' in pkgname_format_nvra: formatstr += "-%{release}"
                if 'arch' in pkgname_format_nvra: formatstr += ".%{arch}"

                cmd = "repoquery --all --repoid=%s " %repoid + "--qf '" + formatstr + "'"
                if ("source" in repoid) or ("src" in repoid):
                         cmd += " --archlist=src"

                (ret, output) = self.runcmd(session, cmd, "list all packages by repoquery for the repo '%s'" % repoid, timeout = "2400")
                if (ret == 0):
                        logging.info("It's successful to list all packages by repoquery for the repo '%s'." % repoid)
                        pkglist = output.strip().splitlines()
                        pkglist.sort()
                        return pkglist
                else:
                        logging.error("Test Failed - Failed to list all packages by repoquery for the repo '%s'." % repoid)
                        return False

        # Get system packages list before level3 to make sure the pkg in this list will not be removed during level3.
        def cnt_get_sys_pkglist(self, session):
                cmd = 'rpm -qa --qf "%{name}\n"'
                (ret, output) = self.runcmd(session, cmd, "list all packages in system before level3 ", timeout = "2400")
                if ret == 0:
                        sys_pkglist = [i for i in output.splitlines()]
                        logging.info("It's successful to get {0} packages from the system.\n".format(len(sys_pkglist)))
			return sys_pkglist
                else:
                        logging.error("Test Failed - Failed to list all packages in system before level3.")
                        return []

	def cnt_rm_pkg(self, session, pkg):
		'''
		Yum remove a package after install in order to resolve dependency issue which described in
		https://bugzilla.redhat.com/show_bug.cgi?id=1272902 
		'''
		cmd = "yum remove -y {0}".format(pkg)
		cmddesc = "remove package '{0}'".format(pkg)
		failed_pkglist = []
		(ret, output) = self.runcmd(session, cmd, cmddesc, timeout = "2400")
		if ret == 0:
			logging.info("It's successful to remove package '{0}'.\n".format(pkg))
			return True
		else:
			logging.warning("Warning -- Can't remove package '{0}'.\n".format(pkg))
			return False

        def cnt_verify_packages_full_installation(self, session, manifest_file, pid, repoid, arch, release, releasever_set, blacklist, newrepologic):
                logging.info("--------------- Begin to verify packages full installation of repo %s ---------------" % repoid)

                system_pkglist = self.cnt_get_sys_pkglist(session)
		# Use to store the failed packages after 'yum remove'.
		failed_rm_pkglist = []

                checkresult = True
                pkglist = self.cnt_get_package_list_from_manifest(session, manifest_file, pid, repoid, arch, release)

                if len(pkglist) != 0:
			# print the packages list ,and number every package in list
			plist = []
			u_plist = []

			for pkg in pkglist:
				if 'src' in pkg.split(' ')[3]:
					# src - e.g format "devtoolset-4.23.5-8.el6.src"
					one_rpm = "%s-%s-%s.%s" % (pkg.split(' ')[0], pkg.split(' ')[1], pkg.split(' ')[2], pkg.split(' ')[3])
				else:
					# rpm - e.g format "devtoolset"
					one_rpm = pkg.split(' ')[0]
				plist.append(one_rpm)

			#uniquify pkgs
			u_plist = list(set(plist))

                        if ("source" in repoid) or ("src" in repoid):
				logging.info("Ready to download below source packages:")
				self.cnt_number_elments_in_queue(u_plist)

				pkgs_str = ' '.join(u_plist)
				if pkgs_str != ' ':
					if blacklist == 'Beta':
						if newrepologic:
							cmd = 'yumdownloader --destdir /tmp --source %s %s' % (pkgs_str, releasever_set)
						else:
							cmd = 'yumdownloader --destdir /tmp --disablerepo=* --enablerepo=*beta* --source %s %s' % (pkgs_str, releasever_set)
					else:
						cmd = 'yumdownloader --destdir /tmp --source %s %s' % (pkgs_str, releasever_set)
				else:
					logging.info("There is no source packages exist!")

                                (ret, output) = self.runcmd(session, cmd, '', timeout = "18000")

                                if ret == 0:
                                        logging.info(" It's successful to download source packages.")
                                else:
					#soliu debug begin
					if "No Match for argument" in output:
   						error_list = []
   						str_list = output.split('\n')
   						for str in str_list:
           						if "No Match" in str:
                   						error_list.append(str)
   						failed_src_pkglist = []
   						for error in error_list:
							pkg = error.replace('No Match for argument ', '')
							new_pkg = pkg.replace('\r','')
           						failed_src_pkglist.append(new_pkg)

						logging.error("Failed to download following source packages: %s" % failed_src_pkglist)
					#soliu debug end

                                        logging.error("Test Failed - Failed to download source packages.")
                                        checkresult = False
                        else:
				logging.info("Ready to install below rpm packages:")
				self.cnt_number_elments_in_queue(u_plist)

				ctr = 0
				tnum = len(u_plist)

                                for pkg in u_plist:
					ctr = ctr + 1
					if blacklist == 'Beta':
						if newrepologic:
							cmd = 'yum install -y --skip-broken %s %s' % (pkg, releasever_set)
						else:
							cmd = 'yum install -y --disablerepo=* --enablerepo=*beta* --skip-broken %s %s' % (pkg, releasever_set)
					else:
						cmd = 'yum install -y --skip-broken %s %s' % (pkg, releasever_set)

	                                cmddesc = "[%s/%s] install package '%s' of repo %s" % (ctr, tnum, pkg, repoid)
                                        (ret, output) = self.runcmd(session, cmd, cmddesc, timeout = "18000")

                                        if ret == 0:
                                                if ("Complete!" in output) or ("Nothing to do" in output) or ("conflicts" in output):
                                                        logging.info(" It's successful to %s.\n" % cmddesc)
                                                else:
                                                        logging.error("Test Failed - Failed to %s.\n" % cmddesc)
                                                        checkresult = False
                                        else:
                                                if ("conflicts" in output):
                                                        logging.info(" It's successful to %s.\n" % cmddesc)
                                                else:
                                                        logging.error("Test Failed - Failed to %s.\n" % cmddesc)
                                                        checkresult = False

					if checkresult:
						if pkg not in system_pkglist:
							# Remove this package if it is not in the system package list.
							# It is used to solve the dependency issue which describe in https://bugzilla.redhat.com/show_bug.cgi?id=1272902.
							if not self.cnt_rm_pkg(session, pkg):
								failed_rm_pkglist.append(pkg)

                if checkresult:
                        logging.info("--------------- End to verify packages full installation of repo %s: PASS ---------------" % repoid)
                else:
                        logging.error("--------------- End to verify packages full installation of repo %s: FAIL ---------------" % repoid)
		
		if len(failed_rm_pkglist) != 0:	
			logging.warning("----------------------Warning -- Can't remove following packages: {0}".format(failed_rm_pkglist))

                return checkresult

	# get packages needed to install from packages manifest
        def cnt_get_package_list_from_manifest(self, session, manifest_file,pid, repoid, arch, release):
                # verify packages with the packages from manifest file

                logging.info("--------------- Begin to get package list from manifest ---------------")

                tag_path = '/%s/%s' %(pid, arch)
                tag_name = 'packagename'
                logging.info("tag_path is %s" % tag_path)
                logging.info("tag_name is %s" % tag_name)
                logging.info("repoid = %s" % repoid)
                logging.info("release = %s" % release)

                package_list = parse_manifest_xml().get_packagename(manifest_file, tag_path, repoid, release, tag_name)

                if 'ERROR' not in package_list:
                       	logging.info("It's successful to get %d packages from package manifest" % len(package_list))
                       	logging.info("--------------- End to get package list from manifest: PASS ---------------")
                       	return package_list
                else:
                        logging.error("Test Failed - Failed to get packages from package manifest file")
                        logging.info("--------------- End to get package list from manifest: FAIL ---------------")
                        return []

        # ================================================
        #       8. Verify repo relativeurl
        # ================================================

        def cnt_verify_repo_relativeurl(self, session, repoid, current_rel_version, arch, manifest_file, pid, release):
                # verify repo relative url

                logging.info("--------------- Begin to verify repo relative_url of repo %s ---------------" % repoid)
                # get repo url from file redhat.repo
                repourl = self.cnt_get_repourl_from_repofile(session, repoid, current_rel_version, release, arch) #replace relver with release
                repourl = re.sub("^.*content", "/content", repourl)
                logging.info("Test repo url : %s" % repourl)

                # get repo relative url from manifest
                #tag_path='/%s/%s/%s' %(pid,arch,repoid)
                tag_path = '/%s/%s' % (pid, arch)
                tag_name = 'relativeurl'

                relativeurl_list = parse_manifest_xml().get_relativeurl(manifest_file, tag_path, repoid, release, tag_name)

		if 'ERROR' in relativeurl_list:
			logging.error("Fail - Failed to get relativeurl %s from package manifest!" % tag_path)
			return []
		else:
                	is_equal = False
                	for mf_url in relativeurl_list:
                	        #mf_url = os.path.join(baseurl, r[1:])
                	        logging.info("Manifest repo url : %s" % mf_url)

                	        if repourl == mf_url:
                	                is_equal = True
                	                break

                	if is_equal:
                	        logging.info("It's successful to verify repo url.")
                	        logging.info("--------------- End to verify repo relative_url of repo %s: PASS ---------------" % repoid)
                	        return True
                	else:
                	        logging.error("Test Failed - Failed to verify repo url.")
                	        logging.error("--------------- End to verify repo relative_url of repo %s: FAIL ---------------" % repoid)
                	        return False

        # ================================================
        #       9. Verify all packages installable
        # ================================================

        def cnt_verify_all_packages_installable(self, session, repoid):
                # verify all packages could be installed by checksum, signature and package dependencies validation
                logging.info("--------------- Begin to verify all packages installable ---------------")

                checkresult = True
                pkglist = self.cnt_get_pkglist_by_repoid(session, repoid)

                if pkglist == False:
                        checkresult = False
                else:
                        for pkg in pkglist:
                                        checkresult &= self.cnt_verify_packages_checksum(session, pkg)
                                        checkresult &= self.cnt_verify_package_signature(session, pkg)
                                        if 'source' not in repoid:
                                                script_path = '/tmp/yum_install_assmueno.sh'
                                                checkresult &= self.cnt_verify_package_dependence(session, pkg, script_path)

                if checkresult:
                        logging.info("--------------- End to verify all packages installable: PASS ---------------")
                else:
                        logging.error("--------------- End to verify all packages installable: FAIL ---------------")

                return checkresult


        def cnt_verify_packages_checksum(self, session, pkg):
                # verify one package checksum

                if '.src' in pkg:
                        #cmd = 'yumdownloader --source %s --url --destdir=/tmp' % pkg
                        cmd = 'yumdownloader --source %s --url ' % pkg
                else:
                        #cmd = "yumdownloader %s --destdir=/tmp" % pkg
                        cmd = "yumdownloader %s " % pkg

                (ret, output) = self.runcmd(session, cmd, "yumdownloader package %s" % pkg, timeout = 2400)
                if (ret != 0) and "Could not download/verify pkg" in output:
                        logging.error("Test Failed - Failed to verify package checksum for %s" % pkg)
                        return False
                else:
                        rpm = '%s.rpm' % pkg
                        if os.path.isfile(rpm) and "kB/s" or "kB" in output:
                                # os.remove(rpm)
                                logging.info("It's successful to verify package checksum for %s" % pkg)
                                return True
                        elif not os.path.isfile(rpm):
                                logging.error("Test Failed - Failed to verify package checksum for %s" % pkg)
                                return False


        def cnt_verify_package_signature(self, session, pkg):
                # verify one package signature

                # verify rpm signature
                rpm = "%s.rpm" % pkg
                cmd = "rpm -K %s" % rpm
                (ret, output) = self.runcmd(session, cmd, "verify rpm signature")

                # remove rpm
                if os.path.isfile(rpm):
                        os.remove(rpm)
                        logging.info("remove the downloaded rpm :%s" % rpm)

                if (ret == 0):
                        logging.info("It's successful to verify signature for %s" % rpm)
                        return True
                else:
                        if os.path.isfile(rpm):
                                os.remove(rpm)
                        logging.error("Test Failed - Failed to verify signature for %s" % rpm)
                        return False


        def cnt_verify_package_dependence(self, session, pkg, script_path):
                # verify package dependence

                #cmd="yum install %s --assumeno" %pkg
                if self.cnt_generate_script_for_yum(session, pkg, script_path):
                        cmd = "expect %s" % script_path
                        (ret, output) = self.runcmd(session, cmd, "%s dependence verification" % pkg, timeout = 240000)
                        if (ret == 0):
                                logging.info("It's successful to verify package dependence for %s" % pkg)
                                return True
                        else:
                                logging.error("Test Failed - Failed to verify package dependence for %s" % pkg)
                                return False


        # ================================================
        #       10. Verify OS upgrade - yum update
        # ================================================

	def cnt_yum_check_update(self, session):
	        logging.info('Begin to yum check-update')
	        cmd = 'yum check-update'

	        (ret, output) = self.runcmd(session, cmd, "check update", timeout = "18000")
		return ret

	def cnt_check_network(self, session):
	        logging.info('Begin to check network')
	        cmd = 'yum repolist'

	        (ret, output) = self.runcmd(session, cmd, "check update", timeout = '18000')
	        if ret == 0:
	                logging.info("It's successfully to connect remote network")
	                return True
	        else:
	                logging.error('Failed to connet remote network')
	                return False

	def cnt_updateOS_yum_update(self, session):
	        logging.info('Begin to yum update and enable all repos')
	        logging.info('Please Waiting ... ')
	        cmd = 'yum update -y --enablerepo=* --skip-broken'
	        (ret, output)=self.runcmd(session, cmd, "yum update", timeout = '200000')
	        if ret == 0:
	                logging.info("It's successfully to yum update")
	                return True
	        else:
	                logging.error('Failed - Failed to yum update')
	                return False

	def cnt_updateOS_reboot(self, session):
	        cmd = 'reboot'
	        (ret, output) = self.runcmd(session, cmd, "reboot")
	        if ret == 0:
	                logging.info("It's successfully to reboot os")
	                return True
	        else:
	                logging.error('Failed - Failed to reboot os')
	                return False
	                testresult = False

	def cnt_updateOS_check_yum_status(self, session):
                logging.info(' ----- Begin to Yum Status ----- ')
	        yum_status = self.cnt_yum_check_update(session)
	        if yum_status == 100:
	                logging.info('Found packages available for an update')
	                logging.error('Failed - Failed to check update : 100')
	               	logging.info(' ----- End to Yum Status ----- ')
	                return False

	        elif yum_status == 0:
	                logging.info('No packages are available for update')
	                logging.info("It's successfully to check update : 0")
                	logging.info(' ----- End to Yum Status ----- ')
	                return True
	        elif yum_status == 1:
	                logging.error('Failed - Failed to check update : 1')
                	logging.info(' ----- End to Yum Status ----- ')
	                return False
	        else:
	                logging.error('Failed - Failed to check update')
                	logging.info(' ----- End to Yum Status ----- ')
	                return False

	def cnt_updateOS_check_network(self, session):
                logging.info(' ----- Begin to Check Network ----- ')
                cmd = 'yum repolist'

                (ret, output) = self.runcmd(session, cmd, "check update")
                if ret == 0:
                        logging.info("It's successfully to connect remote network")
                	logging.info(' ----- End to Check Network ----- ')
			return True
                else:
                        logging.error('Failed - Failed to connet remote network')
                	logging.info(' ----- End to Check Network ----- ')
			return False

	def cnt_updateOS_cmp_redhat_release(self, session, refer_redhat_release):
                logging.info(' ----- Begin to Check Redhat Release ----- ')
	        new_redhat_release = self.cnt_check_redhat_release(session).strip()
	        logging.info("It's successfully to get reference redhat release :%s" % refer_redhat_release)
	        if new_redhat_release == refer_redhat_release:
	                logging.info("It's successfully to check redhat release")
                	logging.info(' ----- End to Check Redhat Release ----- ')
	                return True
	        else:
	                logging.error('Failed - Failed to check redhat release')
                	logging.info(' ----- End to Check Redhat Release ----- ')
	                return False

	def cnt_updateOS_cmp_kernel_version(self, session, current_arch, refer_kernel_version):
	        logging.info(' ----- Begin to Check Kernel Version -----')
	        _new_kernel_version = self.cnt_check_kernel_version(session).strip()
		new_kernel_version = "%s.%s" %(_new_kernel_version, current_arch)
	        refer_kernel_version = '%s.%s' %(refer_kernel_version, current_arch)

	        logging.info("It's successfully to get reference kernel version : %s" %refer_kernel_version)
		logging.info("Compare the updated kernel version to reference kernel:")
		logging.info('Updated Kernel   :%s' %new_kernel_version)
		logging.info('Reference Kernel :%s' %refer_kernel_version)

	        if  refer_kernel_version == new_kernel_version:
	                logging.info("It's successfully to check kernel version")
	        	logging.info(' ----- End to Check Kernel Version -----')
	                return True
	        else:
	                logging.error('Failed - Failed to check kernel version')
	        	logging.info(' ----- End to Check Kernel Version -----')
	                return False


        def cnt_get_os_dirs(self, session, os_url):
                #Get dir anmes from HTML code: <HTML>...</HTML>

		logging.info("------------ Begin to get the building os directory ------------")
                cmd = 'curl %s' %os_url
                (ret, output) = self.runcmd(session, cmd, "get html web from %s" % os_url)
                if (ret == 0):
	                afs = DirParser()
	                afs.feed(output)
	                logging.info("It's successful to get directories from web %s" % os_url)
			logging.info("------------ End to get the building os directory ------------")
	                return afs.ret

                else:
                        logging.error("Test Failed - Failed to get directories from web %s" % os_url)
			logging.info("------------ End to get the building os directory ------------")
                        return False

        def cnt_get_flavors(self, session, os_url):
                # get flavors from os_url

		logging.info("------------ Begin to get flavors ------------")
                all_flavors = ent_biz().cnt_get_os_dirs(session, os_url)

	        if all_flavors:
                        logging.info("All directory     =  %s" %all_flavors)

                        blackfs = ['EFI/', 'Packages/', 'images/', 'isolinux/', 'repodata/', 'etc/', 'ppc/']
                        logging.info("Black directory   =  %s" %blackfs)

                        available_flavors = list(set(all_flavors) - set(blackfs))
                        logging.info("Available flavors =  %s\n" %available_flavors)

                        if len(available_flavors) >= 1:
                                logging.info("It's successfully to get the available flavors: %s" %available_flavors)
				logging.info("------------ End to get flavors------------")
                                return available_flavors
                        else:
                                logging.error("Failed - Failed to get the available flavors")
				logging.info("------------ End to get flavors------------")
                                return False

                else:
                        logging.error("Failed - Failed to get the all directory")
			logging.info("------------ End to get flavors------------")
                        return False

        def cnt_repoquey_pkg_from_repo(self, session, repolist, pkg_type):

	        pkglt = []
		for repo in repolist:
	                logging.info("------------ Begin to repoquery packages for %s ------------" %repo)

	                if pkg_type == 'All':
	                        cmd = 'repoquery -a --repoid=%s --qf %%{name}|sort -u' %repo
	                elif pkg_type == 'Installed':
	                        cmd = "repoquery -a --repoid=%s --qf %%{name}|xargs rpm -q|grep -v installed|sort -u" %repo
	                elif pkg_type == 'NotInstalled':
	                        cmd = 'repoquery -a --repoid=%s --qf %%{name}|xargs rpm -q|grep installed|sort -u' %repo
	                else:
	                        cmd = 'repoquery -a --repoid=%s --qf %%{name}|sort -u' %repo

	                (ret, output) = self.runcmd(session, cmd, "repoquery pkgs for repo %s" % repo)
	                if (ret == 0) :
	                        pkgs = output.replace('package','').replace(' is not installed','').split( )
				pkglt = pkglt + pkgs

	                        logging.info("It's successful to repoquery %d pkgs for repo %s" %(len(pkgs),repo))
				logging.info("------------ End to repoquery packages for %s ------------" %repo)
	                else:
	                        if 'rpm: no arguments given for query' in output:
	                                pkgs=[]
	                                logging.warning("It's successful to repoquery %s pkgs for repo %s" %(len(pkgs),repo))
					logging.info("------------ End to repoquery packages for %s ------------" %repo)
	                        else:
	                                logging.warning("Test Failed - Failed to repoquery pkgs for repo %s" % repo)
					logging.info("------------ End to repoquery packages for %s ------------" %repo)
                return pkglt

        def cnt_install_group_pkgs(self, session, pkglist):
                # yum install multiple packages together.

                if len(pkglist) >=1 :
                        logging.info("------------ Begin to install a group packages %d------------" %len(pkglist))
                        pkgstrs = ''
                        for p in pkglist:
                                pkgstrs = pkgstrs + ' ' + p
                        cmd = 'yum install -y --skip-broken %s' %pkgstrs
                        (ret, output) = self.runcmd(session, cmd, "yum install group packages" , timeout="18000")
                        if (ret == 0):
                                logging.info("It's successful to install %d packages" %len(pkglist))
                                logging.info("------------ End to install a group packages ------------")
                                return True
                        else:
                                logging.error("Test Failed - Failed to install %d packages" %len(pkglist))
                                logging.info("------------ End to install a group packages ------------")
                                return False

        #if status=True the packages which has been installed will be returned, or return pkgs which has not been installed.
        def cnt_get_pkgs_from_os(self, session, pkglist, status):
                # check packages from pkglist, and return the packages are installed/not installed thought setting status

                logging.info("------------ Begin to get package list from os for installed/not-installed ------------")
                installed_pkg = []
                not_installed_pkg = []
                for p in pkglist:
                        cmd="rpm -qa|grep ^%s-[0-9]" %p
                        (ret, output) = self.runcmd(session, cmd, "is package %s installed?" %p)
                        if ret == 0:
                                logging.info("Package %s has been installed!" %p)
                                if installed_pkg.count(p) <= 0:
                                        installed_pkg.append(p)
                        elif ret == 1:
                                logging.info("Package %s has not been installed!" %p)
                                if not_installed_pkg.count(p) <= 0:
                                        not_installed_pkg.append(p)
                        else:
                                logging.info("Package %s has not been installed!" %p)
                                if not_installed_pkg.count(p) <= 0:
                                        not_installed_pkg.append(p)

                logging.info("------------ End to get package list from os for installed/not-installed ------------")
                if status:
                        return installed_pkg
                else:
                        return not_installed_pkg

        def cnt_generate_repos_for_flavors(self, session, os_url, variant):
                # Generate repos files for flavors

                logging.info("------------ Begin to generate repos ------------")

		if os_url[-1] != '/':
			os_url = os_url + '/'

		logging.info("os_url=%s" %os_url)

                flavors = self.cnt_get_flavors(session, os_url)
		repolist = []
                for flr in flavors:
                        baseurl = os.path.join(os_url, flr)
                        reponame = '%s_%s' %(variant, flr[0:len(flr) - 1])
                        repo_file_path = os.path.join('/etc/yum.repos.d/', "%s.repo" %reponame)
                        rfile_str = """[%s]
name=%s
baseurl=%s
gpgcheck=0
gpgkey=http://download.devel.redhat.com/yum/RPM-GPG-KEY-redhatengsystems
enabled=1""" %(reponame, reponame, baseurl)

                        cmd = "echo \"%s\">%s && cat %s |grep baseurl" %(rfile_str, repo_file_path, repo_file_path)
                        (ret, output) = self.runcmd(session, cmd, "generate repo file %s" % repo_file_path)

                        if (ret == 0):
                                logging.info("It's successful to generate repo file %s" % repo_file_path)
				repolist.append(reponame)
                        else:
                                logging.error("Test Failed - Failed to generate repo file %s" % repo_file_path)

                logging.info("------------ End to generate repos ------------")
		return repolist


        # ================================================
        #       11. Verify RHN Content
        # ================================================

	def cnt_register_rhn(self, session, username, password, server_url):
		cmd = "rhnreg_ks --username=%s --password=%s --serverUrl=%s" % (username, password, server_url)

		if self.cnt_isregistered_rhn(session):
			if not self.cnt_unregister_rhn(session):
				logging.info("The system is failed to unregister from rhn server, try to use '--force'!")
				cmd += " --force"

		(ret, output) = self.runcmd(session, cmd, "register to rhn server.")
                if ret == 0:
                        logging.info("It's successful to register to rhn server.")
			cmd = "rm -rf /var/cache/yum/*"
			(ret, output) = self.runcmd(session, cmd, "delete yum cache data.")
			if ret == 0:
				logging.info("It's successful to delete yum cache data.")

			#cmd = "yum clean all"
			#(ret, output) = self.runcmd(session, cmd, "clean yum cache.")
			#if ret == 0:
			#	logging.info("It's successful to clean yum cache.")
                else:
                        raise error.TestFail("Test Failed - Failed to register to rhn server.")

	def cnt_isregistered_rhn(self, session):
		cmd = "ls /etc/sysconfig/rhn/systemid"
		(ret, output) = self.runcmd(session, cmd, "check if registered to rhn")
		if ret == 0:
			logging.info("The system is registered to rhn server now.")
			return True
		else:
			logging.info("The system is not registered to rhn server now.")
			return False

	def cnt_unregister_rhn(self, session):
		cmd = "rm -rf /etc/sysconfig/rhn/systemid"
		(ret1, output1) = self.runcmd(session, cmd, "unregister from rhn - delete systemid")

		cmd = "sed -i 's/enabled = 1/enabled = 0/' /etc/yum/pluginconf.d/rhnplugin.conf"
		(ret2, output2) = self.runcmd(session, cmd, "unregister from rhn - modify rhnplugin.conf")

		if ret1 == 0 and ret2 == 0:
			logging.info("It's successful to unregister from rhn server.")
			return True
		else:
			logging.error("Test Failed - Failed to unregister from rhn server.")
			return False

	def cnt_add_channels_rhn(self, session, username, password, channels):
		channel_default = []
		cmd = "rhn-channel --list --user=%s --password=%s" % (username, password)
		(ret, output) = self.runcmd(session, cmd, "list the channel which was added by default after register")
		if ret == 0:
			channel_default = output.splitlines()
			logging.info("It's successful to get default channel from rhn server: %s" % channel_default)

		for channel in channels:
			if channel not in channel_default:
				# add channel
				cmd = "rhn-channel --add --channel=%s --user=%s --password=%s" % (channel, username, password)
				(ret, output) = self.runcmd(session, cmd, "add channel %s" % channel)

			cmd = "rhn-channel --list --user=%s --password=%s" % (username, password)
			(ret, output) = self.runcmd(session, cmd, "check if channel %s was added successfully" % channel)
			channel_added = output.splitlines()

			if ret == 0 and channel in channel_added:
				logging.info("It's successful to add channel %s." % channel)
			else:
				raise error.TestFail("Test Failed - Failed to add channel %s." % channel)

		cmd = "yum repolist all"
		(ret, output) = self.runcmd(session, cmd, "yum repolist all")
		if ret == 0:
			logging.info("It's successful to yum repolist all.")

	def cnt_remove_channels_rhn(self, session, username, password, channels = None):
		if channels == None:
			cmd = "rhn-channel --list --user=%s --password=%s" % (username, password)
			(ret, output) = self.runcmd(session, cmd, "list all added channel already")
			channels = output.splitlines()
		else:
			pass

		for channel in channels:
			cmd = "rhn-channel --remove --channel=%s --user=%s --password=%s" % (channel, username, password)
			(ret, output) = self.runcmd(session, cmd, "remove channel %s" % channel)
			if ret == 0:
				logging.info("It's successful to remove channel %s." % channel)
			else:
				logging.info("Test Failed - Failed to remove channel %s." % channel)

	def cnt_get_channels_from_manifest_rhn(self, manifest_file, current_arch, variant):
		# get all channels from manifest which need testing
		repo_filter = "%s-%s" % (current_arch, variant)
		tag_path = "/"

		channel_list = []
		all_channel_list = []
		all_channel_list = parse_manifest_xml().get_element_list(manifest_file, tag_path)
		for channel in all_channel_list:
			if repo_filter in channel:
				channel_list.append(channel)
		return channel_list

	def cnt_verify_channels_rhn(self, session, manifest_file, username, password, current_arch, variant):
		# for now, this function can be only tested on RHEL6, as there is no param --available-channels on RHEL5

                logging.info("--------------- Begin to verify channel manifest ---------------")

		# get all channels which are not added
		available_channels = []
		cmd = "rhn-channel --available-channels --user=%s --password=%s" % (username, password)
		(ret, output) = self.runcmd(session, cmd, "get available channels with command rhn-channel", timeout = "180000")
		if ret == 0:
			available_channels = output.splitlines()
		else:
			logging.error("Failed to get available channels.")

		# get all channels which are already added
		added_channels = []
		cmd = "rhn-channel --list --user=%s --password=%s" % (username, password)
		(ret, output) = self.runcmd(session, cmd, "get added channels with command rhn-channel")
		if ret == 0:
			added_channels = output.splitlines()
		else:
			logging.error("Failed to get added channels.")

		channels_rhn = available_channels + added_channels

		# get all channels from manifest which are needed testing
		channels_manifest = self.cnt_get_channels_from_manifest_rhn(manifest_file, current_arch, variant)

                list1 = self.cnt_cmp_arrays(channels_manifest, channels_rhn)

                if len(list1) > 0:
			logging.error("Failed to verify channel manifest.")
                        logging.info('Below are channels in expected channel manifest but not in rhn-channel:')
                        self.cnt_print_list(list1)
                        logging.error("--------------- End to verify channel manifest: FAIL ---------------")
                        raise error.TestFail("Test Failed - Failed to verify channel manifest.")
                else:
                        logging.info("All Expected channels exist in test list!")
                        logging.info("--------------- End to verify channel manifest: PASS ---------------")
                        return True

	def cnt_get_packages_from_manifest_rhn(self, manifest_file, channel, version = None):
		# get all packages from manifest which need testing
		tag_path = "/"
		release = "None"
		tagname = "packagename"

		pkg_list = parse_manifest_xml().get_packagename(manifest_file, tag_path, channel, release, tagname)

		plist = []
		src_plist = []
		if version == None:
			for pkg in pkg_list:
				pkgname_list = pkg.split(" ")
				if "src" in pkg[3]:
					src_plist.append("%s-%s-%s.%s" % (pkgname_list[0], pkgname_list[1], pkgname_list[2], pkgname_list[3]))
				else:
					plist.append(pkgname_list[0])
			plist = set(plist)
			return src_plist, plist

		else:
			for pkg in pkg_list:
				pkgname_list = pkg.split(" ")
				pkgname = pkgname_list[0]
				pkgversion = pkgname_list[1]
				pkgrelease = pkgname_list[2]
				pkgarch = pkgname_list[3]
				if "src" in pkgarch:
					src_plist.append("%s-%s-%s.%s" % (pkgname, pkgversion, pkgrelease, pkgarch))
				else:
					plist.append("%s-%s-%s.%s" % (pkgname, pkgversion, pkgrelease, pkgarch))
			return src_plist, plist

	def cnt_package_consistency_rhn(self, session, manifest_file, channel):

		logging.info("--------------- Begin to verify package consistency for channel %s  ---------------" % channel)

		fstr = "%{name}-%{ver}-%{rel}.%{arch}"
		cmd = "repoquery --plugins --qf=%s -a --show-dupes --repoid=%s"% (fstr, channel)
		(ret, output) = self.runcmd(session, cmd, "get all binary packages from rhn-channel with command repoquery")
		binary_pkgs_rhn = output.splitlines()

		# There are source rpms in channels, but they can only be downloaded through the customer portal web site.  They aren't exposed to yum/yumdownloader/repoquery.
		# RHN APIs that can be used to query the source packages available, but the APIs are only available to RHN admins. So, let's not worry about SRPMs for now.
		# src_pkgs_rhn = ??
		# pkgs_rhn = binary_pkgs_rhn # + src_pkgs_rhn

		# get all packages from manifest which are needed testing
		src_pkgs_manifest, binary_pkgs_manifest = self.cnt_get_packages_from_manifest_rhn(manifest_file, channel, 'version')

                list1 = self.cnt_cmp_arrays(binary_pkgs_manifest, binary_pkgs_rhn)

                if len(list1) > 0:
                        logging.error("The package consistency test for the channel '%s' FAILED" % channel)

                        logging.info('Below are packages listed in expected package manifest but not in rhn-channel:')
                        self.cnt_print_list(list1)
                        logging.error("--------------- End to verify package consistency for channel %s : FAIL ---------------" % channel)
                        return False
                else:
                        logging.info("All Expected channels exist in test list!")
                        logging.info("--------------- End to verify package consistency for channel %s : PASS ---------------" % channel)
                        return True

	def cnt_rhn_installation_rhn(self, session, manifest_file, channel):

		logging.info("--------------- Begin to verify packages full installation for channel %s ---------------" % channel)
		# get packages from manifest
		src_pkgs_manifest, binary_pkgs_manifest = self.cnt_get_packages_from_manifest_rhn(manifest_file, channel)

		# There are source rpms in channels, but they can only be downloaded through the customer portal web site.  They aren't exposed to yum/yumdownloader/repoquery.
		# RHN APIs that can be used to query the source packages available, but the APIs are only available to RHN admins. So, let's not worry about SRPMs for now.
		# download source rpms from the customer portal web site - ignored for now

		# yum install binary packages
		checkresult = True
		for pkg in binary_pkgs_manifest:
			cmd = "yum install -y %s" % pkg
			(ret, output) = self.runcmd(session, cmd, "yum install package %s" % pkg)

			if ret == 0:
			        if ("Complete!" in output) or ("Nothing to do" in output) or ("conflicts" in output):
			                logging.info(" It's successful to install package %s." % pkg)
			        else:
			                logging.error("Test Failed - Failed to install package %s of channel %s." % (pkg, channel))
			                checkresult = False
			else:
			        if ("conflicts" in output):
			                logging.info(" It's successful to install package %s." % pkg)
			        else:
			                logging.error("Test Failed - Failed to install package %s of channel %s." % (pkg, channel))
			                checkresult = False

                if checkresult:
                        logging.info("--------------- End to verify packages full installation for channel %s: PASS ---------------" % channel)
                else:
                        logging.error("--------------- End to verify packages full installation for channel %s: FAIL ---------------" % channel)

                return checkresult



        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #               ======= Function Classes ======
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        def cnt_generate_script_for_yum(self, session, pkg, output_file_path):
                # generate expect script for yum install

                cmd = '''echo '#!/usr/bin/expect
spawn yum install %s
expect \"Is this ok \" {send_user \"M\\r\" }
expect \"Is this ok \" {send \"N\\r\" }
expect \"Exiting on user Command\" {send \"exit\"}'>%s''' % (pkg, output_file_path)

                (ret, output) = self.runcmd(session, cmd, "generating shell script of dependence verification")

                if (ret == 0):
                        logging.info("It's successful to generate expect script file :%s" % output_file_path)
                        return True
                else:
                        logging.error("Test Failed - Failed to verify package dependence for %s" % pkg)
                        return False

class parse_manifest_xml:
        def __getNextElement(self, ele, tagvalue):
                # get next element instance
                ele_child_list = list(ele)
                for i in ele_child_list:
                        vl = i.get('value')
                        if vl == tagvalue:
                                return i

        def __findLastEle(self, tag_list, ele):
                # find the last element instance
                for n in tag_list:
                        ele = self.__getNextElement(ele, n)
                return ele

        def __get_leaf_tags_lists(self, cur_ele, tags_list):
                # get all leaf tags content, return content list
                total_list = []
                for t in tags_list:
                        sublist = []
                        for m in list(cur_ele):
                                if m.tag == t:
                                        sublist.append(m.text)
                        total_list.append(sublist)
                return total_list

        def __get_leaf_tag_list(self, cur_ele, tagname):
                # get one leaf tag content, return content list
                taglist = []
                for m in list(cur_ele):
                        if m.tag == tagname:
                                for aa in m.text.strip().splitlines():
                                        taglist.append(aa.strip())
                return taglist

        def get_allleafs(self, xmlfile, tag_path, get_tag_list):
                # get all leaf tags text list
		try:
                	doc = ElementTree.parse(xmlfile)
                	root_ele = doc.getroot()
                	tag_list = tag_path.split('/')[1:]

                	# get the last tag element in tag path
			if tag_list[0] == '' or tag_list[0] == 'rhel':
                                cur_ele = root_ele
                        else:
	                	cur_ele = self.__findLastEle(tag_list, root_ele)

                	result_list = self.__get_leaf_tags_lists(cur_ele, get_tag_list)
		except:
			logging.warning("Except in parse_manifest_xml::get_allleafs")
                        result_list = 'ERROR'
                return result_list

        def get_oneleaf(self, xmlfile, tag_path, tagname):
		try:
	                doc = ElementTree.parse(xmlfile)
	                root_ele = doc.getroot()
	                tag_list = tag_path.split('/')[1:]

			if tag_list[0] == '' or tag_list[0] == 'rhel':
				cur_ele = root_ele
			else:
		                cur_ele = self.__findLastEle(tag_list, root_ele)

	                result_list = self.__get_leaf_tag_list(cur_ele, tagname)
		except:
			logging.warning("Except in parse_manifest_xml::get_oneleaf")
                        result_list = 'ERROR'
                return result_list

        def get_repoidElement(self, xmlfile, tag_path):
                #get repoid of release specified from manifest.xml
		try:
                	doc = ElementTree.parse(xmlfile)
                	ele = doc.getroot()

                	tag_list = tag_path.split('/')[1:]

                	for n in tag_list:
                	        ele = self.__getNextElement(ele, n)
               	except:
			logging.warning("Except in parse_manifest_xml::get_repoidElement")
			ele = 'ERROR'

		if ele == None:
			ele = 'ERROR'

                return ele

        def get_packagename(self, xmlfile, tag_path, repoid, release, tagname=None):
                tagname = 'packagename'
		cur_repoid = ''
		mlist = []
		try:
                	if release == "None":
				tag_path = os.path.join(tag_path, repoid)
                	        mlist = self.get_oneleaf(xmlfile, tag_path, tagname)
                	else:
                	        repoid_eles = self.get_repoidElement(xmlfile, tag_path)
	               	        for repoid_ele in repoid_eles:
	               	                if repoid_ele.get("releasever") == release and repoid_ele.get("value") == repoid:
                	                        cur_repoid = repoid_ele
						break
                	        mlist = self.__get_leaf_tag_list(cur_repoid, tagname)
		except:
			logging.warning("Except in parse_manifest_xml::get_packagename")
			mlist='ERROR'

                return mlist

        def get_relativeurl(self, xmlfile, tag_path, repoid, release, tagname=None):
                tagname = 'relativeurl'
		cur_repoid = ''
		mlist = []
		try:
                	if release == "None":
                	        tag_path += "/%s" % repoid
                	        mlist = self.get_oneleaf(xmlfile, tag_path, tagname)
                	else:
                	        repoid_eles = self.get_repoidElement(xmlfile, tag_path)
                	        for repoid_ele in repoid_eles:
                	                if repoid_ele.get("releasever") == release and repoid_ele.get("value") == repoid:
                	                        cur_repoid = repoid_ele
						break
                	        mlist = self.__get_leaf_tag_list(cur_repoid, tagname)
		except:
			logging.warning("Except in parse_manifest_xml::get_relativeurl")
                        mlist = 'ERROR'
                return mlist

	def get_arch_list(self, xmlfile, arch_father_path, cur_release):
		arch_list = self.get_element_list(xmlfile, arch_father_path)
		new_arch_list = []
		for arch in arch_list:
			repoid_father_path = arch_father_path + '/' + arch
			repo_list = self.get_repoidElement(xmlfile, repoid_father_path)
			release_list = []
			for repo in repo_list:
				release = repo.get("releasever")
				release_list.append(release)
			if cur_release in release_list:
				new_arch_list.append(arch)

		return new_arch_list

        def get_element_list(self, xmlfile, path):
                # get values from matched tag
            	try:
                	doc = ElementTree.parse(xmlfile)
                	root_ele = doc.getroot()
                	path_list = path.split('/')[1:]

			if path_list[0] == '' or path_list[0] == 'rhel':
				cur_ele = root_ele
			else:
	                	cur_ele = self.__findLastEle(path_list, root_ele)

			x = []
        		for i in list(cur_ele):
        		        x.append(i.get("value"))
		except:
			logging.warning("Except in parse_manifest_xml::get_element_list")
                        x = 'ERROR'
               	return x


class ListParser(SGMLParser):
    	def __init__(self):
        	SGMLParser.__init__(self)
		self.is_a = 0
		self.ret = []

    	def start_a(self, attrs):
        	for id,value in attrs:
			if id == 'href' and not ';' in value:
        			self.is_a = 1

    	def end_a(self):
        	self.is_a = 0

    	def handle_data(self, text):
        	if self.is_a == 1:
            		self.ret.append(text)

class DirParser(SGMLParser):
        def __init__(self):
                SGMLParser.__init__(self)
                self.is_a = 0
                self.ret = []

        def start_a(self, attrs):
                for id,value in attrs:
                        if id == 'href' and not ';' in value:
                                self.is_a = 1

        def end_a(self):
                self.is_a = 0

        def handle_data(self, text):
                if '/' in text and text.count('/') == 1:
                        self.ret.append(text)



class PackageParser(SGMLParser):
    	def __init__(self):
        	SGMLParser.__init__(self)
        	self.is_a = 0
        	self.obj = []

    	def start_a(self, attrs):
        	for id, value in attrs:
            		if id == 'href' and '.rpm' in value:
                		self.obj.append(value)
                		self.is_a = 1
    	def end_a(self):
        	self.is_a = 0
