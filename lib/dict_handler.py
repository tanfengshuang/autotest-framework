##@ Summary:
##@ Description:
##@ Maintainer: Chen Cao <kcao@redhat.com>
##@ Update:     Sep 26, 2010
##@ Version:    1

import os, sys, getopt, shelve
import logging, common


dict_template = {
'main_vm':               'vm1',
'start_vm':              'yes',
'dst_vm':                'vm2',
'vms':                   'vm1',
'serial_file':           None,
'serial_dev':            None,
'bus_id':                None,
'vmlinuz':               None,
'initrd':                None,
'extra_params':          ' -usbdevice tablet -no-hpet',
'kill_vm_gracefully':    'yes',
'kill_vm_timeout':       '60',
'kill_vm_timeout_on_error':'0',
'kill_vm_on_error':       'no',
'use_storage':            'local',
'cmd_reboot':             'shutdown -r now',
'cmd_shutdown':           'shutdown -h now',
'migration_test_command' : None,
'ssh_status_test_command': 'echo $?',
'depend':                 '[]',
'display':                'vnc',
'fail_if_stuck_for':      '300',
'name':                   'rhel53_server-install',
'password':               '123456',
'shortname':              'standalone_example',
'steps':                 'RHEL-Server-5.3-64.steps',
'user':                  '',
'username':              'root',
'host_passwd':           'redhat',
'src_host':              '0.0.0.0',
'dst_host':              '0.0.0.0',
'guest_name':            'RHEL-Server-6.0',
'guest_type':            'rhel_server_60_64',
'type':                  'jumbo',
'test_name':             None,
'platform':              '64',
'host_type':             'small',
'storage_dir':           None,
'use_storage':           'local',
'nfs_storage':           '10.66.71.226',
'nfs_mntdir':            '/vol/kvm1/auto/nfs_storage',
'nfs_localdir':          '/tmp/kvm_autotest_root/images',
'LogVol_name':           None,
'iscsi_server':          '10.66.90.100',
'iscsi_initiator':       'iqn.2010-07.com.redhat:kvmautotest',
'iscsi_keyword':         'kvm',
'iscsi_dev':             '',
'iscsi_number':          '',
'images':               'image1',
'image_format':         'qcow2',
'image_size':           '40G',
'image_name' :          'images/RHEL-Server-5.3-64',
'image_boot':           'yes',
'image_snapshot':       'no',
'image_snapshot_vm2':   'yes',
'force_create_image':   'no',
'drive_format':         'virtio_blk',
'floppy_image':         None,
'snapshot':             'no',
'img_clean':            'no',
'cdrom':                '',
'md5sum':               'c5ed6b284410f4d8212cafc78fd7a8c5',
'md5sum_1m':            'b999f437583098ea5bbd56fb1de1d011',
'keep_ppm_files':       'no',
'keep_ppm_files_on_error':'no',
'mac_prefix':           '00:11:22:33:44:',
'guest_port_ssh':       '22',
'network':              'user',
'nic_model':            'virtio_nic',
'nics':                 'nic1',
'bridge_nic2':          'virbr0',
'redirs':               'ssh',
'ssh_port':             '22',
'ssh_prompt':           '\[root@.{0,50}][\#\$]',
'bridge':               'switch',
'bridge_names':         'switch virbr0 breth0',
'vlan_mode':            'default',
'vlan_id':              None,
'nic_list':             None,
'if_type':              None,
'mem':                  '512',
'vcpu':                 2,
'vcpu_cores':           '0',
'vcpu_threads':         '0',
'vcpu_socket':          '0',
'test_timeout':          None,
'mig_timeout':           600,
'login_timeout':         360,
'install_timeout':       130,
'ksm':                   '0',
'ksm_size':              None,
'remote_host':           None,
'remote_login':          None,
'format_list':           None,
'size':                  None,
'app':                   None,
'test_control_file':     'control',
'migration_src':         None,
'reboot':                None,
'npages':                None,
'sleep':                 None,
'dependency':            'none',
'category':              'function_all',
'testcase':              'boot',
'ipfix':                 'yes',
'nrepeat':               1,
'iterations':            1,
'logstyle':              'virtlab',
'clone':                 'yes',
'dryrun':                'no',
'ins':                   1,
'use_telnet':            'no',
'rhev':                  'no',
'stress':                'autotest.stress',
'wait_augment_ratio':    1,
'hugepage':              'no',
"versions":              'kvm-83-142.el5',
'single':                'yes',
"verbose":               'no',
'run_loop':              'yes',
'virtlab':               'no',
'supercmd':              'none',
'tags':                  'VT,KVM_TEST',
'profile':               '',
'autotest_tree':         'git://10.66.82.200/autotest',
'autotest_branch':       'master',
'use_customized_cmd':    'yes',
'customized_cmd':        'none',
'launcher_tree':         'git://10.66.82.200/autotest',
'launcher_branch':       'master',
'launch_agent':          'loop',
}


def build_dict(argv):
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

    if os.system("yum -h &> /dev/null"):
        dict['rhev'] = 'yes'
    else:
        dict['rhev'] = 'no'

    return common.ip_fixup(dict)


def parse_params(dict, loop = False):
    fixup = ""
    # Guest Name resolution
    if dict['guest_name'] != 'all':
        fixup += "only %s\n" % dict['guest_name']
    # Guest Platform resolution
    if dict['platform'] != 'all':
        fixup += "only %s\n" % dict['platform']
    # Guest Drive format resolution
    if dict['drive_format'] != 'all':
        fixup += "only %s\n" % dict['drive_format']
    # Guest NIC model handling
    if dict['nic_model'] != 'all':
        fixup += "only %s\n" % dict['nic_model']
    # Image format handling
    if dict['image_format'] != 'all':
        fixup += "only %s\n" % dict['image_format']
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
    # Host type
    fixup += "host_type = %s\n" % dict['host_type']
    if dict.get('nic_model') == 'virtio_nic' or \
       dict.get('drive_format') == 'virtio_blk' or \
       dict.get('nic_model') == 'all' or \
       dict.get('drive_format') == 'all':
        fixup += "image_name += -virtio\n"
    if dict.get('ipfix') == 'no':
        fixup += "ipfix = no\n"
    if dict.get('src_host') != '0.0.0.0':
        fixup += "src_host = %s\n" % dict.get('src_host')
    if dict.get('dst_host') != '0.0.0.0':
        fixup += "dst_host = %s\n" % dict.get('dst_host')
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
    if dict.get('vcpu') and not loop:
        fixup += "smp = %s\n" % dict.get('vcpu')
    if dict.get('vcpu_cores') and not loop:
        fixup += "vcpu_cores = %s\n" % dict.get('vcpu_cores')
    if dict.get('vcpu_threads') and not loop:
        fixup += "vcpu_threads = %s\n" % dict.get('vcpu_threads')
    if dict.get('vcpu_socket') and not loop:
        fixup += "vcpu_socket = %s\n" % dict.get('vcpu_socket')
    if dict.get('mem') and not loop:
        fixup += "mem = %s\n" % dict.get('mem')
    if dict.get('iterations'):
        fixup += "iterations = %s\n" % dict.get('iterations')

    if dict.get('hugepages') == 'yes':
        fixup += 'only hugepages\n'
    if not dict.get('hugepages') or dict.get('hugepages') == 'no':
        fixup += 'only smallpages\n'

    if dict.get('test_timeout') != None:
        fixup += "test_timeout = %s\n" % dict.get('test_timeout')

    return fixup


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


def combine_fixup(dict, string,
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
    fixup_top += "pci_assignable = no\n"

    if dict.get("iscsi_dev") != None:
        fixup_bottom += "iscsi_dev = %s\n" % dict.get('iscsi_dev')
    if dict.get("iscsi_number") != None:
        fixup_bottom += "iscsi_number = %s\n" % dict.get('iscsi_number')

    return fixup_top + string + fixup_bottom


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

