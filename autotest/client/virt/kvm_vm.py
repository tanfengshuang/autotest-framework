"""
Utility classes and functions to handle Virtual Machine creation using qemu.

@copyright: 2008-2009 Red Hat Inc.
"""

import time, os, logging, fcntl, re, commands, shelve, glob
import virt_test_utils
from autotest_lib.client.common_lib import error, cartesian_config
from autotest_lib.client.bin import utils
import virt_utils, virt_vm, virt_test_setup, kvm_monitor, aexpect


class VM(virt_vm.BaseVM):
    """
    This class handles all basic VM operations.
    """

    MIGRATION_PROTOS = ['tcp', 'unix', 'exec']

    def __init__(self, name, params, root_dir, address_cache, state=None):
        """
        Initialize the object and set a few attributes.

        @param name: The name of the object
        @param params: A dict containing VM params
                (see method make_qemu_command for a full description)
        @param root_dir: Base directory for relative filenames
        @param address_cache: A dict that maps MAC addresses to IP addresses
        @param state: If provided, use this as self.__dict__
        """
        virt_vm.BaseVM.__init__(self, name, params)

        if state:
            self.__dict__ = state
        else:
            self.process = None
            self.serial_console = None
            self.redirs = {}
            self.vnc_port = 5900
            self.monitors = []
            self.pci_assignable = None
            self.netdev_id = []
            self.device_id = []
            self.tapfds = []
            self.uuid = None


        self.init_pci_addr = int(params.get("init_pci_addr", 4))
        self.spice_port = 8000
        self.name = name
        self.params = params
        self.root_dir = root_dir
        self.address_cache = address_cache
        self.index_in_use = {}

        self.host_version = cartesian_config.get_host_verson(self.params)


    def verify_alive(self):
        """
        Make sure the VM is alive and that the main monitor is responsive.

        @raise VMDeadError: If the VM is dead
        @raise: Various monitor exceptions if the monitor is unresponsive
        """
        try:
            virt_vm.BaseVM.verify_alive(self)
            if self.monitors:
                self.monitor.verify_responsive()
        except virt_vm.VMDeadError:
            raise virt_vm.VMDeadError(self.process.get_status(),
                                      self.process.get_output())


    def is_alive(self):
        """
        Return True if the VM is alive and its monitor is responsive.
        """
        return not self.is_dead() and (not self.monitors or
                                       self.monitor.is_responsive())


    def is_dead(self):
        """
        Return True if the qemu process is dead.
        """
        return not self.process or not self.process.is_alive()




    def clone(self, name=None, params=None, root_dir=None, address_cache=None,
              copy_state=False):
        """
        Return a clone of the VM object with optionally modified parameters.
        The clone is initially not alive and needs to be started using create().
        Any parameters not passed to this function are copied from the source
        VM.

        @param name: Optional new VM name
        @param params: Optional new VM creation parameters
        @param root_dir: Optional new base directory for relative filenames
        @param address_cache: A dict that maps MAC addresses to IP addresses
        @param copy_state: If True, copy the original VM's state to the clone.
                Mainly useful for make_qemu_command().
        """
        if name is None:
            name = self.name
        if params is None:
            params = self.params.copy()
        if root_dir is None:
            root_dir = self.root_dir
        if address_cache is None:
            address_cache = self.address_cache
        if copy_state:
            state = self.__dict__.copy()
        else:
            state = None
        return VM(name, params, root_dir, address_cache, state)


    def __make_qemu_command(self, name=None, params=None, root_dir=None):
        """
        Generate a qemu command line. All parameters are optional. If a
        parameter is not supplied, the corresponding value stored in the
        class attributes is used.

        @param name: The name of the object
        @param params: A dict containing VM params
        @param root_dir: Base directory for relative filenames

        @note: The params dict should contain:
               mem -- memory size in MBs
               cdrom -- ISO filename to use with the qemu -cdrom parameter
               extra_params -- a string to append to the qemu command
               shell_port -- port of the remote shell daemon on the guest
               (SSH, Telnet or the home-made Remote Shell Server)
               shell_client -- client program to use for connecting to the
               remote shell daemon on the guest (ssh, telnet or nc)
               x11_display -- if specified, the DISPLAY environment variable
               will be be set to this value for the qemu process (useful for
               SDL rendering)
               images -- a list of image object names, separated by spaces
               nics -- a list of NIC object names, separated by spaces

               For each image in images:
               drive_format -- string to pass as 'if' parameter for this
               image (e.g. ide, scsi)
               image_snapshot -- if yes, pass 'snapshot=on' to qemu for
               this image
               image_boot -- if yes, pass 'boot=on' to qemu for this image
               In addition, all parameters required by get_image_filename.

               For each NIC in nics:
               nic_model -- string to pass as 'model' parameter for this
               NIC (e.g. e1000)
        """

        # Helper function for command line option wrappers
        def has_option(help, option):
            return bool(re.search(r"^-%s(\s|$)" % option, help, re.MULTILINE))

        # Wrappers for all supported qemu command line parameters.
        # This is meant to allow support for multiple qemu versions.
        # Each of these functions receives the output of 'qemu -help' as a
        # parameter, and should add the requested command line option
        # accordingly.


        def get_free_pci_addr(pci_addr=None):
            """
            return *hex* format free pci addr.

            @param pci_addr: *decimal* formated, desired pci_add
            """
            if pci_addr is None:
                pci_addr = self.init_pci_addr
                while True:
                    # actually when pci_addr > 20? errors may happen
                    if pci_addr > 31:
                        raise error.TestError("pci_addr got too big.")
                    if pci_addr in self.pci_addr_list:
                        pci_addr += 1
                    else:
                        self.pci_addr_list.append(pci_addr)
                        return hex(pci_addr)
            elif int(pci_addr) in self.pci_addr_list:
                raise error.TestError("PCI address 0x%s is already in use."
                                      " Recheck the config file." % pci_addr)
            else:
                self.pci_addr_list.append(int(pci_addr))
                return hex(int(pci_addr))


        def add_name(help, name):
            return " -name '%s'" % name

        def add_human_monitor(help, filename):
            if has_option(help, "chardev"):
                # -chardev socket, id=monitor,path=\
                #   /var/lib/libvirt/qemu/r6.monitor,server,nowait
                # -mon chardev=monitor,mode=readline
                id = "human_monitor_id_%s" % monitor_name
                cmd = " -chardev socket,id=%s,path=%s,server,nowait" % \
                      (id, filename)
                cmd += " -mon chardev=%s,mode=readline" % id
                return cmd
            else:
                return " -monitor unix:'%s',server,nowait" % filename

        def add_qmp_monitor(help, filename):
            if has_option(help, "qmp"):
                if has_option(help, "chardev"):
                    # -chardev socket, id=monitor,path=\
                    #   /var/lib/libvirt/qemu/r6.monitor,server,nowait
                    # -mon chardev=monitor,mode=control
                    id = "qmp_monitor_id_%s" % monitor_name
                    cmd = " -chardev socket,id=%s,path=%s,server,nowait" % \
                          (id, filename)
                    cmd += " -mon chardev=%s,mode=control" % id
                    return cmd
                else:
                    return " -qmp unix:'%s',server,nowait" % filename
            else:
                return add_human_monitor(help, filename)

        def add_serial(help, filename):
            if has_option(help, "chardev"):
                default_id = "serial_id_%s" % self.instance
                cmd = " -chardev socket,id=%s,path=%s,server,nowait" % \
                                          (default_id, filename)
                cmd += " -device isa-serial,chardev=%s" % default_id
                return cmd
            else:
                return " -serial unix:'%s',server,nowait" % filename

        def add_mem(help, mem):
            return " -m %s" % mem

        def add_smp(help, smp,
                    vcpu_cores="0", vcpu_threads="0", vcpu_sockets="0"):
            smp_str = " -smp %s" % smp
            # the value is not None, "", or "0"
            if vcpu_cores and vcpu_cores !="0":
                smp_str += ",cores=%s" % vcpu_cores
            if vcpu_threads and vcpu_threads !="0":
                smp_str += ",threads=%s" % vcpu_threads
            if vcpu_sockets and vcpu_sockets !="0":
                smp_str += ",sockets=%s" % vcpu_sockets
            return smp_str

        def add_cdrom(help, filename, index=None):
            if has_option(help, "drive"):
                cmd = " -drive file='%s',media=cdrom" % filename
                if index is not None and index.isdigit():
                    cmd += ",index=%s" % index
                return cmd
            else:
                return " -cdrom '%s'" % filename

        def add_drive(help, filename, index=None, format=None, cache=None,
                      werror=None, rerror=None, serial=None, snapshot=False,
                      boot=False, blkdebug=None,imgfmt="raw", aio=None,
                      media="disk", ide_bus=None, ide_unit=None, vdisk=None,
                      pci_addr=None,floppy_unit=None, readonly=False,
                      physical_block_size=None, logical_block_size=None):
            free_pci_addr = get_free_pci_addr(pci_addr)

            dev = {"virtio" : "virtio-blk-pci",
                   "ide" : "ide-drive"}

            if format == "ide":
                id ="ide0-%s-%s" % (ide_bus, ide_unit)
                ide_bus = "ide." + str(ide_bus)
            elif format == "virtio":
                if media == "disk":
                    vdisk += 1
                blkdev_id ="virtio-disk%s" % vdisk
                id = "virtio-disk%s" % vdisk
            if media == "floppy":
                id ="fdc0-0-%s" % floppy_unit
            blkdev_id = "drive-%s" % id

            # -drive part
            if blkdebug is not None:
                cmd = " -drive file=blkdebug:%s:%s" % (blkdebug, filename)
            else:
                cmd = " -drive file='%s'" % filename

            if index is not None and index.isdigit():
                cmd += ",index=%s" % index
            if has_option(help, "device"):
                cmd += ",if=none"
                cmd += ",id=%s" % blkdev_id
            else:
                if format: cmd += ",if=%s" % format

            if media != "floppy":
                cmd += ",media=%s" % media
            if cache: cmd += ",cache=%s" % cache
            if rerror:
                cmd += ",rerror=%s" % rerror
            if werror: cmd += ",werror=%s" % werror
            if serial: cmd += ",serial=%s" % serial
            if snapshot: cmd += ",snapshot=on"
            if boot: cmd += ",boot=on"
            if media == "cdrom" or readonly : cmd += ",readonly=on"
            cmd += ",format=%s" % imgfmt
            if ",aio=" in help and aio : cmd += ",aio=%s" % aio

            # -device part
            if has_option(help, "device") and media != "floppy":
                cmd += " -device %s" % dev[format]
                if format == "ide":
                    cmd += ",bus=%s" % ide_bus
                    cmd += ",unit=%s" % ide_unit
                else:
                    cmd += ",bus=pci.0,addr=%s" % free_pci_addr
                    if physical_block_size:
                        cmd += ",physical_block_size=%s" % physical_block_size
                    if logical_block_size:
                        cmd += ",logical_block_size=%s" % logical_block_size
                cmd += ",drive=%s" % blkdev_id
                cmd += ",id=%s" % id

            # -global part
            drivelist = ['driveA','driveB']
            if has_option(help,"global") and media == "floppy" :
                cmd += " -global isa-fdc.%s=drive-%s" \
                          % (drivelist[floppy_unit],id)
            return cmd

        def add_nic(help, vlan, model=None, mac=None, netdev_id=None,
                    nic_extra_params=None, pci_addr=None, device_id=None):
            free_pci_addr = get_free_pci_addr(pci_addr)

            if has_option(help, "netdev"):
                netdev_vlan_str = ",netdev=%s" % netdev_id
            else:
                netdev_vlan_str = ",vlan=%d" % vlan

            if has_option(help, "device"):
                if not model:
                    model = "rtl8139"
                elif model == "virtio":
                    model = "virtio-net-pci"
                cmd = " -device %s" % model + netdev_vlan_str
                if mac:
                    cmd += ",mac=%s" % mac

                if has_option(help, "netdev"):
                    cmd += ",id=%s" % "ndev00" + netdev_id

                # only pci domain=0,bus=0,function=0 is supported for now.
                #
                # libvirt gains the pci_slot, free_pci_addr here,
                # value by parsing the xml file, i.e. counting all the
                # pci devices and store the number.
                cmd += ",bus=pci.0,addr=%s" % free_pci_addr
                if nic_extra_params:
                    cmd += ",%s" % nic_extra_params
            else:
                cmd = " -net nic" + netdev_vlan_str
                if model:
                    cmd += ",model=%s" % model
                if mac:
                    cmd += ",macaddr='%s'" % mac
            if device_id:
                cmd += ",id='%s'" % device_id
            return cmd

        def add_net(help, vlan, mode, ifname=None, script=None,
                    downscript=None, tftp=None, bootfile=None, hostfwd=[],
                    netdev_id=None, vhost=None, netdev_extra_params=None,
                    tapfd=None):
            if has_option(help, "netdev"):
                cmd = " -netdev %s,id=%s" % (mode, netdev_id)
                if vhost:
                    cmd += ",%s" % vhost
                if netdev_extra_params:
                    cmd += ",%s" % netdev_extra_params
            else:
                cmd = " -net %s,vlan=%d" % (mode, vlan)
            if mode == "tap" and tapfd is not None:
                cmd += ",fd=%d" % tapfd
            elif mode == "user":
                if tftp and "[,tftp=" in help:
                    cmd += ",tftp='%s'" % tftp
                if bootfile and "[,bootfile=" in help:
                    cmd += ",bootfile='%s'" % bootfile
                if "[,hostfwd=" in help:
                    for host_port, guest_port in hostfwd:
                        cmd += ",hostfwd=tcp::%s-:%s" % (host_port, guest_port)
            else:
                if ifname:
                    cmd += ",ifname='%s'" % ifname
                if script:
                    cmd += ",script='%s'" % script
                cmd += ",downscript='%s'" % (downscript or "no")

            return cmd

        def add_floppy(help, filename):
            return " -fda '%s'" % filename

        def add_usbdevice(help, filename):
            if has_option(help, "device"):
                id = virt_utils.generate_random_id()
                return " -usb -device usb-tablet,id=%s%s" % (filename, id)
            else:
                return " -usbdevice %s" % filename


        def add_tftp(help, filename):
            # If the new syntax is supported, don't add -tftp
            if "[,tftp=" in help:
                return ""
            else:
                return " -tftp '%s'" % filename

        def add_bootp(help, filename):
            # If the new syntax is supported, don't add -bootp
            if "[,bootfile=" in help:
                return ""
            else:
                return " -bootp '%s'" % filename

        def add_tcp_redir(help, host_port, guest_port):
            # If the new syntax is supported, don't add -redir
            if "[,hostfwd=" in help:
                return ""
            else:
                return " -redir tcp:%s::%s" % (host_port, guest_port)

        def add_vnc(help, vnc_port, vnc_password='no', extra_params=None):
            vnc_cmd = " -vnc :%d" % (vnc_port - 5900)
            if "yes" in vnc_password:
                vnc_cmd += ",password"
            if extra_params is not None:
                vnc_cmd += ",%s" % extra_params
            return vnc_cmd

        def add_sdl(help):
            if has_option(help, "sdl"):
                return " -sdl"
            else:
                return ""

        def add_nographic(help):
            return " -nographic"

        def add_uuid(help, uuid):
            return " -uuid '%s'" % uuid

        def add_pcidevice(help, host):
            return " -pcidevice host=%s" % host

        def add_spice(help, port, param):
            if has_option(help,"spice"):
                return " -spice port=%s,%s" % (port, param)
            else:
                return ""

        def add_qxl_vga(help, qxl, vga, qxl_dev_nr=None):
            str = ""
            if has_option(help, "qxl"):
               if qxl and qxl_dev_nr is not None:
                  str += " -qxl %s" % qxl_dev_nr
               if has_option(help, "vga") and vga and vga != "qxl":
                  str += " -vga %s" % vga
            elif has_option(help, "vga"):
               if qxl:
                   str += " -vga qxl"
               elif vga:
                   str += " -vga %s" % vga
            return str


        def add_kernel(help, filename):
            return " -kernel '%s'" % filename

        def add_initrd(help, filename):
            return " -initrd '%s'" % filename

        def add_rtc(help):
            # Pay attention that rtc-td-hack is for early version
            # if "rtc " in help:
            if has_option(help, "rtc"):
                base = params.get("rtc_base", "utc")
                clock = params.get("rtc_clock", "host")
                drift = params.get("rtc_drift", "none")
                return " -rtc base=%s,clock=%s,driftfix=%s" % (base, clock, drift)
            else:
                return " -rtc-td-hack"

        def add_kernel_cmdline(help, cmdline):
            return " -append %s" % cmdline

        def add_testdev(help, filename):
            return (" -chardev file,id=testlog,path=%s"
                    " -device testdev,chardev=testlog" % filename)

        def add_no_hpet(help):
            if has_option(help, "no-hpet"):
                return " -no-hpet"
            else:
                return ""

        def add_cpu_flags(help, cpu_model, flags=None, vendor_id=None,
                          family=None):
            if has_option(help, 'cpu'):
                cmd = " -cpu %s" % cpu_model

                if vendor_id:
                    cmd += ",vendor=\"%s\"" % vendor_id
                if flags:
                    cmd += ",%s" % flags
                if family is not None:
                    cmd += ",family=%s" % family
                return cmd
            else:
                return ""

        def add_boot(help, boot_order, boot_once, boot_menu):
            cmd = "-boot "
            if has_option(help, "boot \[a\|c\|d\|n\]"):
                cmd += "%s" % boot_once
            elif has_option(help, "boot \[order=drives\]\[,once=drives\]\[,menu=on\|off\]"):
                cmd += "order=%s,once=%s,menu=%s " % (boot_order, boot_once, boot_menu)
            else:
                cmd = ""
            return cmd

        def get_index(index):
            while self.index_in_use.get(str(index)):
                index += 1
            return index

        # End of command line option wrappers

        if name is None:
            name = self.name
        if params is None:
            params = self.params
        if root_dir is None:
            root_dir = self.root_dir

        # Clone this VM using the new params
        vm = self.clone(name, params, root_dir, copy_state=True)

        # global counters
        ide_bus = 0
        ide_unit = 0
        vdisk = 0
        floppy_unit = 0
        self.pci_addr_list = [0, 1, 2]
        self.host_version = cartesian_config.get_host_verson(self.params)

        qemu_binary = virt_utils.get_path(root_dir, params.get("qemu_binary",
                                                              "qemu"))
        # Get the output of 'qemu -help' (log a message in case this call never
        # returns or causes some other kind of trouble)
        logging.debug("Getting output of 'qemu -help'")
        help = commands.getoutput("%s -help" % qemu_binary)

        index_global = 0
        # init the dict index_in_use
        for key in params.keys():
            if 'drive_index' in key:
                self.index_in_use[params.get(key)] = True

        # Start constructing the qemu command
        qemu_cmd = ""
        # Set the X11 display parameter if requested
        if params.get("x11_display"):
            qemu_cmd += "DISPLAY=%s " % params.get("x11_display")
        # Add the qemu binary
        qemu_cmd += qemu_binary
        # Add the VM's name
        qemu_cmd += add_name(help, name)
        # Add monitors
        for monitor_name in params.objects("monitors"):
            monitor_params = params.object_params(monitor_name)
            monitor_filename = vm.get_monitor_filename(monitor_name)
            if monitor_params.get("monitor_type") == "qmp":
                qemu_cmd += add_qmp_monitor(help, monitor_filename)
            else:
                qemu_cmd += add_human_monitor(help, monitor_filename)


        # Add serial console redirection
        qemu_cmd += add_serial(help, vm.get_serial_console_filename())

        for image_name in params.objects("images"):
            image_params = params.object_params(image_name)
            if image_params.get("boot_drive") == "no":
                continue

            if params.get("index_enable") == "yes":
                drive_index = image_params.get("drive_index")
                if drive_index:
                    index = drive_index
                else:
                    index_global = get_index(index_global)
                    index = str(index_global)
                    index_global += 1
            else:
                index = None
            qemu_cmd += add_drive(help,
                                  virt_vm.get_image_filename(image_params, root_dir),
                                  index,
                                  image_params.get("drive_format"),
                                  image_params.get("drive_cache"),
                                  image_params.get("drive_rerror"),
                                  image_params.get("drive_werror"),
                                  image_params.get("drive_serial"),
                                  image_params.get("image_snapshot") == "yes",
                                  image_params.get("image_boot") == "yes",
                  virt_vm.get_image_blkdebug_filename(image_params, root_dir),
                                  image_params.get("image_format"),
                                  image_params.get("image_aio", "native"),
                                  "disk", ide_bus, ide_unit, vdisk,
                                  image_params.get("drive_pci_addr"),
                physical_block_size=image_params.get("physical_block_size"),
                logical_block_size=image_params.get("logical_block_size")
                                  )

            # increase the bus and unit no for ide device
            if params.get("drive_format") == "ide":
                if ide_unit == 1:
                    ide_bus += 1
                ide_unit ^= 1
            else:
                vdisk += 1

        redirs = []
        for redir_name in params.objects("redirs"):
            redir_params = params.object_params(redir_name)
            guest_port = int(redir_params.get("guest_port"))
            host_port = vm.redirs.get(guest_port)
            redirs += [(host_port, guest_port)]

        if params.get('pci_assignable') == "no":
            vlan = 0
            for nic_name in params.objects("nics"):
                nic_params = params.object_params(nic_name)
                try:
                    netdev_id = vm.netdev_id[vlan]
                    device_id = vm.device_id[vlan]
                except IndexError:
                    netdev_id = None
                    device_id = None
                # Handle the '-net nic' part
                try:
                    mac = self.get_mac_address(vlan)
                except virt_vm.VMAddressError:
                    mac = None
                except IndexError:
                    mac = None
                if len(self.netdev_id) < vlan+1:
                    self.netdev_id.append(virt_utils.generate_random_id())
                qemu_cmd += add_nic(help, vlan, nic_params.get("nic_model"), mac,
                                    self.netdev_id[vlan],
                                    nic_params.get("nic_extra_params"),
                                    nic_params.get("nic_pci_addr"))

                # Handle the '-net tap' or '-net user' part
                script = nic_params.get("nic_script")
                downscript = nic_params.get("nic_downscript")
                tftp = nic_params.get("tftp")
                vhost = nic_params.get("vhost")
                if script:
                    script = virt_utils.get_path(root_dir, script)
                if downscript:
                    downscript = virt_utils.get_path(root_dir, downscript)
                if tftp:
                    tftp = virt_utils.get_path(root_dir, tftp)
                if nic_params.get("nic_mode") == "tap":
                    try:
                        tapfd = vm.tapfds[vlan]
                    except:
                        tapfd = None
                else:
                    tapfd = None
                qemu_cmd += add_net(help, vlan, nic_params.get("nic_mode", "user"),
                                    vm.get_ifname(vlan),
                                    script, downscript, tftp,
                                    nic_params.get("bootp"), redirs, netdev_id,
                                    nic_params.get("netdev_extra_params"),
                                    vhost, tapfd)

                # Proceed to next NIC
                vlan += 1
        else:
            qemu_cmd += " -net none"

        mem = params.get("mem")
        if mem:
            qemu_cmd += add_mem(help, mem)

        smp = params.get("smp", 1)

        vcpu_threads = params.get("vcpu_threads", "1")
        vcpu_cores = params.get("vcpu_cores", smp)
        vcpu_sockets = params.get("vcpu_sockets", "1")
        guest_name = params.get("guest_name")

        if int(smp) > 8 and vcpu_threads == "1":
            vcpu_threads = "2"
        if (vcpu_sockets and int(vcpu_sockets) > 2  and "Win" in
                               re.findall("win", guest_name, re.I)):
            vcpu_sockets = "2"

        if not vcpu_cores:
            vcpu_cores = str(int(smp)/int(vcpu_threads)/int(vcpu_sockets))
        if not vcpu_threads:
            vcpu_threads = str(int(smp)/int(vcpu_cores)/int(vcpu_sockets))
        if not vcpu_sockets:
            vcpu_sockets = str(int(smp)/int(vcpu_cores)/int(vcpu_threads))
        if smp == "1":
            vcpu_threads = "1"
            vcpu_cores = "1"
            vcpu_sockets = "1"

        if smp:
            qemu_cmd += add_smp(help, smp,
                                vcpu_cores, vcpu_threads, vcpu_sockets)

        # Add cdroms
        for cdrom in params.objects("cdroms"):
            cdrom_params = params.object_params(cdrom)
            iso = cdrom_params.get("cdrom")
            if iso:
                iso = virt_utils.get_path(root_dir, iso)
                if params.get("index_enable") == "yes":
                    drive_index = cdrom_params.get("drive_index")
                    if drive_index:
                        index = drive_index
                    else:
                        index_global = get_index(index_global)
                        index = str(index_global)
                        index_global += 1
                else:
                    index = None
                if has_option(help, "device"):
                    qemu_cmd += add_drive(help, iso, index, "ide", media="cdrom",
                                          ide_bus=ide_bus, ide_unit=ide_unit)
                else:
                    qemu_cmd += add_cdrom(help, iso, index)
                if ide_unit == 1:
                    ide_bus += 1
                ide_unit ^= 1

        cpu_model = params.get("cpu_model", "qemu64")
        if "2.6.32" in commands.getoutput("uname -r"):
            cpu_model = "cpu64-rhel6"
        flags = params.get("extra_flags")
        x2apic = params.get("enable_x2apic")

        if "el6" in commands.getoutput("uname -r") and x2apic=="yes":
            flags += ",+x2apic"

        qemu_cmd += add_cpu_flags(help, cpu_model, flags,
                                  params.get("cpu_vendor_id"),
                                  params.get("family"))

        soundhw = params.get("soundcards")
        if soundhw:
            if "2.6.32" not in commands.getoutput("uname -r"):
                qemu_cmd += " -soundhw %s" % soundhw

        # We may want to add the floppy using the "-drive -global " format
        # and the current script allow the nums of the floppies to be 2
        # Readonly floppy is supported by adding the parameter of floppy_readonly
        floppies = params.get("floppy")
        floppies_readonly = params.get("floppy_readonly")
        if floppies:
            for floppy in floppies.split():
                floppy = virt_utils.get_path(root_dir, floppy)
                qemu_cmd += add_floppy(help, floppy)
        if floppies and floppies_readonly:
            floppy_list = floppies.split()
            fl_readonly_list = floppies_readonly.split()
            for index in range(len(fl_readonly_list)):
                fl_readonly_list[index] = eval(fl_readonly_list[index])
            if len(floppy_list) > 2 :
                raise error.TestError("Only the maximum of 2 floppies"
                                      " can be supported here")
            for (floppy,fl_readonly) in zip(floppy_list,fl_readonly_list):
                floppy = virt_utils.get_path(root_dir, floppy)
                if has_option(help,"global"):
                    qemu_cmd += add_drive(help,floppy,media="floppy",
                        floppy_unit=floppy_unit,readonly=fl_readonly)
                else:
                    qemu_cmd += add_floppy(help, floppy)
                floppy_unit ^= 1

        usbdevice = params.get("usbdevice")
        if usbdevice:
            qemu_cmd += add_usbdevice(help, usbdevice)

        tftp = params.get("tftp")
        if tftp:
            tftp = virt_utils.get_path(root_dir, tftp)
            qemu_cmd += add_tftp(help, tftp)

        bootp = params.get("bootp")
        if bootp:
            qemu_cmd += add_bootp(help, bootp)

        kernel = params.get("kernel")
        if kernel:
            kernel = virt_utils.get_path(root_dir, kernel)
            qemu_cmd += add_kernel(help, kernel)

        kernel_cmdline = params.get("kernel_cmdline")
        if kernel_cmdline:
            qemu_cmd += add_kernel_cmdline(help, kernel_cmdline)

        initrd = params.get("initrd")
        if initrd:
            initrd = virt_utils.get_path(root_dir, initrd)
            qemu_cmd += add_initrd(help, initrd)

        for host_port, guest_port in redirs:
            qemu_cmd += add_tcp_redir(help, host_port, guest_port)

        if params.get("display") == "vnc":
            vnc_extra_params = params.get("vnc_extra_params")
            vnc_password = "no"
            if params.get("vnc_password"):
                vnc_password = params.get("vnc_password")
            qemu_cmd += add_vnc(help, self.vnc_port, vnc_password,
                                                     vnc_extra_params)
        elif params.get("display") == "sdl":
            qemu_cmd += add_sdl(help)
        elif params.get("display") == "nographic":
            qemu_cmd += add_nographic(help)
        elif params.get("display") == "spice":
            qemu_cmd += add_spice(help, self.spice_port, params.get("spice"))

        qxl = ""
        vga = ""
        if params.get("qxl"):
            qxl = params.get("qxl")
        if params.get("vga"):
            vga = params.get("vga")
        if qxl or vga:
            if params.get("display") == "spice":
                qxl_dev_nr = params.get("qxl_dev_nr", None)
                qemu_cmd += add_qxl_vga(help, qxl, vga, qxl_dev_nr)

        if params.get("uuid") == "random":
            qemu_cmd += add_uuid(help, vm.uuid)
        elif params.get("uuid"):
            qemu_cmd += add_uuid(help, params.get("uuid"))

        if params.get("testdev") == "yes":
            qemu_cmd += add_testdev(help, vm.get_testlog_filename())

        if params.get("disable_hpet") == "yes":
            qemu_cmd += add_no_hpet(help)

        # If the PCI assignment step went OK, add each one of the PCI assigned
        # devices to the qemu command line.
        if vm.pci_assignable:
            for pci_id in vm.pa_pci_ids:
                qemu_cmd += add_pcidevice(help, pci_id)

        qemu_cmd += add_rtc(help)

        if has_option(help, "boot"):
            boot_order = params.get("boot_order", "cdn")
            boot_once = params.get("boot_once", "c")
            boot_menu = params.get("boot_menu", "off")
            qemu_cmd += " %s " % add_boot(help, boot_order, boot_once, boot_menu)

        # Add for RHEL 7 by GG
        if params.get("url"):
            RHEL_URL = params.get("url")
            replaced_append = "ksdevice=link ks=cdrom:/dev/sr0 nicdelay=60 console=ttyS0,115200 console=tty0 root=live:%s/LiveOS/squashfs.img" % RHEL_URL
            if "RHEL-7" in RHEL_URL:
                params["extra_params"] = params.get("extra_params").replace("ks=cdrom nicdelay=60 console=ttyS0,115200 console=tty0", replaced_append)

        extra_params = params.get("extra_params")
        if extra_params:
            qemu_cmd += " %s" % extra_params

        if has_option(help, "enable-kvm") and params.get("enable-kvm",
                                                         "yes") == "yes":
            qemu_cmd += " -enable-kvm "

        return qemu_cmd


    @error.context_aware
    def create(self, name=None, params=None, root_dir=None, timeout=5.0,
               migration_mode=None, mac_source=None):
        """
        Start the VM by running a qemu command.
        All parameters are optional. If name, params or root_dir are not
        supplied, the respective values stored as class attributes are used.

        @param name: The name of the object
        @param params: A dict containing VM params
        @param root_dir: Base directory for relative filenames
        @param migration_mode: If supplied, start VM for incoming migration
                using this protocol (either 'tcp', 'unix' or 'exec')
        @param migration_exec_cmd: Command to embed in '-incoming "exec: ..."'
                (e.g. 'gzip -c -d filename') if migration_mode is 'exec'
        @param mac_source: A VM object from which to copy MAC addresses. If not
                specified, new addresses will be generated.

        @raise VMCreateError: If qemu terminates unexpectedly
        @raise VMKVMInitError: If KVM initialization fails
        @raise VMHugePageError: If hugepage initialization fails
        @raise VMImageMissingError: If a CD image is missing
        @raise VMHashMismatchError: If a CD image hash has doesn't match the
                expected hash
        @raise VMBadPATypeError: If an unsupported PCI assignment type is
                requested
        @raise VMPAError: If no PCI assignable devices could be assigned
        @raise TAPCreationError: If fail to create tap fd
        @raise BRAddIfError: If fail to add a tap to a bridge
        @raise TAPBringUpError: If fail to bring up a tap
        @raise PrivateBridgeError: If fail to bring the private bridge
        """
        error.context("creating '%s'" % self.name)
        self.destroy(free_mac_addresses=False)

        if name is not None:
            self.name = name
        if params is not None:
            self.params = params
        if root_dir is not None:
            self.root_dir = root_dir
        name = self.name
        params = self.params
        root_dir = self.root_dir

        self.init_pci_addr = int(params.get("init_pci_addr", 4))
        # Verify the md5sum of the ISO images
        for cdrom in params.objects("cdroms"):
            cdrom_params = params.object_params(cdrom)
            iso = cdrom_params.get("cdrom")
            if iso:
                iso = virt_utils.get_path(root_dir, iso)
                if not os.path.exists(iso):
                    raise virt_vm.VMImageMissingError(iso)
                compare = False
                if cdrom_params.get("md5sum_1m"):
                    logging.debug("Comparing expected MD5 sum with MD5 sum of "
                                  "first MB of ISO file...")
                    actual_hash = utils.hash_file(iso, 1048576, method="md5")
                    expected_hash = cdrom_params.get("md5sum_1m")
                    compare = True
                elif cdrom_params.get("md5sum"):
                    logging.debug("Comparing expected MD5 sum with MD5 sum of "
                                  "ISO file...")
                    actual_hash = utils.hash_file(iso, method="md5")
                    expected_hash = cdrom_params.get("md5sum")
                    compare = True
                elif cdrom_params.get("sha1sum"):
                    logging.debug("Comparing expected SHA1 sum with SHA1 sum "
                                  "of ISO file...")
                    actual_hash = utils.hash_file(iso, method="sha1")
                    expected_hash = cdrom_params.get("sha1sum")
                    compare = True
                if compare:
                    if actual_hash == expected_hash:
                        logging.debug("Hashes match")
                    else:
                        raise virt_vm.VMHashMismatchError(actual_hash,
                                                          expected_hash)

        # Make sure the following code is not executed by more than one thread
        # at the same time
        lockfile = open("/tmp/kvm-autotest-vm-create.lock", "w+")
        fcntl.lockf(lockfile, fcntl.LOCK_EX)

        try:
            # Handle port redirections
            redir_names = params.objects("redirs")
            host_ports = virt_utils.find_free_ports(5000, 6000, len(redir_names))
            self.redirs = {}
            for i in range(len(redir_names)):
                redir_params = params.object_params(redir_names[i])
                guest_port = int(redir_params.get("guest_port"))
                self.redirs[guest_port] = host_ports[i]

            # Generate netdev IDs for all NICs and create TAP fd
            self.netdev_id = []
            self.tapfds = []
            vlan = 0
            
            for nic in params.objects("nics"):
                self.netdev_id.append(virt_utils.generate_random_id())
                self.device_id.append(virt_utils.generate_random_id())
                nic_params = params.object_params(nic)
                if nic_params.get("nic_mode") == "tap" and\
                   nic_params.get("use_nic_scritps") == "no":
                    ifname = self.get_ifname(vlan)
                    brname = nic_params.get("bridge")
                    if brname == "private":
                        brname = virt_test_setup.PrivateBridgeConfig().brname
                    tapfd = virt_utils.open_tap("/dev/net/tun", ifname)
                    virt_utils.add_to_bridge(ifname, brname)
                    virt_utils.bring_up_ifname(ifname)
                    self.tapfds.append(tapfd)
                vlan += 1

            # Find available VNC port, if needed
            if params.get("display") == "vnc":
                self.vnc_port = virt_utils.find_free_port(5900, 6100)

            # Find available spice port, if needed
            if params.get("spice"):
                self.spice_port = virt_utils.find_free_port(8000, 8100)

            # Find available spice port
            if params.get("spice"):
                self.spice_port = virt_utils.find_free_port(8000, 8100)

            # Find random UUID if specified 'uuid = random' in config file
            if params.get("uuid") == "random":
                f = open("/proc/sys/kernel/random/uuid")
                self.uuid = f.read().strip()
                f.close()

            # Generate or copy MAC addresses for all NICs
            pa_type = params.get("pci_assignable")
            if pa_type == "no":
                num_nics = len(params.objects("nics"))
                for vlan in range(num_nics):
                    nic_name = params.objects("nics")[vlan]
                    nic_params = params.object_params(nic_name)
                    mac = (nic_params.get("nic_mac") or
                           mac_source and mac_source.get_mac_address(vlan))
                    if mac:
                        virt_utils.set_mac_address(self.instance, vlan, mac)
                    else:
                        virt_utils.generate_mac_address(self.instance, vlan)
            # Assign a PCI assignable device
            self.pci_assignable = None
            pa_type = params.get("pci_assignable")
            if pa_type and pa_type != "no":
                pa_devices_requested = params.get("devices_requested")

                # Virtual Functions (VF) assignable devices
                if pa_type == "vf":
                    self.pci_assignable = virt_utils.PciAssignable(
                        type=pa_type,
                        driver=params.get("driver"),
                        driver_option=params.get("driver_option"),
                        devices_requested=pa_devices_requested,
                        host_set_flag = params.get("host_setup_flag"),
                        kvm_params = params.get("kvm_default"))
                # Physical NIC (PF) assignable devices
                elif pa_type == "pf":
                    self.pci_assignable = virt_utils.PciAssignable(
                        type=pa_type,
                        names=params.get("device_names"),
                        devices_requested=pa_devices_requested,
                        host_set_flag = params.get("host_setup_flag"),
                        kvm_params = params.get("kvm_default"))
                # Working with both VF and PF
                elif pa_type == "mixed":
                    self.pci_assignable = virt_utils.PciAssignable(
                        type=pa_type,
                        driver=params.get("driver"),
                        driver_option=params.get("driver_option"),
                        names=params.get("device_names"),
                        devices_requested=pa_devices_requested,
                        host_set_flag = params.get("host_setup_flag"),
                        kvm_params = params.get("kvm_default"))
                else:
                    raise virt_vm.VMBadPATypeError(pa_type)

                self.pa_pci_ids = self.pci_assignable.request_devs()

                if self.pa_pci_ids:
                    logging.debug("Successfuly assigned devices: %s",
                                  self.pa_pci_ids)
                else:
                    raise virt_vm.VMPAError(pa_type)

            # Make qemu command
            qemu_command = self.__make_qemu_command()

            # Add migration parameters if required
            if migration_mode == "tcp":
                self.migration_port = virt_utils.find_free_port(5200, 6000)
                qemu_command += " -incoming tcp:0:%d" % self.migration_port
            elif migration_mode == "unix":
                self.migration_file = "/tmp/migration-unix-%s" % self.instance
                qemu_command += " -incoming unix:%s" % self.migration_file
            elif migration_mode == "exec":
                self.migration_port = virt_utils.find_free_port(5200, 6000)
                qemu_command += (' -incoming "exec:nc -l %s"' %
                                 self.migration_port)

            logging.info("Running qemu command:\n%s", qemu_command)
            self.process = aexpect.run_bg(qemu_command, None,
                                                 logging.info, "(qemu) ")
            for tapfd in self.tapfds:
                try:
                    os.close(tapfd)
                # File descriptor is already closed
                except OSError:
                    pass

            # Make sure the process was started successfully
            if not self.process.is_alive():
                e = virt_vm.VMCreateError(qemu_command,
                                          self.process.get_status(),
                                          self.process.get_output())
                self.destroy()
                raise e

            # Establish monitor connections
            self.monitors = []
            for monitor_name in params.objects("monitors"):
                monitor_params = params.object_params(monitor_name)
                # Wait for monitor connection to succeed
                end_time = time.time() + timeout
                while time.time() < end_time:
                    try:
                        if monitor_params.get("monitor_type") == "qmp":
                            if not virt_utils.has_option("qmp"):
                                break
                            # Add a QMP monitor
                            monitor = kvm_monitor.QMPMonitor(
                                monitor_name,
                                self.get_monitor_filename(monitor_name))
                        else:
                            # Add a "human" monitor
                            monitor = kvm_monitor.HumanMonitor(
                                monitor_name,
                                self.get_monitor_filename(monitor_name))
                        monitor.verify_responsive()
                        break
                    except kvm_monitor.MonitorError, e:
                        logging.warn(e)
                        time.sleep(1)
                else:
                    logging.error("Could not connect to monitor '%s'" %
                                  monitor_name)
                    self.destroy(gracefully=False)
                    raise e
                # Add this monitor to the list
                self.monitors += [monitor]

            # Get the output so far, to see if we have any problems with
            # KVM modules or with hugepage setup.
            output = self.process.get_output()

            if re.search("Could not initialize KVM", output, re.IGNORECASE):
                e = virt_vm.VMKVMInitError(qemu_command, self.process.get_output())
                self.destroy()
                raise e

            if "alloc_mem_area" in output:
                e = virt_vm.VMHugePageError(qemu_command, self.process.get_output())
                self.destroy()
                raise e

            logging.debug("VM appears to be alive with PID %s", self.get_pid())

            # Establish a session with the serial console -- requires a version
            # of netcat that supports -U
            self.serial_console = aexpect.ShellSession(
                "nc -U %s" % self.get_serial_console_filename(),
                auto_close=False,
                output_func=virt_utils.log_line,
                output_params=("serial-%s.log" % name,))

        finally:
            fcntl.lockf(lockfile, fcntl.LOCK_UN)
            lockfile.close()


    def destroy(self, gracefully=True, free_mac_addresses=True):
        """
        Destroy the VM.

        If gracefully is True, first attempt to shutdown the VM with a shell
        command.  Then, attempt to destroy the VM via the monitor with a 'quit'
        command.  If that fails, send SIGKILL to the qemu process.

        @param gracefully: If True, an attempt will be made to end the VM
                using a shell command before trying to end the qemu process
                with a 'quit' or a kill signal.
        @param free_mac_addresses: If True, the MAC addresses used by the VM
                will be freed.
        """
        try:
            # Is it already dead?
            if self.is_dead():
                return

            logging.debug("Destroying VM with PID %s...", self.get_pid())

            if gracefully and self.params.get("shutdown_command"):
                # Try to destroy with shell command
                logging.debug("Trying to shutdown VM with shell command...")
                try:
                    session = self.login()
                except (virt_utils.LoginError, virt_vm.VMError), e:
                    logging.debug(e)
                else:
                    try:
                        # Send the shutdown command
                        session.sendline(self.params.get("shutdown_command"))
                        logging.debug("Shutdown command sent; waiting for VM "
                                      "to go down...")
                        if virt_utils.wait_for(self.is_dead, 60, 1, 1):
                            logging.debug("VM is down")
                            return
                    finally:
                        session.close()

            if self.monitor:
                # Try to destroy with a monitor command
                logging.debug("Trying to kill VM with monitor command...")
                try:
                    self.monitor.quit()
                except kvm_monitor.MonitorError, e:
                    logging.warn(e)
                else:
                    # Wait for the VM to be really dead
                    if virt_utils.wait_for(self.is_dead, 5, 0.5, 0.5):
                        logging.debug("VM is down")
                        return

            # If the VM isn't dead yet...
            logging.debug("Cannot quit normally; sending a kill to close the "
                          "deal...")
            virt_utils.kill_process_tree(self.process.get_pid(), 9)
            # Wait for the VM to be really dead
            if virt_utils.wait_for(self.is_dead, 5, 0.5, 0.5):
                logging.debug("VM is down")
                return

            logging.error("Process %s is a zombie!", self.process.get_pid())

        finally:
            self.monitors = []
            if self.pci_assignable:
                self.pci_assignable.release_devs()
            if self.process:
                self.process.close()
            if self.serial_console:
                self.serial_console.close()
            for f in ([self.get_testlog_filename(),
                       self.get_serial_console_filename()] +
                      self.get_monitor_filenames()):
                try:
                    os.unlink(f)
                except OSError:
                    pass
            if hasattr(self, "migration_file"):
                try:
                    os.unlink(self.migration_file)
                except OSError:
                    pass
            if free_mac_addresses:
                num_nics = len(self.params.objects("nics"))
                for vlan in range(num_nics):
                    self.free_mac_address(vlan)


    @property
    def monitor(self):
        """
        Return the main monitor object, selected by the parameter main_monitor.
        If main_monitor isn't defined, return the first monitor.
        If no monitors exist, or if main_monitor refers to a nonexistent
        monitor, return None.
        """
        for m in self.monitors:
            if m.name == self.params.get("main_monitor"):
                return m
        if self.monitors and not self.params.get("main_monitor"):
            return self.monitors[0]

    @property
    def qmp_monitor(self):
        """
        Return the first QMP monitor.
        If no QMP monitor exist, return None.
        """
        for m in self.monitors:
            if isinstance(m, kvm_monitor.QMPMonitor):
                return m
        return None

    def get_monitor_filename(self, monitor_name):
        """
        Return the filename corresponding to a given monitor name.
        """
        return "/tmp/monitor-%s-%s" % (monitor_name, self.instance)


    def get_monitor_filenames(self):
        """
        Return a list of all monitor filenames (as specified in the VM's
        params).
        """
        return [self.get_monitor_filename(m) for m in
                self.params.objects("monitors")]


    def get_address(self, index=0):
        """
        Return the address of a NIC of the guest, in host space.

        If port redirection is used, return 'localhost' (the NIC has no IP
        address of its own).  Otherwise return the NIC's IP address.

        @param index: Index of the NIC whose address is requested.
        @raise VMMACAddressMissingError: If no MAC address is defined for the
                requested NIC
        @raise VMIPAddressMissingError: If no IP address is found for the the
                NIC's MAC address
        @raise VMAddressVerificationError: If the MAC-IP address mapping cannot
                be verified (using arping)
        """
        nics = self.params.objects("nics")
        nic_name = nics[index]
        nic_params = self.params.object_params(nic_name)
        if nic_params.get("nic_mode") == "tap":
            mac = self.get_mac_address(index).lower()
            # Get the IP address from the cache
            ip = self.address_cache.get(mac)
            if not ip:
                raise virt_vm.VMIPAddressMissingError(mac)
            # Make sure the IP address is assigned to this guest
            macs = [self.get_mac_address(i) for i in range(len(nics))]
            if not virt_utils.verify_ip_address_ownership(ip, macs):
                raise virt_vm.VMAddressVerificationError(mac, ip)
            return ip
        else:
            return "localhost"

    def get_macaddr(self, nic_index=0):
        """
        Return the macaddr of guest nic.

        @param nic_index: Index of the NIC
        """
        mac_filename = os.path.join(self.root_dir, "address_pool")
        mac_shelve = shelve.open(mac_filename, writeback=False)
        mac_pool = mac_shelve.get("macpool")
        val = "%s:%s" % (self.instance, nic_index)
        for key in mac_pool.keys():
            if val in mac_pool[key]:
                return key
        return None

    def get_port(self, port, nic_index=0):
        """
        Return the port in host space corresponding to port in guest space.

        @param port: Port number in host space.
        @param nic_index: Index of the NIC.
        @return: If port redirection is used, return the host port redirected
                to guest port port. Otherwise return port.
        @raise VMPortNotRedirectedError: If an unredirected port is requested
                in user mode
        """
        nic_name = self.params.objects("nics")[nic_index]
        nic_params = self.params.object_params(nic_name)
        if nic_params.get("nic_mode") == "tap":
            return port
        else:
            try:
                return self.redirs[port]
            except KeyError:
                raise virt_vm.VMPortNotRedirectedError(port)


    def get_peer(self, netid):
        """
        Return the peer of netdev or network deivce.

        @param netid: id of netdev or device
        @return: id of the peer device otherwise None
        """
        o = self.monitor.info("network")
        network_info = o
        if isinstance(o, dict):
            network_info = o.get["return"]

        netdev_peer_re = self.params.get("netdev_peer_re")
        if not netdev_peer_re:
            raise virt_vm.VMConfigMissingError(self.name, "netdev_peer_re")

        pairs = re.findall(netdev_peer_re, network_info, re.S)
        for nic, tap in pairs:
            if nic == netid:
                return tap
            if tap == netid:
                return nic

        return None


    def get_ifname(self, nic_index=0):
        """
        Return the ifname of a tap device associated with a NIC.

        @param nic_index: Index of the NIC
        """
        nics = self.params.objects("nics")
        try:
            nic_name = nics[nic_index]
        except IndexError:
            return "t%d-%s" % (nic_index, self.instance[-11:])
        nic_params = self.params.object_params(nic_name)
        if nic_params.get("nic_ifname"):
            return nic_params.get("nic_ifname")
        else:
            return "t%d-%s" % (nic_index, self.instance[-11:])


    def get_mac_address(self, nic_index=0):
        """
        Return the MAC address of a NIC.

        @param nic_index: Index of the NIC
        @raise VMMACAddressMissingError: If no MAC address is defined for the
                requested NIC
        """
        nic_name = self.params.objects("nics")[nic_index]
        nic_params = self.params.object_params(nic_name)
        mac = (nic_params.get("nic_mac") or
               virt_utils.get_mac_address(self.instance, nic_index))
        if not mac:
            raise virt_vm.VMMACAddressMissingError(nic_index)
        return mac


    def free_mac_address(self, nic_index=0):
        """
        Free a NIC's MAC address.

        @param nic_index: Index of the NIC
        """
        virt_utils.free_mac_address(self.instance, nic_index)


    def get_pid(self):
        """
        Return the VM's PID.  If the VM is dead return None.

        @note: This works under the assumption that self.process.get_pid()
        returns the PID of the parent shell process.
        """
        try:
            children = commands.getoutput("ps --ppid=%d -o pid=" %
                                          self.process.get_pid()).split()
            return int(children[0])
        except (TypeError, IndexError, ValueError):
            return None


    def get_shell_pid(self):
        """
        Return the PID of the parent shell process.

        @note: This works under the assumption that self.process.get_pid()
        returns the PID of the parent shell process.
        """
        return self.process.get_pid()


    def get_vnc_port(self):
        """
        Return self.vnc_port.
        """

        return self.vnc_port


    def get_shared_meminfo(self):
        """
        Returns the VM's shared memory information.

        @return: Shared memory used by VM (MB)
        """
        if self.is_dead():
            logging.error("Could not get shared memory info from dead VM.")
            return None

        filename = "/proc/%d/statm" % self.get_pid()
        shm = int(open(filename).read().split()[2])
        # statm stores informations in pages, translate it to MB
        return shm * 4.0 / 1024


    @error.context_aware
    def migrate(self, timeout=3600, protocol="tcp", cancel_delay=None,
                offline=False, stable_check=False, clean=True,
                save_path="/tmp", dest_host="localhost", remote_port=None):
        """
        Migrate the VM.

        If the migration is local, the VM object's state is switched with that
        of the destination VM.  Otherwise, the state is switched with that of
        a dead VM (returned by self.clone()).

        @param timeout: Time to wait for migration to complete.
        @param protocol: Migration protocol (as defined in MIGRATION_PROTOS)
        @param cancel_delay: If provided, specifies a time duration after which
                migration will be canceled.  Used for testing migrate_cancel.
        @param offline: If True, pause the source VM before migration.
        @param stable_check: If True, compare the VM's state after migration to
                its state before migration and raise an exception if they
                differ.
        @param clean: If True, delete the saved state files (relevant only if
                stable_check is also True).
        @save_path: The path for state files.
        @param dest_host: Destination host (defaults to 'localhost').
        @param remote_port: Port to use for remote migration.
        """
        if protocol not in self.MIGRATION_PROTOS:
            raise virt_vm.VMMigrateProtoUnsupportedError

        error.base_context("migrating '%s'" % self.name)

        def mig_finished():
            o = self.monitor.info("migrate")
            if isinstance(o, str):
                return "status: active" not in o
            else:
                return o.get("status") != "active"

        def mig_succeeded():
            o = self.monitor.info("migrate")
            if isinstance(o, str):
                return "status: completed" in o
            else:
                return o.get("status") == "completed"

        def mig_failed():
            o = self.monitor.info("migrate")
            if isinstance(o, str):
                return "status: failed" in o
            else:
                return o.get("status") == "failed"

        def mig_cancelled():
            o = self.monitor.info("migrate")
            if isinstance(o, str):
                return ("Migration status: cancelled" in o or
                        "Migration status: canceled" in o)
            else:
                return (o.get("status") == "cancelled" or
                        o.get("status") == "canceled")

        def wait_for_migration():
            if not virt_utils.wait_for(mig_finished, timeout, 2, 2,
                                      "Waiting for migration to complete"):
                raise virt_vm.VMMigrateTimeoutError("Timeout expired while waiting "
                                            "for migration to finish")

        local = dest_host == "localhost"

        clone = self.clone()
        if local:
            error.context("creating destination VM")
            if stable_check:
                # Pause the dest vm after creation
                extra_params = clone.params.get("extra_params", "") + " -S"
                clone.params["extra_params"] = extra_params
            clone.create(migration_mode=protocol, mac_source=self)
            error.context()

        try:
            if protocol == "tcp":
                if local:
                    uri = "tcp:localhost:%d" % clone.migration_port
                else:
                    uri = "tcp:%s:%d" % (dest_host, remote_port)
            elif protocol == "unix":
                uri = "unix:%s" % clone.migration_file
            elif protocol == "exec":
                uri = 'exec:nc localhost %s' % clone.migration_port

            if offline:
                self.monitor.cmd("stop")

            logging.info("Migrating to %s", uri)
            self.monitor.migrate(uri)

            if cancel_delay:
                time.sleep(cancel_delay)
                self.monitor.cmd("migrate_cancel")
                if not virt_utils.wait_for(mig_cancelled, 60, 2, 2,
                                          "Waiting for migration "
                                          "cancellation"):
                    raise virt_vm.VMMigrateCancelError("Cannot cancel migration")
                return

            wait_for_migration()

            # Report migration status
            if mig_succeeded():
                logging.info("Migration completed successfully")
            elif mig_failed():
                raise virt_vm.VMMigrateFailedError("Migration failed")
            else:
                raise virt_vm.VMMigrateFailedError("Migration ended with "
                                                   "unknown status")

            # Switch self <-> clone
            temp = self.clone(copy_state=True)
            self.__dict__ = clone.__dict__
            clone = temp

            # From now on, clone is the source VM that will soon be destroyed
            # and self is the destination VM that will remain alive.  If this
            # is remote migration, self is a dead VM object.

            error.context("after migration")
            if local:
                time.sleep(1)
                self.verify_alive()

            if local and stable_check:
                try:
                    save1 = os.path.join(save_path, "src-" + clone.instance)
                    save2 = os.path.join(save_path, "dst-" + self.instance)
                    clone.save_to_file(save1)
                    self.save_to_file(save2)
                    # Fail if we see deltas
                    md5_save1 = utils.hash_file(save1)
                    md5_save2 = utils.hash_file(save2)
                    if md5_save1 != md5_save2:
                        raise virt_vm.VMMigrateStateMismatchError(md5_save1,
                                                                  md5_save2)
                finally:
                    if clean:
                        if os.path.isfile(save1):
                            os.remove(save1)
                        if os.path.isfile(save2):
                            os.remove(save2)

        finally:
            # If we're doing remote migration and it's completed successfully,
            # self points to a dead VM object
            if self.is_alive():
                self.monitor.cmd("cont")
            clone.destroy(gracefully=False)


    @error.context_aware
    def reboot(self, session=None, method="shell", nic_index=0, timeout=240):
        """
        Reboot the VM and wait for it to come back up by trying to log in until
        timeout expires.

        @param session: A shell session object or None.
        @param method: Reboot method.  Can be "shell" (send a shell reboot
                command) or "system_reset" (send a system_reset monitor command).
        @param nic_index: Index of NIC to access in the VM, when logging in
                after rebooting.
        @param timeout: Time to wait for login to succeed (after rebooting).
        @return: A new shell session object.
        """
        error.base_context("rebooting '%s'" % self.name, logging.info)
        error.context("before reboot")
        session = session or self.login()
        error.context()

        if method == "shell":
            session.sendline(self.params.get("reboot_command"))
        elif method == "system_reset":
            # Clear the event list of all QMP monitors
            qmp_monitors = [m for m in self.monitors if m.protocol == "qmp"]
            for m in qmp_monitors:
                m.clear_events()
            # Send a system_reset monitor command
            self.monitor.cmd("system_reset")
            # Look for RESET QMP events
            time.sleep(1)
            for m in qmp_monitors:
                if m.get_event("RESET"):
                    logging.info("RESET QMP event received")
                else:
                    raise virt_vm.VMRebootError("RESET QMP event not received "
                                                "after system_reset "
                                                "(monitor '%s')" % m.name)
        else:
            raise virt_vm.VMRebootError("Unknown reboot method: %s" % method)

        error.context("waiting for guest to go down", logging.info)
        if not virt_utils.wait_for(lambda:
                                  not session.is_responsive(),
                                  120, 0, 1):
            raise virt_vm.VMRebootError("Guest refuses to go down")
        session.close()
        if self.params.get("mac_changeable") == "yes":
            virt_test_utils.update_mac_ip_address(self, self.params)

        error.context("logging in after reboot", logging.info)
        return self.wait_for_login(nic_index, timeout=timeout)


    def send_key(self, keystr):
        """
        Send a key event to the VM.

        @param: keystr: A key event string (e.g. "ctrl-alt-delete")
        """
        # For compatibility with versions of QEMU that do not recognize all
        # key names: replace keyname with the hex value from the dict, which
        # QEMU will definitely accept
        dict = {"comma": "0x33",
                "dot":   "0x34",
                "slash": "0x35"}
        for key, value in dict.items():
            keystr = keystr.replace(key, value)
        self.monitor.sendkey(keystr)
        time.sleep(0.2)


    # should this really be expected from VMs of all hypervisor types?
    def screendump(self, filename):
        try:
            if self.monitor:
                self.monitor.screendump(filename=filename)
        except kvm_monitor.MonitorError, e:
            logging.warn(e)


    def save_to_file(self, path):
        """
        Save the state of virtual machine to a file through migrate to
        exec
        """
        # Make sure we only get one iteration
        self.monitor.cmd("migrate_set_speed 1000g")
        self.monitor.cmd("migrate_set_downtime 100000000")
        self.monitor.migrate("exec:cat>%s" % path)
        # Restore the speed and downtime of migration
        self.monitor.cmd("migrate_set_speed %d" % (32<<20))
        self.monitor.cmd("migrate_set_downtime 0.03")


    def needs_restart(self, name, params, basedir):
        """
        Verifies whether the current qemu commandline matches the requested
        one, based on the test parameters.
        """
        return (self.__make_qemu_command() !=
                self.__make_qemu_command(name, params, basedir))
