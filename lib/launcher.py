#
#

import os, commands, logging, sys, re, time
import utils, dict_handler


def _launch_autotest(control='control', dryrun=False, verbose=True):
    """
    Lauch autotest client with default control file.
    FIXME: control name passing
    """
    logging.info('Launching autotest...')
    autotest_bin_d = os.path.join(os.getcwd(),'kvm-test/bin/autotest')
    control_path = os.path.join(os.getcwd(), 'kvm-test/tests/kvm/')
    control = os.path.join(control_path, control)
    kvm_config = os.path.join(control_path, "kvm_config.py")
    state = control + '.state'

    if dryrun:
        os.system("%s | grep shortname" %kvm_config)
    else:
        os.system('rm -rf %s' % state)
        start_cmd = "%s %s" % (autotest_bin_d, control)
        if verbose:
            start_cmd += " --verbose"
        os.system(start_cmd)


def run_loop(dict):
    # Big Loop Fixup
    fixup ="""
"""
    max_cpu, max_mem = utils.get_host_capability()

    dict_loop = {}

    category = dict.get('category')

    if category != 'all':
        try:
            lines = file("desc/%s.desc" % category).readlines()
        except:
            print "Warning: Could not found corresponding desc file!"
            sys.exit(-1)

        f = ''.join(lines)
        f = f.replace("{max_mem}", str(max_mem))
        fixup += f.replace("{max_cpu}", str(max_cpu))

        # Judge whether loop for memory & cpu. By default, single = yes
        if dict.get('single') == 'yes':
            print 'Single loop (without cpu and memory increment)'
            if category == "function_all":
                if max_mem >= 8192 and max_cpu >= 4:
                    fixup += """
variants:
    - smp4.8192m:
        smp = 4
        mem = 8192
"""
                else:
                    fixup += """
variants:
    - smp2.4096m:
        smp = 2
        mem = 4096
"""
                fixup += """
    - smp1.2048m:
        smp = 1
        mem = 2048
"""


        else:
            fixup += dict_handler.add_loop_variants('smp', 1,
                                                    max_cpu, multiplier=2)
            fixup += dict_handler.add_loop_variants('mem', 512,
                                                    max_mem, multiplier=4)

    if category not in ['acceptance_test','regression']:
        fixup += dict_handler.parse_params(dict, True)

    if category == 'acceptance_test' and dict.get('bridge') != None:
        fixup += "script = scripts/qemu-ifup-%s\n" % dict.get('bridge')

    # only use ide/rtl8139 to do the unattended installation for Windows guests
    if category == 'function_all':
        fixup += "unattended_install.cd:\n"
        fixup += "    Windows:\n"
        fixup += "        nic_model = rtl8139\n"
        fixup += "        drive_format = ide\n"

    if dict['snapshot'] == 'yes':
        fixup += 'extra_params += -snapshot\n'

    if dict['nrepeat']:
        fixup += dict_handler.gen_nrepeat_variants(int(dict.get('nrepeat')))

    if dict.get('clone') == 'no':
        fixup += 'no unattended_install.cd image_copy\n'
    else:
        fixup += 'image_copy|unattended_install.cd:\n'
        fixup += '    smp = 2\n'
        fixup += '    mem = 2048\n'
        fixup += '    only repeat1\n'
        fixup += '    iterations = 1\n'

    # Configure & launch test now
    # Do some preparations: verify kvm installation, directories setup etc.
    utils.common_prepare(dict)
    fixup = dict_handler.combine_fixup(dict, fixup)
    # Generate kvm_tests.cfg under test.bindir and add 'fixup' to the end
    dict_handler.build_config_file(fixup)

    _launch_autotest(dryrun=dict.get("dryrun") == "yes",
                     verbose=dict.get("verbose") == "yes")


def run_customized_autotest(tree, cmd, branch='master'):
    if not tree:
        logging.error("Illegal tree: %s" % tree)
        sys.exit(1)

    git_cmd = "wget http://kernel.org/pub/software/scm/git/git-1.7.3.3.tar.bz2"\
              " && tar xvfj git-1.7.3.3.tar.bz2 " \
              " && cd git-1.7.3.3 " \
              " && ./configure && make && make install"
    s, o = commands.getstatusoutput("git --help")
    if s != 0:
        logging.info("Installing Git ...")
        commands.getstatusoutput(git_cmd)
    s, o = commands.getstatusoutput("git --help")
    if s != 0:
        logging.error("Failed to install git")
        sys.exit(1)

    result_dir = "/usr/local/staf/test/RHEV/kvm-new/autotest/client/results"

    logging.info("Probing the virtlab mount point ...")
    mounts_fd = file("/proc/mounts")
    mounts = mounts_fd.read()
    mounts_fd.close()
    logging.info("Virtlab nfs dir %s" % mounts)

    #FIXME: result_dir is not mounted at all
    virtlab_nfs_dir = re.findall("(.*)\s+%s" % result_dir, mounts, re.M)[0]

    logging.info("Umount the result dir ...")
    s, o = commands.getstatusoutput("umount %s" % result_dir)
    if s != 0:
        logging.error("Could not umount %s:%s" % (result_dir, o))
        sys.exit(1)

    logging.info("Removing the original tree address")
    s, o = commands.getstatusoutput("rm -rf autotest")
    if s != 0:
        logging.error("Could not remove the tree %s" % o)
        sys.exit(1)


    logging.info("Cloning tree: git clone %s" % tree)
    s, o = commands.getstatusoutput("git clone %s autotest" % tree)
    if s != 0:
        logging.error("Could not finish the cloning:%s" % o)
        sys.exit(1)

    logging.info("Checking out branch %s..." % branch)
    s, o = commands.getstatusoutput("(cd autotest && "
                                    "git checkout --track -b %s ;"
                                    "git checkout %s)" % \
                                    (branch, branch))
    if s != 0:
        logging.error("Failed to check out branch '%s'" % branch)
        sys.exit(1)
    if "Already" not in o:
        logging.error("Still not on branch '%s', Aborting..." % branch)
        sys.exit(1)


    result_dir = os.path.join(os.getcwd(), 'autotest/client/results')
    logging.info("Create result directory: %s" % result_dir)
    s, o = commands.getstatusoutput("mkdir -p %s" % result_dir)
    if s != 0:
        logging.error("Could not create directory")
        sys.exit(1)

    logging.info("Remount the virtlab dir")
    s, o = commands.getstatusoutput("mount %s %s" % \
                                    (virtlab_nfs_dir, result_dir))
    if s != 0:
        logging.error("Could not mount %s to %s: %s" % \
                      (virtlab_nfs_dir, result_dir, o))
        sys.exit(1)

    logging.info("Executing the command %s" % cmd)
    os.system(cmd)


def run_customized_launcher(launcher_tree=None, launcher_branch='master',
                            autotest_tree=None, autotest_branch='master',
                            cmd=None):
    if not launcher_tree:
        logging.error("Illegal tree: %s" % launcher_tree)
        sys.exit(1)

    git_cmd = "wget http://kernel.org/pub/software/scm/git/git-1.7.3.3.tar.bz2"\
              " && tar xvfj git-1.7.3.3.tar.bz2 " \
              " && cd git-1.7.3.3 " \
              " && ./configure && make && make install"
    s, o = commands.getstatusoutput("git --help")
    if s != 0:
        logging.info("Installing Git ...")
        commands.getstatusoutput(git_cmd)
    s, o = commands.getstatusoutput("git --help")
    if s != 0:
        logging.error("Failed to install git")
        sys.exit(1)


    logging.info("Cloning tree: git clone %s" % launcher_tree)
    autotest_cli_local = "autotest-cli-%s" % str(time.time())
    s, o = commands.getstatusoutput("git clone %s %s" % \
                                    (launcher_tree, autotest_cli_local))
    if s != 0:
        logging.error("Could not finish the cloning:%s" % o)
        sys.exit(1)

    logging.info("Checking out branch %s..." % launcher_branch)
    s, o = commands.getstatusoutput("(cd %s && "
                                    "git checkout --track -b %s ; "
                                    "git checkout %s)" % \
                                    (autotest_cli_local,
                                     launcher_branch, launcher_branch))
    if s != 0:
        logging.error("Failed to check out branch '%s'" % launcher_branch)
        sys.exit(1)
    if "Already" not in o:
        logging.error("Still not on branch '%s', Abort." % launcher_branch)
        sys.exit(1)

    logging.info("Launch customized launcher...")
    #os.system(cmd)
    # cd autotest-cli && python configured_suite.py \
    # --launch_agent=alt-autotest --cmd=%s
    os.symlink('autotest/client', '%s/kvm-test' % autotest_cli_local)
    os.chdir(autotest_cli_local)
    run_customized_autotest(autotest_tree, cmd, autotest_branch)


