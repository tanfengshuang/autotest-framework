import commands, sys

# NOTE: This script is only for binary and debug packages of rhel testing, can not be used for source packages which need to verify manually

'''Usage 1: python verify_level3_pkgs_for_rhel.py log_file_name '''

# You can run this script in the background with command: nohup python verify_level3_pkgs_for_rhel.py log_file_name &
# This script will generate file result.txt to record test log, you can use 'tail -f result.txt' to track log and status
# For the log_file_name: it should be the log file of *.INFO or *.DEBUG, please don't use *.ERROR log file

'''usage 2: python verify_level3_pkgs_for_rhel.py'''
# For usage 2, before run the command, please update all_failed_pkgs_by_repo first in line around 24 with the failed pkgs along with related repos


f = open('result.txt', 'w+')

params = len(sys.argv)

all_failed_pkgs_by_repo = {} # data model: {repo1:[pkg11,pkg12,...], repo2:[pkg21,pkg22,...]}
releasever_para = ""
baserepo = ""

if params == 1:
	all_failed_pkgs_by_repo = {'repo1': ['pkg11', 'pkg12'], 'repo2': ['pkg21', 'pkg22', 'pkg23']}
	command = "## command ##  python %s" % (sys.argv[0])
	f.write(command + '\n')

elif params == 2: 
	command = "## command ##  python %s %s" % (sys.argv[0], sys.argv[1])
        f.write(command + '\n')

	file_name = sys.argv[1]

	# Register and subscribe
	cmd = """cat %s | grep "subscription-manager register --username" | awk -F ': ' '{print $2}'""" % file_name
	ret, output1 = commands.getstatusoutput(cmd)
	
	ret, output2 = commands.getstatusoutput(output1)
	print output1
	print output2
	
	if ret == 0:
		print '======  Register successfully  ======\n'
	else: 
		print '======  Failed to register  ======\n'
		sys.exit(-1)

	cmd = """cat %s | grep "subscription-manager subscribe" | awk -F ': ' '{print $2}'""" % file_name
	ret, output = commands.getstatusoutput(cmd)
	
	cmds = output.splitlines()
	for cmd in cmds:
		ret, output = commands.getstatusoutput(cmd)
		print cmd
		print output
		
        	if ret == 0:
                	print '======  Subscribe successfully  ======\n'
		else:
			print '======  Failed to subscribe  ======\n'
			sys.exit(-1)

	# Yum clean all cache
	cmd = "yum clean all --enablerepo=*"
	ret, output = commands.getstatusoutput(cmd)
	print cmd
	#print output
	
	if ret == 0:
        	print '======  Yum clean all cache successfully  ======\n'
	else:
		print '======  Failed to yum clean all cache  ======\n'
		sys.exit(-1)

	# Disable all repos
	cmd = "subscription-manager repos --disable=*"
	ret, output = commands.getstatusoutput(cmd)
	print cmd
	#print output
	
        if ret == 0:
	        print '======  Disable all repos successfully  ======\n'
	else:
		print '======  Failed to disable all repos  ======\n'
		sys.exit(-1)

	# Enable base repo
	cmd = "cat %s | grep 'command of enable base repo' | awk -F ': ' '{print $2}'" % file_name
	ret, output1 = commands.getstatusoutput(cmd)
	
	ret, output2 = commands.getstatusoutput(output1)
	baserepo = output2
	print output1
	print output2
	
        if ret == 0:
	        print '======  Enable base repo successfully  ======\n'
	else:
		print '======  Failed to enable base repo  ======\n'
		sys.exit(-1)
	
	# Get all failed packages
	cmd = """cat %s | grep 'Test Failed - Failed to' | grep 'install package' | awk -F "'" '{print $2,$3}'""" % file_name
	ret, output = commands.getstatusoutput(cmd)
	
	all_failed_pkgs = list(output.strip().splitlines())
	f.write('\n' + "------ Get all failed packages from the testing log file ------" + '\n' + output + '\n')
	
	# Organize all failed pkgs by repos into the dict 'all_failed_pkgs_by_repo'
	for pkg_repo in all_failed_pkgs:
		pkg = pkg_repo.split("  of repo ")[0]
		repo= pkg_repo.split("  of repo ")[1][:-1]
		if not all_failed_pkgs_by_repo.has_key(repo): 
			all_failed_pkgs_by_repo[repo]=[pkg]
		else:
			all_failed_pkgs_by_repo[repo].append(pkg)

	# Get the value of testing para 'release_list'
	cmd = """cat %s | grep "release_list = "|awk -F ' = ' '{print $2}'""" % file_name
	ret, output = commands.getstatusoutput(cmd)
	
	if ret == 0:
		release_list = output.strip()
		if release_list != "":
			print "======  The value of testing para 'release_list' is: %s, so need to set '--releasever=%s' when install pkg  ======\n" % (release_list, release_list)
			releasever_para = " --releasever=%s" % release_list
		else:
			print "======  The testing para 'release_list' was not set  ======\n"

	else: 
		print "======  Failed to get the value of testing para 'release_list'  ======\n"
		sys.exit(-1)


# Start to install all failed packages one by one
for repo in all_failed_pkgs_by_repo.keys():

	print "++++++  Begin to install packages for the repo '%s'  ++++++\n" % repo

	# Enable test repo
	cmd = "subscription-manager repos --enable=%s" % repo
	ret, output = commands.getstatusoutput(cmd)
	print cmd
	print output
	
        if ret == 0:
	        print '======  Enable test repo successfully: %s  ======\n' % repo
	else:
		print '======  Failed to enable test repo, skip the installation of the pkgs in this repo: %s  ======\n' % repo
		continue
	
	# Install the packages one by one
	for pkg in all_failed_pkgs_by_repo[repo]:
		        
		f.write("\n")
		f.write("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

		cmd = "yum install -y %s%s" % (pkg, releasever_para)
	        f.write(cmd + "\n")
	        ret, output = commands.getstatusoutput(cmd)
	        f.write(output)
	        f.write("\n")
		if (ret == 0) and (("Complete!" in output) or ("Nothing to do" in output) or ("conflicts with" in output)):
			print " * It's successful to install package %s.\n" % pkg
	                f.write("\n * It's successful to install package %s.\n" % pkg)
	        else:
	                print " * Test Failed - Failed to install package %s.\n" % pkg
	                f.write("\n * Test Failed - Failed to install package %s.\n" % pkg)

	# Disable test repo but not disable base repo - (*)
	if not repo in baserepo:
	
		cmd = "subscription-manager repos --disable=%s" % repo
		ret, output = commands.getstatusoutput(cmd)
		print cmd
		print output
		
		if ret == 0:
			print '======  Disable test repo successfully: %s  ======\n' % repo
		else:
			print '======  Failed to disable test repo: %s  ======\n' % repo
			continue
	else:
		print '======  This test repo is baserepo skip to disable it: %s  ======\n' % repo

	print "++++++  Finish to install packages successfully for the repo '%s'  ++++++\n" % repo

f.close()


