
import os, sys, socket, commands, re, math
import wrapper, logging, env_setup

def ip_fixup(dict):
    """ fixup src/dst host parameter in dictionary """

    def get_hostname_twin(hostname):
        """ get the twin machine ip address """
        postfix = ".englab.nay.redhat.com"
        if not postfix in hostname:
            return
        twin = hostname[:-23]
        index = int(len(twin))
        host_index = int(hostname[index])
        if host_index % 2 == 0:
            twin += '%s' % str(host_index - 1)
        else:
            twin += '%s' % str(host_index + 1)
        twin += postfix
        return twin

    def resolve_ip(hostname):
        """ get the ip address of hostname """
        try:
            ip = socket.gethostbyname("%s.englab.nay.redhat.com" % hostname)
        except IndexError:
            return None
        return ip

    def get_bridge_ip(bridge):
        try:
            #ip = os.popen("ifconfig %s" % bridge).readlines()[1].split()[1.5:]
            cmd = "ifconfig %s|awk 'NR==2 {print $2}'|awk -F: '{print $2}'"
            ip = commands.getoutput(cmd % bridge)
        except IndexError:
            return None
        return ip

    # dynamic generated mac address prefix
    line = os.popen("ip addr show eth0 |awk 'NR==2 {print $2}'").read().strip()

    if dict.get("ipfix") == "no":
        return dict

    dict['srchost'] = get_bridge_ip(dict.get("bridge"))
    try:
        # get hostname
        hostname = socket.gethostbyaddr(dict['srchost'])[0]
        # get the twin name
        dsthost = get_hostname_twin(hostname)
        if dsthost != None:
            # get the twin ip
            dict['dsthost'] = socket.gethostbyname(dsthost)
    except:
        pass
    return dict

def common_prepare(dict):
    """ Common preparating routine
    """
    env_dict = env_setup.config_parser(dict)

    # verify the kvm installation
    env_setup.kvm_verify(env_dict)

    # launch ksm
    env_setup.launch_ksm(env_dict)

    # setup directories and links for autotest
    env_setup.directory_setup(env_dict)

    # shutdown iptables in host
    env_setup.stop_iptables()

    # prepare qemu-ifup script
    env_setup.bridge_setup(env_dict)

    # install brewkoji
    env_setup.brewkoji_install()

    # modprobe the vhost module
    os.system("modprobe vhost_net")

    # setup remote machine environment
    # env_setup.remote_machine_setup(env_dict)

def env_passthrough(dict):
    # pass_through key/value to environment
    env_string = ""
    pass_keys = ["rhev","use_storage","nfs_storage","nfs_mntdir","nfs_localdir",
                 "dsthost","login_timeout"]
    for key in pass_keys:
        if dict.get(key):
            env_string += "%s = %s\n" % (key,dict.get(key))
    if dict.get('rhev') == 'yes':
        env_string += "bridge=breth0\nbridge_name=breth0"
    return env_string

def virtlab_parse(dict, argv):
    if dict['virtlab'] != 'yes':
        return
    if not dict['user']:
        dict['user'] = os.environ.get('USER')
    if not dict['profile']:
        o = commands.getoutput("virtlab list_profiles")
        p = "\| (RHEL.*kvm\S*) *\| Success rate:"
        dict['profile'] = re.findall(p, o)[-1]

    cmd = [i for i in argv]
    for i in ['user', 'tree', 'tags', 'profile', 'virtlab']:
        for j in argv:
            if i in j:
                cmd.remove(j)

    content = """<?xml version="1.0" encoding="UTF-8"?>
<virtlab>
<job name="%s-%s-%s-%s-%s-%s" product="RHEV" component="kvm-new"
 need_reboot="True" need_reinstall="True" need_multiple_machine="False">
""" % (dict['guestname'], dict['driveformat'], dict['nicmodel'],
       dict['imageformat'], dict['category'], dict['profile'])
    content += "<profile>%s</profile>\n" % dict['profile']
    content += "<tags>%s</tags>\n" % dict['tags']
    content += """<case name="CustomizedTree">
<parameter name="cmd">python %s</parameter>
<parameter name="tree">%s</parameter>
</case>
</job>
</virtlab>
""" % (' '.join(cmd), dict['tree'])

    f = file("/tmp/virtlab.xml", 'w')
    f.write(content)
    f.close()
    cmd = "virtlab add_job -u %s -f /tmp/virtlab.xml" % dict['user']
    print ''.join(re.findall("Create Job (\d+).", commands.getoutput(cmd)))
    sys.exit()

def common_parameter_parse(dict, function_loop = False):
    fixup = ""
    # Guest Name resolution
    if dict['guestname'] != 'all':
        fixup += "only %s\n" % dict['guestname']
    # Guest Platform resolution
    if dict['platform'] != 'all':
        fixup += "only %s\n" % dict['platform']
    # Guest Drive format resolution
    if dict['driveformat'] != 'all':
        fixup += "only %s\n" % dict['driveformat']
    # Guest NIC model handling
    if dict['nicmodel'] != 'all':
        fixup += "only %s\n" % dict['nicmodel']
    # Image format handling
    if dict['imageformat'] != 'all':
        fixup += "only %s\n" % dict['imageformat']
    # Log style analyze
    if dict.get('logstyle') == 'autotest':
        fixup += "logstyle = autotest\n"
    # Network method judge
    if dict.get('network') == 'bridge':
        fixup += "network = bridge\n"
    if dict.get('dryrun') == 'yes':
        fixup += "dryrun = yes\n"
    if dict.get('use_telnet') == 'yes':
        fixup +="use_telnet = yes\n"
    # Display client
    if dict.get('display'):
        fixup += "display = %s\n" % dict.get('display')
    # Host type
    fixup += "hosttype = %s\n" % dict['hosttype']
    if dict.get('ipfix') == 'no':
        fixup += "ipfix = no\n"
    if dict.get('srchost') != '0.0.0.0':
        fixup += "srchost = %s\n" % dict.get('srchost')
    if dict.get('dsthost') != '0.0.0.0':
        fixup += "dsthost = %s\n" % dict.get('dsthost')
    if dict.get('kill_vm'):
        fixup += "kill_vm = %s\n" % dict.get('kill_vm')
    if dict.get('rhev') == 'yes':
        fixup += "bridge = breth0\n"
    elif dict.get('bridge'):
        fixup += "bridge = %s\n" % dict.get('bridge')
    if dict.get('use_storage'):
        fixup += "use_storage = %s\n" % dict.get("use_storage")
    if dict.get('mig_timeout'):
        fixup += "mig_timeout = %s\n" % dict.get("mig_timeout")
    if dict.get('login_timeout'):
        fixup += "login_timeout = %s\n" % dict.get("login_timeout")
    if dict.get('wait_augment_ratio'):
        fixup += "wait_augment_ratio = %s\n" % dict.get("wait_augment_ratio")
    if dict.get('install_timeout'):
        fixup += "install_timeout = %s\n" % dict.get("install_timeout")

    #Entitlement parameters
    if dict.get('pkg_sm'):
        fixup += "pkg_sm = %s\n" % dict.get("pkg_sm")
    if dict.get('testtype'):
        fixup += "testtype = %s\n" % dict.get("testtype")
    if dict.get('pkg_url'):
        fixup += "pkg_url = %s\n" % dict.get("pkg_url")
    if dict.get('hostname'):
        fixup += "hostname = %s\n" % dict.get("hostname")
    if dict.get('baseurl'):
        fixup += "baseurl = %s\n" % dict.get("baseurl")
    if dict.get('serverURL'):
        fixup += "serverURL = %s\n" % dict.get("serverURL")
    if dict.get('samhostname'):
        fixup += "samhostname = %s\n" % dict.get("samhostname")
    if dict.get('samhostip'):
        fixup += "samhostip = %s\n" % dict.get("samhostip")
    if dict.get('sambaseurl'):
        fixup += "sambaseurl = %s\n" % dict.get("sambaseurl")
    if dict.get('candlepinhostname'):
        fixup += "candlepinhostname = %s\n" % dict.get("candlepinhostname")
    if dict.get('candlepinhostip'):
        fixup += "candlepinhostip = %s\n" % dict.get("candlepinhostip")
    #if dict.get('repocacert'):
    #    fixup += "repocacert = %s\n" % dict.get("repocacert")
    if dict.get('content_level'):
        fixup += "content_level = %s\n" % dict.get("content_level")
	if "level3" in dict.get("content_level"):
		fixup += "image_size = 100G\n"
    if dict.get('relserver'):
        fixup += "relserver = %s\n" % dict.get("relserver")
    if dict.get('runcasein'):
        fixup += "runcasein = %s\n" % dict.get("runcasein")
	fixup += "only %s\n" % ('runcasein-'+dict['runcasein'])
    if dict.get('runcasein') and dict.get('runcasein')=="guest":
        fixup += "profilers = \"kvm_stat \" \n"

#    if dict.get('runcasefor') and dict.get('runcasefor') == "upgrade":
#        fixup += "only %s\n" % ('upgrade')
#    else:
#        fixup += "no %s\n" % ('upgrade')

    if dict.get('category'):
	fixup += "category = %s\n" % dict.get("category")
    if dict.get('sku'):
	fixup += "sku = %s\n" % dict.get("sku")
    if dict.get('package_mf_url'):
        fixup += "package_mf_url = %s\n" % dict.get("package_mf_url")
    if dict.get('manifest_url'):
        fixup += "manifest_url = %s\n" % dict.get("manifest_url")
    if dict.get('release_list'):
	fixup += "release_list = %s\n" % dict.get("release_list")
    if dict.get('blacklist'):
        fixup += "blacklist = %s\n" % dict.get("blacklist")

    #URL of image for Entitlement
    fixup += "unattended_install.url:\n"
    fixup += "    RHEL-Client-6.1.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.1_32_url")
    fixup += "    RHEL-Client-6.1.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.1_64_url")
    fixup += "    RHEL-Client-5.7.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.7_32_url")
    fixup += "    RHEL-Client-5.7.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.7_64_url")
    fixup += "    RHEL-Client-6.2.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.2_32_url")
    fixup += "    RHEL-Client-6.2.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.2_64_url")
    fixup += "    RHEL-Client-6.3.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.3_32_url")
    fixup += "    RHEL-Client-6.3.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.3_64_url")
    fixup += "    RHEL-Client-6.4.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.4_32_url")
    fixup += "    RHEL-Client-6.4.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.4_64_url")
    fixup += "    RHEL-Client-6.5.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.5_32_url")
    fixup += "    RHEL-Client-6.5.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.5_64_url")
    fixup += "    RHEL-Client-6.6.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.6_32_url")
    fixup += "    RHEL-Client-6.6.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.6_64_url")
    fixup += "    RHEL-Client-6.7.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.7_32_url")
    fixup += "    RHEL-Client-6.7.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-6.7_64_url")
    fixup += "    RHEL-Client-7.0.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-7.0_32_url")
    fixup += "    RHEL-Client-7.0.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-7.0_64_url")
    fixup += "    RHEL-Client-7.1.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-7.1_32_url")
    fixup += "    RHEL-Client-7.1.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-7.1_64_url")
    fixup += "    RHEL-Client-7.2.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-7.2_32_url")
    fixup += "    RHEL-Client-7.2.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-7.2_64_url")
    fixup += "    RHEL-Client-5.8.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.8_32_url")
    fixup += "    RHEL-Client-5.8.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.8_64_url")
    fixup += "    RHEL-Client-5.9.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.9_32_url")
    fixup += "    RHEL-Client-5.9.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.9_64_url")
    fixup += "    RHEL-Client-5.10.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.10_32_url")
    fixup += "    RHEL-Client-5.10.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.10_64_url")
    fixup += "    RHEL-Client-5.11.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.11_32_url")
    fixup += "    RHEL-Client-5.11.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Client-5.11_64_url")
    fixup += "    RHEL-Server-6.1.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.1_32_url")
    fixup += "    RHEL-Server-6.1.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.1_64_url")
    fixup += "    RHEL-Server-5.7.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.7_32_url")
    fixup += "    RHEL-Server-5.7.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.7_64_url")
    fixup += "    RHEL-Server-6.2.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.2_32_url")
    fixup += "    RHEL-Server-6.2.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.2_64_url")
    fixup += "    RHEL-Server-6.3.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.3_32_url")
    fixup += "    RHEL-Server-6.3.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.3_64_url")
    fixup += "    RHEL-Server-6.4.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.4_32_url")
    fixup += "    RHEL-Server-6.4.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.4_64_url")
    fixup += "    RHEL-Server-6.5.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.5_32_url")
    fixup += "    RHEL-Server-6.5.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.5_64_url")
    fixup += "    RHEL-Server-6.6.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.6_32_url")
    fixup += "    RHEL-Server-6.6.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.6_64_url")
    fixup += "    RHEL-Server-6.7.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.7_32_url")
    fixup += "    RHEL-Server-6.7.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-6.7_64_url")
    fixup += "    RHEL-Server-7.0.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-7.0_32_url")
    fixup += "    RHEL-Server-7.0.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-7.0_64_url")
    fixup += "    RHEL-Server-7.1.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-7.1_32_url")
    fixup += "    RHEL-Server-7.1.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-7.1_64_url")
    fixup += "    RHEL-Server-7.2.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-7.2_32_url")
    fixup += "    RHEL-Server-7.2.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-7.2_64_url")
    fixup += "    RHEL-Server-5.8.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.8_32_url")
    fixup += "    RHEL-Server-5.8.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.8_64_url")
    fixup += "    RHEL-Server-5.9.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.9_32_url")
    fixup += "    RHEL-Server-5.9.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.9_64_url")
    fixup += "    RHEL-Server-5.10.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.10_32_url")
    fixup += "    RHEL-Server-5.10.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.10_64_url")
    fixup += "    RHEL-Server-5.11.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.11_32_url")
    fixup += "    RHEL-Server-5.11.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Server-5.11_64_url")
    fixup += "    RHEL-Workstation-5.7.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.7_32_url")
    fixup += "    RHEL-Workstation-5.7.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.7_64_url")
    fixup += "    RHEL-Workstation-6.1.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.1_32_url")
    fixup += "    RHEL-Workstation-6.1.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.1_64_url")
    fixup += "    RHEL-Workstation-6.2.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.2_32_url")
    fixup += "    RHEL-Workstation-6.2.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.2_64_url")
    fixup += "    RHEL-Workstation-6.3.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.3_32_url")
    fixup += "    RHEL-Workstation-6.3.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.3_64_url")
    fixup += "    RHEL-Workstation-6.4.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.4_32_url")
    fixup += "    RHEL-Workstation-6.4.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.4_64_url")
    fixup += "    RHEL-Workstation-6.5.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.5_32_url")
    fixup += "    RHEL-Workstation-6.5.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.5_64_url")
    fixup += "    RHEL-Workstation-6.6.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.6_32_url")
    fixup += "    RHEL-Workstation-6.6.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.6_64_url")
    fixup += "    RHEL-Workstation-6.7.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.7_32_url")
    fixup += "    RHEL-Workstation-6.7.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-6.7_64_url")
    fixup += "    RHEL-Workstation-7.0.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-7.0_32_url")
    fixup += "    RHEL-Workstation-7.0.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-7.0_64_url")
    fixup += "    RHEL-Workstation-7.1.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-7.1_32_url")
    fixup += "    RHEL-Workstation-7.1.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-7.1_64_url")
    fixup += "    RHEL-Workstation-7.2.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-7.2_32_url")
    fixup += "    RHEL-Workstation-7.2.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-7.2_64_url")
    fixup += "    RHEL-Workstation-5.8.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.8_32_url")
    fixup += "    RHEL-Workstation-5.8.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.8_64_url")
    fixup += "    RHEL-Workstation-5.9.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.9_32_url")
    fixup += "    RHEL-Workstation-5.9.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.9_64_url")
    fixup += "    RHEL-Workstation-5.10.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.10_32_url")
    fixup += "    RHEL-Workstation-5.10.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.10_64_url")
    fixup += "    RHEL-Workstation-5.11.32:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.11_32_url")
    fixup += "    RHEL-Workstation-5.11.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-Workstation-5.11_64_url")
    fixup += "    RHEL-ComputeNode-6.1.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-6.1_64_url")
    fixup += "    RHEL-ComputeNode-6.2.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-6.2_64_url")
    fixup += "    RHEL-ComputeNode-6.3.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-6.3_64_url")
    fixup += "    RHEL-ComputeNode-6.4.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-6.4_64_url")
    fixup += "    RHEL-ComputeNode-6.5.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-6.5_64_url")
    fixup += "    RHEL-ComputeNode-6.6.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-6.6_64_url")
    fixup += "    RHEL-ComputeNode-6.7.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-6.7_64_url")
    fixup += "    RHEL-ComputeNode-7.0.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-7.0_64_url")
    fixup += "    RHEL-ComputeNode-7.1.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-7.1_64_url")
    fixup += "    RHEL-ComputeNode-7.2.64:\n"
    fixup += "        url = %s\n" % dict.get("RHEL-ComputeNode-7.2_64_url")
    # for upgrade  
    # 5.9
    fixup += "RHEL-Server-5.9_64_url = %s\n" % dict.get("RHEL-Server-5.9_64_url")
    fixup += "RHEL-Server-5.9_32_url = %s\n" % dict.get("RHEL-Server-5.9_32_url")
    fixup += "RHEL-Client-5.9_64_url = %s\n" % dict.get("RHEL-Client-5.9_64_url")
    fixup += "RHEL-Client-5.9_32_url = %s\n" % dict.get("RHEL-Client-5.9_32_url")
    fixup += "RHEL-Workstation-5.9_64_url = %s\n" % dict.get("RHEL-Workstation-5.9_64_url")
    fixup += "RHEL-Workstation-5.9_32_url = %s\n" % dict.get("RHEL-Workstation-5.9_32_url")
    fixup += "RHEL-ComputeNode-5.9_64_url = %s\n" % dict.get("RHEL-ComputeNode-5.9_64_url")
    # 6.4
    fixup += "RHEL-Server-6.4_64_url = %s\n" % dict.get("RHEL-Server-6.4_64_url")
    fixup += "RHEL-Server-6.4_32_url = %s\n" % dict.get("RHEL-Server-6.4_32_url")
    fixup += "RHEL-Client-6.4_64_url = %s\n" % dict.get("RHEL-Client-6.4_64_url")
    fixup += "RHEL-Client-6.4_32_url = %s\n" % dict.get("RHEL-Client-6.4_32_url")
    fixup += "RHEL-Workstation-6.4_64_url = %s\n" % dict.get("RHEL-Workstation-6.4_64_url")
    fixup += "RHEL-Workstation-6.4_32_url = %s\n" % dict.get("RHEL-Workstation-6.4_32_url")
    fixup += "RHEL-ComputeNode-6.4_64_url = %s\n" % dict.get("RHEL-ComputeNode-6.4_64_url")


    if not function_loop:
        if dict.get('vcpu') == "Default":
            max_cpu = get_cpu_num()
            
            #Add this adjudgement just for running case in virtual machine which has just 1 cpu
            if max_cpu < 2:
            	max_cpu = 2
            	
            mid_cpu = int(math.pow(2, math.ceil(math.log(max_cpu / 2, 2))))
            if mid_cpu < 2:
                mid_cpu = 2
            fixup += "smp = %s\n" % mid_cpu
        else:
            fixup += "smp = %s\n" % dict.get('vcpu')
        if dict.get('vcpu_cores'):
            fixup += "vcpu_cores = %s\n" % dict.get('vcpu_cores')
        if dict.get('vcpu_threads'):
            fixup += "vcpu_threads = %s\n" % dict.get('vcpu_threads')
        if dict.get('vcpu_socket'):
            fixup += "vcpu_socket = %s\n" % dict.get('vcpu_socket')
        if dict.get('mem') == "Default":
            max_mem = get_mem_num()
            mem_g = max_mem / 1024
            mem_g = int(math.pow(2, math.ceil(math.log(mem_g / 2, 2))))
            mid_mem = mem_g * 1024
            fixup += "mem = %s\n" % mid_mem
        else:
            fixup += "mem = %s\n" % dict.get('mem')
    fixup += "exec:\n"
    fixup += "    mem = 1024\n"
    if dict.get('iterations'):
        fixup += "iterations = %s\n" % dict.get('iterations')

    if dict.get('hugepages') == 'yes':
        fixup += 'only hugepages\n'
    if not dict.get('hugepages') or dict.get('hugepages') == 'no':
        fixup += 'only smallpages\n'


    if dict.get('test_timeout') != None:
        fixup += "test_timeout = %s\n" % dict.get('test_timeout')
    if dict['snapshot'] == 'yes':
        fixup += 'extra_params += -snapshot\n'

    if not dict.get('deviceassign') or dict.get('deviceassign') == 'no':
        fixup += 'only virtual_device\n'
    elif dict.get('deviceassign') == 'yes':
        fixup += 'only assign_device\n'

    return fixup

def combine_fixup_string(dict, string,
                         base_config_filename = "virtlab_tests.cfg",
                         config_filename= "tests.cfg"):
    """
    Combine the fixup string, the pameters which is changed in prepare process
    can also be added.
    """
    fixup_top = ""
    fixup_bottom = ""
    if dict.get('bridge') != None:
        fixup_top += "nic_script = scripts/qemu-ifup-%s\n" % dict.get('bridge')
    fixup_top += "include %s\ninclude cdkeys.cfg\n" % base_config_filename

    if dict.get("iscsi_dev") != None:
        fixup_bottom += "iscsi_dev = %s\n" % dict.get('iscsi_dev')
    if dict.get("iscsi_number") != None:
        fixup_bottom += "iscsi_number = %s\n" % dict.get('iscsi_number')

    return fixup_top + string + fixup_bottom

def get_cpu_num():
    """ get cpu number of host machine """
    cmd = "cat /proc/cpuinfo | grep processor | wc -l"
    ncpu= int(os.popen(cmd).readlines()[0].strip())
    print "number of cpus got: %d" % ncpu
    return ncpu

def get_mem_num():
    """ get the memory number of host machine """
    nmem = 0
    mems = os.popen("dmidecode -t 17").read()
    mems = mems.split("Memory Device")
    for block in mems:
        tmp = re.findall("Size: (\d+).*Form Factor: (.*?[DRS]IMM)", block, re.S)
        if tmp:
            mem_size, mem_type = tmp[0]
            if (("DIMM" in mem_type) or ("SIMM" in mem_type) \
                    or ("RIMM" in mem_type)) and mem_size.isdigit():
                nmem += int(mem_size)
    print "number of memories got: %d" % nmem
    return nmem

def get_host_capability():
    max_vcpu = get_cpu_num()
    max_mem = get_mem_num()
    if max_vcpu > 16:
        max_vcpu = 16
    return max_vcpu, max_mem


def build_config_file(config_string, config_filename= "tests.cfg"):
    """
    Use str to generate the test configuration file on the fly base on the base
    config file.
    @config_string: String contains the configurations.
    @config_filename: Filename of the generated configuration file.
    """
    kvm_dir = os.path.join(os.getcwd(), 'kvm-test/tests/kvm')
    kvm_tests = os.path.join(kvm_dir, config_filename)
    try:
        file = open(kvm_tests, 'w')
    except IOError:
        print "Failed to create config file kvm_tests.cfg"
        sys.exit(1)
    file.write(config_string)
    file.close()

def add_loop_variants(name, start, end, multiplier=2, indent=''):
    """
    Add a variants with level 1 for loop testing. It will write to
    kvm_tests.cfg something like this:

        variants:
        - smp1:
            smp = 1
        - smp2:
            smp = 2 (1 * 2)
        - smp4:
            smp = 4 (2 * 2)
        ...

    It will loop from start * multiplier to end. So it is:
    value = start * multiplier

    @name: key name added to kvm_tests.cfg
    @start: start number for value in dict
    @end:   end number for value
    @multiplier: multiplier for multiply with start
    """
    str = indent + 'variants:' + '\n'

    def add_one_loop(key, value, indent):
        string = indent + '    - %s%d:\n' % (key, value)
        string += indent + '        %s = %d\n' % (key, value)
        return string

    while start <= end:
        str += add_one_loop(name, start, indent)
        start *= multiplier

    str += '\n'
    return str

def gen_nrepeat_variants(count):
    """
    Simply add a variants with counted section and without defining
    any parameters.
    """
    str = 'variants:' + '\n'
    nr = 1
    while nr <= count:
        str += '    - repeat%d:\n' % nr
        nr += 1
    return str

def start(string, dict):
    """
    This helper function mainly does:
    1) generate kvm_tests.cfg under test.bindir and add $string to the end
    2) do some preparations like verify kvm installation, directories setup etc
    """
    # Do some preparations: verify kvm installation, directories setup etc.
    if dict.get('runcasein') and dict.get('runcasein')=="guest":
        common_prepare(dict)
    string = combine_fixup_string(dict, string)
    # Generate kvm_tests.cfg under test.bindir and add 'fixup' to the end
    build_config_file(string)
    wrapper.launch_autotest_control(dryrun = dict.get("dryrun") == "yes",
                                    verbose = dict.get("verbose") == "yes")


# for unit testing
if __name__ == "__main__":
    dict = {}
    dict['nfs_src']="10.66.71.224:/vol/kvm1/auto/iso"
    common_prepare(dict)
