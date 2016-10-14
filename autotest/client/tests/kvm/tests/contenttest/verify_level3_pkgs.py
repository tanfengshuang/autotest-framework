import commands, sys

# This script is only for binary and debug packages, not including source packages

#'''usage: python verify_level3_pkgs.py log_file_name '''
# please run in the background with command 'nohup python verify_level3_pkgs.py log_file_name &' 
# will generate file result.txt to record test log, can use 'tail -f result.txt' to track log
# log_file_name: *.INFO or *.DEBUG, please don't use *.ERROR

#'''usage: python verify_level3_pkgs.py'''
# please update failed_pkgs first


f = open('result.txt', 'w+')

params = len(sys.argv)
all_failed_pkgs = []

if params == 1:
	failed_pkgs = "lam-devel,ldapjdk,libmudflap-devel,mkinitrd-devel,mod_perl-devel,pycairo-devel"
	all_failed_pkgs = failed_pkgs.split(',')
	command = "## command ##  python %s" % (sys.argv[0])
	f.write(command + '\n')

elif params == 2: 
	command = "## command ##  python %s %s" % (sys.argv[0], sys.argv[1])
        f.write(command + '\n')

	file_name = sys.argv[1]

	# Register and subscribe
	#cmd = '''cat %s | grep "subscription-manager register --username" | sed -e "s/^.\{37\}//"''' % file_name
	cmd = """cat %s | grep "subscription-manager register --username" | awk -F ': ' '{print $2}'""" % file_name
	ret, output = commands.getstatusoutput(cmd)
	print output
	ret, output = commands.getstatusoutput(output)
	if ret == 0:
		print '======  Register successfully...  ======'
	else: 
		print '======  Failed to register...  ======'

	#cmd = '''cat %s | grep "subscription-manager subscribe" | sed -e "s/^.\{38\}//"''' % file_name
	cmd = """cat %s | grep "subscription-manager subscribe" | awk -F ': ' '{print $2}'""" % file_name
	ret, output = commands.getstatusoutput(cmd)
	cmds = output.splitlines()
	for cmd in cmds:
		print cmd
		ret, output = commands.getstatusoutput(cmd)
        	if ret == 0:
                	print '======  Subscribe successfully...  ======'
		else:
			print '======  Failed to subscribe...  ======'

	cmd = "yum clean all"
	ret, output = commands.getstatusoutput(cmd)

	#cmd = """cat %s | grep "for(" | sed -e "s/^.\{38\}//" | awk -F "redhat.repo:" '{print $2}'""" % file_name
	cmd = "cat %s | grep 'subscription-manager repos --enable' | awk -F ': ' '{print $2}'" % file_name
	ret, output = commands.getstatusoutput(cmd)
	cmds = output.splitlines()
	for cmd in cmds:
		print output
		ret, output = commands.getstatusoutput(cmd)
	        if ret == 0:
        	        print '======  enable repo successfully: %s  ======' % cmd

	cmd = "cat %s | grep 'subscription-manager repos --disable' | awk -F ': ' '{print $2}'" % file_name
        ret, output = commands.getstatusoutput(cmd)
        cmds = output.splitlines()
        for cmd in cmds:
                print output
                ret, output = commands.getstatusoutput(cmd)
                if ret == 0:
                        print '======  disable repo successfully: %s  ======' % cmd
		
	# get packages failed to install
	#cmd = '''cat %s | grep 'Test Failed - Failed to' | grep 'install package' | sed -e 's/\[.*\]//' -e "s/^.\{80\}//" -e "s/' of.*$//"''' % file_name
	cmd = """cat %s | grep 'Test Failed - Failed to' | grep 'install package' | awk -F "'" '{print $2}'""" % file_name
	ret, output = commands.getstatusoutput(cmd)
	debug_binary_pkgs = list(output.strip().splitlines())
	f.write('\n' + "------ get packages failed to install ------" + '\n' + output)
	
	# get packages failed to download
	#cmd = '''cat %s | grep 'Test Failed - Failed to download package' | sed -e "s/^.\{80\}//" -e "s/'.//"''' % file_name
	#ret, output = commands.getstatusoutput(cmd)
	#source_pkgs = list(output.strip().splitlines())
	#f.write('\n' + '\n' + "------ get packages failed to download ------" + '\n' + output)
	
	#all_failed_pkgs = list(set(debug_binary_pkgs) | set(source_pkgs))
	all_failed_pkgs = debug_binary_pkgs
	#print all_failed_pkgs


for pkg in all_failed_pkgs:
                
	f.write("\n")
        f.write("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

        if 'src' in pkg or 'source' in pkg:
		# download source packages
        	cmd = "yumdownloader --source %s" % pkg
                f.write(cmd + "\n")
                ret, output = commands.getstatusoutput(cmd)
                f.write(output)
                f.write("\n")
	else:
		# install binary and debug packages
		cmd = "yum install -y --skip-broken %s" % pkg
                f.write(cmd + "\n")
                ret, output = commands.getstatusoutput(cmd)
                f.write(output)
                f.write("\n")
		if (ret == 0) and (("Complete!" in output) or ("Nothing to do" in output) or ("conflicts with" in output)):
			print "\n * It's successful to install package %s." % pkg
                        f.write("\n * It's successful to install package %s.\n" % pkg)
                else:
                        print "\n * Test Failed - Failed to install package %s." % pkg
                        f.write("\n * Test Failed - Failed to install package %s.\n" % pkg)

f.close( )


