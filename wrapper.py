##@ Summary: Common STAF warrper of autotest client
##@ Description: 1) default parameters 2) argv analyzer 3) autotest client initiater
##@ Maintainer: Jason Wang <jasowang@redhat.com>
##@ Update:     NOW
##@ Version:    1

import os, sys, getopt, shelve
import logging, common

dict_template = {
'cmd_reboot':		'shutdown -r now',
'cmd_shutdown': 	'shutdown -h now',
'depend':		'[]',
'display':		'vnc',
'fail_if_stuck_for':	'300',
'force_create_image':	'no',
'use_storage':		'local',
'guest_port_ssh':	'22',
'image_format': 	'raw',
'image_name' :		'images/RHEL-Server-5.3-64',
'image_size': 		'10G',
'images':		'image1',
'keep_ppm_files': 	'no',
'keep_ppm_files_on_error': 'no',
'kill_vm_gracefully':	'yes',
'kill_vm_timeout':	'60',
'kill_vm_timeout_on_error':	'0',
'mac_prefix':		'00:11:22:33:44:',
'main_vm':		'vm1',
'md5sum':		'c5ed6b284410f4d8212cafc78fd7a8c5',
'md5sum_1m':		'b999f437583098ea5bbd56fb1de1d011',
'mem':			'1024',
'name':			'rhel53_server-install',
'network':		'user',
'nic_model':		'e1000',
'nics':			'nic1',
'bridge_nic2':          'virbr0',
'password':		'123456',
'redirs': 		'ssh',
'shortname':		'standalone_example',
'ssh_port':		'22',
'ssh_prompt':		'\[root@.{0,50}][\#\$]',
'start_vm':		'yes',
'steps': 		'RHEL-Server-5.3-64.steps',
'type': 		'jumbo',
'username': 		'root',
'dst_vm':		'vm2',
'vms': 			'vm1',
'image_snapshot':       'no',
'image_snapshot_vm2':	'yes',
'ksm_size':		None,
'extra_params':	        ' -usbdevice tablet -no-hpet',
'bridge':		'switch',
'bridge_names':         'switch virbr0 breth0',
'cdrom':                '',
'vlan_mode':            'default',
'guest_type':           'rhel_server_60_64',
'srchost':              '0.0.0.0',
'dsthost':              '0.0.0.0',
'floppy_image':         None,
'host_passwd':          'redhat',
'migration_test_command' : None,
'serial_file':          None,
'serial_dev':           None,
'remote_host':          None,
'remote_login':         None,
'storage_dir':          None,
'bus_id':               None,
'format_list':          None,
'size':                 None,
'if_type':              None,
'vlan_id':              None,
'vcpu':                 'Default',
'app':                  None,
'test_name':            None,
'test_control_file':    'control',
'test_timeout':         None,
'nfs_storage':          '10.66.71.226',
'nfs_mntdir':           '/vol/kvm1/auto/nfs_storage',
'nfs_localdir':         '/tmp/kvm_autotest_root/images',
'LogVol_name':          None,
'vmlinuz':              None,
'kill_vm_on_error':     'no',
'nic_list':             None,
'initrd':               None,
'migration_src':        None,
'hostpasswd':           'redhat',
'reboot':               None,
'npages':               None,
'sleep':                None,
'ssh_status_test_command': 'echo $?',
'ksm':                    '0',
'guestname':             'RHEL-Server-6.0',
'platform':               '64',
'hosttype':              'small',
'driveformat':           'ide',
'nicmodel':              'rtl8139',
'dependency':            'none',
'snapshot':              'no',
'category':              'function_all',
'imageformat':           'raw',
'testcase':              'boot',
'nrepeat':               1,
'iterations':            1,
'clone':                 'yes',
'logstyle':              'virtlab',
'dryrun':                'no',
'ipfix':                 'yes',
'ins':                   1,
'use_telnet':            'no',
'rhev':                  'no',
'use_storage':           'local',
'mig_timeout':           600,
'img_clean':             'no',
'stress':                'autotest.stress',
'login_timeout':          1200,
'install_timeout':        130,
'wait_augment_ratio':     1,
'hugepage':              'no',
'loop_type':             'fixed',
"versions":               'kvm-83-142.el5',
"verbose":               'no',
"supercmd":              'none',
'virtlab':               'no',
'tags':                  'VT,KVM_TEST',
'tree':                  'git://10.66.82.200/autotest',
'profile':               '',
'user':                  '',
'vcpu_cores':            '',
'vcpu_threads':          '1',
'vcpu_sockets':          '2',
'iscsi_server':          '10.66.90.100',
'iscsi_initiator':       'iqn.2010-07.com.redhat:kvmautotest',
'iscsi_keyword':         'kvm',
'iscsi_dev':             '',
'iscsi_number':          '',
'hugepages':             'no',
'deviceassign':          'no',
"RHEL-Client-6.2_32_url":'',
"RHEL-Client-6.2_64_url":'',
"RHEL-Client-6.3_32_url":'',
"RHEL-Client-6.3_64_url":'',
"RHEL-Client-6.4_32_url":'',
"RHEL-Client-6.4_64_url":'',
"RHEL-Client-6.5_32_url":'',
"RHEL-Client-6.5_64_url":'',
"RHEL-Client-6.6_32_url":'',
"RHEL-Client-6.6_64_url":'',
"RHEL-Client-6.7_32_url":'',
"RHEL-Client-6.7_64_url":'',
"RHEL-Client-7.0_32_url":'',
"RHEL-Client-7.0_64_url":'',
"RHEL-Client-7.1_32_url":'',
"RHEL-Client-7.1_64_url":'',
"RHEL-Client-7.2_32_url":'',
"RHEL-Client-7.2_64_url":'',
"RHEL-Client-5.8_32_url":'',
"RHEL-Client-5.8_64_url":'',
"RHEL-Client-5.9_32_url":'',
"RHEL-Client-5.9_64_url":'',
"RHEL-Client-5.10_32_url":'',
"RHEL-Client-5.10_64_url":'',
"RHEL-Client-5.11_32_url":'',
"RHEL-Client-5.11_64_url":'',
"RHEL-Server-6.2_32_url":'',
"RHEL-Server-6.2_64_url":'',
"RHEL-Server-6.3_32_url":'',
"RHEL-Server-6.3_64_url":'',
"RHEL-Server-6.4_32_url":'',
"RHEL-Server-6.4_64_url":'',
"RHEL-Server-6.5_32_url":'',
"RHEL-Server-6.5_64_url":'',
"RHEL-Server-6.6_32_url":'',
"RHEL-Server-6.6_64_url":'',
"RHEL-Server-6.7_32_url":'',
"RHEL-Server-6.7_64_url":'',
"RHEL-Server-7.0_32_url":'',
"RHEL-Server-7.0_64_url":'',
"RHEL-Server-7.1_32_url":'',
"RHEL-Server-7.1_64_url":'',
"RHEL-Server-7.2_32_url":'',
"RHEL-Server-7.2_64_url":'',
"RHEL-Server-5.8_32_url":'',
"RHEL-Server-5.8_64_url":'',
"RHEL-Server-5.9_32_url":'',
"RHEL-Server-5.9_64_url":'',
"RHEL-Server-5.10_32_url":'',
"RHEL-Server-5.10_64_url":'',
"RHEL-Server-5.11_32_url":'',
"RHEL-Server-5.11_64_url":'',
"RHEL-Server-6.1_32_url":'',
"RHEL-Server-6.1_64_url":'',
"RHEL-Client-6.1_32_url":'',
"RHEL-Client-6.1_64_url":'',
"RHEL-Workstation-6.1_32_url":'',
"RHEL-Workstation-6.1_64_url":'',
"RHEL-ComputeNode-6.1_64_url":'',
"RHEL-Server-5.7_32_url":'',
"RHEL-Server-5.7_64_url":'',
"RHEL-Client-5.7_32_url":'',
"RHEL-Client-5.7_64_url":'',
"RHEL-Workstation-5.7_32_url":'',
"RHEL-Workstation-5.7_64_url":'',
"RHEL-Workstation-6.2_32_url":'',
"RHEL-Workstation-6.2_64_url":'',
"RHEL-Workstation-6.3_32_url":'',
"RHEL-Workstation-6.3_64_url":'',
"RHEL-Workstation-6.4_32_url":'',
"RHEL-Workstation-6.4_64_url":'',
"RHEL-Workstation-6.5_32_url":'',
"RHEL-Workstation-6.5_64_url":'',
"RHEL-Workstation-6.6_32_url":'',
"RHEL-Workstation-6.6_64_url":'',
"RHEL-Workstation-6.7_32_url":'',
"RHEL-Workstation-6.7_64_url":'',
"RHEL-Workstation-7.0_32_url":'',
"RHEL-Workstation-7.0_64_url":'',
"RHEL-Workstation-7.1_32_url":'',
"RHEL-Workstation-7.1_64_url":'',
"RHEL-Workstation-7.2_32_url":'',
"RHEL-Workstation-7.2_64_url":'',
"RHEL-Workstation-5.8_32_url":'',
"RHEL-Workstation-5.8_64_url":'',
"RHEL-Workstation-5.9_32_url":'',
"RHEL-Workstation-5.9_64_url":'',
"RHEL-Workstation-5.10_32_url":'',
"RHEL-Workstation-5.10_64_url":'',
"RHEL-Workstation-5.11_32_url":'',
"RHEL-Workstation-5.11_64_url":'',
"RHEL-ComputeNode-6.2_64_url":'',
"RHEL-ComputeNode-6.3_64_url":'',
"RHEL-ComputeNode-6.4_64_url":'',
"RHEL-ComputeNode-6.5_64_url":'',
"RHEL-ComputeNode-6.6_64_url":'',
"RHEL-ComputeNode-6.7_64_url":'',
"RHEL-ComputeNode-7.0_64_url":'',
"RHEL-ComputeNode-7.1_64_url":'',
"RHEL-ComputeNode-7.2_64_url":'',
"pkg_sm":'',
"pkg_url":'',
"testtype":'',
"hostname":'',
"baseurl":'',
"serverURL":'',
"sku":'',
"samhostname":'',
"samhostip":'',
"sambaseurl":'',
"candlepinhostname":'',
"candlepinhostip":'',
"content_level":'',
"runcasein":'guest',
"runcasefor":'',
"package_mf_url":'',
"manifest_url":'',
"release_list":'',
"blacklist":'',
}


def do_dict_fixup(dict):
    """ get guest related information from dict_fixup
    """
    name = dict.get('guest_type')
    if not name:
        logging.error("lack of guest_type")
        return False
    fixup = dict_fixup[name]
    for key in fixup:
        if not key == 'cdrom':
            # do not fixup cdrom key by default
            dict[key] = fixup[key]


def do_fixup(dict, key):
    """ do dedicated key fixup
    """
    name = dict.get('guest_type')
    if not name:
        logging.error("lack of guest_type")
        return False
    fixup = dict_fixup[name]
    dict[key] = fixup[key]


def build_dict_from_argv(argv):
    """ Build opt string used for getopt() from string argv
        FIXME: make use of GetoptError!
    """
    dict = dict_template.copy()
    opt_string = []

    for key in dict.keys():
        opt_string.append(key + '=')

    try:
        opt_string, args = getopt.getopt(argv,'',opt_string)
    except getopt.GetoptError, err:
        print str(err)
        print "Please check available options"
        sys.exit(2)

    for item in opt_string:
        dict[item[0][2:]]=item[1]

    #do_dict_fixup(dict)

    if os.system("yum -h &> /dev/null"):
        dict['rhev'] = 'yes'
    else:
        dict['rhev'] = 'no'

    return common.ip_fixup(dict)

def launch_autotest_control(control='control', dryrun = False, verbose = False):
    """
    Lauch autotest client with default control file.
    FIXME: control name passing
    """
    autotest_bin_d = os.path.join(os.getcwd(),'kvm-test/bin/autotest')
    control_path = os.path.join(os.getcwd(), 'kvm-test/tests/kvm/')
    control = os.path.join(control_path, control)
    kvm_config = os.path.join(os.getcwd(),
                              "kvm-test/common_lib/cartesian_config.py")
    tests_config = os.path.join(control_path, "tests.cfg")
    state = control + '.state'

    if dryrun:
        os.system("%s %s" % (kvm_config, tests_config))
    else:
        os.system('rm -rf %s' % state)
        start_cmd = "%s %s" % (autotest_bin_d, control)
        if verbose:
            start_cmd += " --verbose"
        os.system(start_cmd)

def bigloop_fixup(str, dict=None, env_dict=None):
    """  Write special requirement to loop_shelve
    """
    filename = "loop_shelve"
    autotest_bin_d = os.path.join(os.getcwd(),'kvm-test/bin/autotest')
    pwd = os.path.join(os.getcwd(),'kvm-test/tests/kvm/')
    shelve_filename = os.path.join(os.getcwd(),'loop_shelve')

    os.system('rm -rf %s' % shelve_filename)
    db = shelve.open(shelve_filename,writeback=False)
    db['loop'] = str
    if dict:
        db['dict'] = dict
    if env_dict:
        db['env'] = env_dict
    db.close()
