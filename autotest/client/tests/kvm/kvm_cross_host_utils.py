#!/usr/bin/python
"""
Utility classes and functions to handle cross host tests.

@copyright: 2010 Red Hat Inc.
"""

import time, socket, logging, commands, os
import select, threading
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_utils, kvm_vm
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpclib

def local_prepare_nfs_server(dir_dict, client='*', args="no_root_squash,async"):
    # first, start nfs serivce.
    commands.getoutput("service nfs restart")
    exportfs_cmd = "/usr/sbin/exportfs"
    for d in dir_dict.keys():
        d_args = ' '.join([dir_dict[d][1], args])
        if not ':' in d:
            cmd = "%s -io %s %s:%s" % (exportfs_cmd, d_args, client, d)
            commands.getoutput(cmd)
    logging.info(commands.getoutput("/usr/sbin/exportfs"))

def test_init(test, params, env):
    """
    Try to setup cross_host test environment.
    this func needs items in 'params':
    'login_timeout' 'listen_ip' 'listen_port' 'dsthost'
    'slaver_peer' 'remote_test'

    @return remote_host: RemoteHost object.
            xmlrpc_server: XMLRPC Server.
    """
    login_timeout = int(params.get("login_timeout"))
    listen_ip = params.get("listen_ip")

    dsthost = params.get("dsthost")
    if dsthost == '':
        raise error.TestError("Can't get remote host ip address.")

    if params.get("slaver_peer") == "yes":
        listen_port = int(params.get("listen_port"))
    else:
        # generate listen_port on srchost.
        listen_port = virt_utils.find_free_port(32000, 33000)
        for i in xrange(1, 10):
            if virt_utils.is_port_free(listen_port, dsthost):
                break
            listen_port = virt_utils.find_free_port(listen_port + i, 33000)
        else:
            raise error.TestError("Could not find a free port"
                                  " for xmlrpc server.")

    xmlrpc_server = None
    if listen_ip and listen_port:
        xmlrpc_server = ServerSideUtils(params, env, listen_ip, listen_port)

    params["test_bindir"] = test.bindir
    remote_host = RemoteHost(dsthost, params, listen_port, login_timeout)

    link_dict = {"/usr/libexec/qemu-kvm": "/usr/bin/qemu-kvm",
                 "/usr/bin/qemu-kvm": test.bindir + "/qemu",
                 "/usr/bin/qemu-img": test.bindir + "/qemu-img",
                 "/home/kvm_autotest_root/images": test.bindir + "/images",
                 "/home/kvm_autotest_root/iso": test.bindir + "/isos"}
    mount_dict = {"/home/kvm_autotest_root/images": ['', "ro"],
            params.get("nfs_iso"): ["/home/kvm_autotest_root/iso", "ro"]}

    if params.get("slaver_peer") == "yes":
        # This part executes on 'dsthost'.
        logging.info("Trying to mount remote fs via NFS.")
        for d in mount_dict.keys():
            host = params.get("dsthost")
            root_dir = d
            if ':' in d:
                host, root_dir = d.split(':')
            mount_point = mount_dict[d][0]
            if mount_point == '':
                mount_point = root_dir
            if not os.path.exists(mount_point):
                utils.system("mkdir -p %s" % mount_point)
            mount_args = mount_dict[d][1]
            remote_host.mount_nfs_fs(host, root_dir, mount_point, mount_args)
        logging.info("Trying to prepare symbolic link.")
        for link in link_dict.keys():
            if not os.path.exists(link_dict[link]):
                utils.system("ln -sf %s %s" % (link, link_dict[link]))
    else:
        logging.info("Preparing NFS server for remote host.")
        local_prepare_nfs_server(mount_dict)

        if params.get("remote_test", "yes") == "yes":
            logging.info("Trying to start autotest on remote host.")
            from autotest_lib.client.virt.tests import autotest
            autotest.run_autotest_background(test, params, env,
                                test_name=None,
                                test_control_file=None,
                                machine=remote_host, kvm_test=True)

    if xmlrpc_server:
        logging.info("Trying to connect to remote XMLRPC server.")
        success = virt_utils.wait_for(remote_host.is_controller_ready,
                                        login_timeout)
        if not success:
            raise error.TestError("Can't connect to remote XMLRPC server, "
                                  "abord test.")
        logging.info("Connected to XMLRPC server.")

    return (remote_host, xmlrpc_server)

def test_finish(remote_host, xmlrpc_server, timeout):
    if remote_host:
        remote_host.shutdown_xmlrpc_server()
    if xmlrpc_server:
        logging.info("waiting server thread finish.")
        ret = virt_utils.wait_for(lambda: not xmlrpc_server.is_alive(), timeout)
        if ret is None:
            logging.info("Timeout elapsed, stop local XMLRPC server.")
            xmlrpc_server.shutdown_xmlrpc_server()

def start_vms(test, params, env):
    from autotest_lib.client.virt import virt_env_process
    params["start_vm"] = "yes"
    for vm in params.get("vms").split():
        virt_env_process.preprocess_vm(test, params, env, vm)

class XMLRPCServer(SimpleXMLRPCServer):
    """
    XMLRPC Server.
    """
    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                logRequests=1):
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests)
        self.__is_shut_down = threading.Event()
        self.__serving = False

    def serve_forever(self, poll_interval=0.5):
        """Handle one request at a time until shutdown.

        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """
        self.__serving = True
        self.__is_shut_down.clear()
        while self.__serving:
            # XXX: Consider using another file descriptor or
            # connecting to the socket to wake this up instead of
            # polling. Polling reduces our responsiveness to a
            # shutdown request and wastes cpu at all other times.
            r, w, e = select.select([self], [], [], poll_interval)
            if r:
                self._handle_request_noblock()
        self.__is_shut_down.set()

    def _handle_request_noblock(self):
        """Handle one request, without blocking.

        I assume that select.select has returned that the socket is
        readable before this function was called, so there should be
        no risk of blocking in get_request().
        """
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except:
                self.handle_error(request, client_address)
                self.close_request(request)

    def shutdown(self):
        """Stops the serve_forever loop.

        Blocks until the loop has finished. This must be called while
        serve_forever() is running in another thread, or it will
        deadlock.
        """
        self.__serving = False
        self.__is_shut_down.wait()


class ServerSideUtils:
    # Server-side functions.
    def __init__(self, params, env, listen_ip, listen_port):
        self.params = params
        self.env = env
        try:
            logging.info("Setup a XMLRPC server.")
            self._xmlrpc_server = XMLRPCServer((listen_ip, listen_port),
                                        logRequests=False)
            self._xmlrpc_server.register_introspection_functions()
            # start a thread for XMLRPC server.
            self._server_thread = threading.Thread(
                            target=self._xmlrpc_server.serve_forever)
            self._server_thread.start()
        except:
            logging.error("Start XMLRPC server failed.")
            raise

        # register all functions for this test.
        logging.debug("register functions to XMLRPC server.")
        for func_name in [f for f in dir(self) if 'export_' in f]:
            name = func_name.split("export_")[1]
            func = getattr(self, func_name)
            self._xmlrpc_server.register_function(func, name)

        logging.debug("exported functions: %s",
                    str(self._xmlrpc_server.system_listMethods()))

    class MacSource:
        """
        Hack for copying mac address during VM clone.
        """
        def __init__(self, macs):
            self.macs = macs

        def get_mac_address(self, nic_index=0):
            return self.macs[nic_index]

    def is_alive(self):
        return self._server_thread.isAlive()

    def shutdown_xmlrpc_server(self):
        self._xmlrpc_server.shutdown()

    def export_server_ready(self):
        """
        Check whether server is ready. Just return True now.
        """
        return True

    def export_get_params(self):
        return self.params

    def export_shutdown_xmlrpc_server(self, timeout=2):
        """
        Stop XMLRPC server. Always return True.

        @param timeout: timeout before really stop server.
        """
        def _stop():
            time.sleep(timeout)
            self._xmlrpc_server.shutdown()
            logging.info("XMLRPC server stoped.")
        t = threading.Thread(target=_stop)
        t.start()
        return True

    def export_get_vms_list(self):
        """
        Return the guest(s) list of the host.
        """
        return self.params.get("vms").split()

    def export_is_vm_alive(self, vm_name):
        vm = env.get_vm(vm_name)
        if vm and vm.is_alive():
            return True
        return False

    def export_get_vm_mac_address(self, vm_name, nic_index=0):
        """
        Return the mac address of a NIC of the guest.

        @param vm_name: Name of the guest whose address is requested.
        @param nic_index: Index of the NIC whose address is requested.
        """
        vm = env.get_vm(vm_name)
        mac = vm.get_mac_address(nic_index)
        if mac is None:
            mac = "None"
        return mac

    def export_get_vm_address(self, vm_name, nic_index=0):
        """
        Return the address of a NIC of the guest, in host space.

        @param vm_name: Name of the guest whose address is requested.
        @param nic_index: Index of the NIC whose address is requested.
        """
        #XXX: If the guest is using private bridge, we can't
        #     get currect ip address with this method. need impovement.
        vm = virt_test_utils.get_living_vm(self.env, vm_name)
        addr = vm.get_address(nic_index)
        if addr is None:
            return "None"

        return addr

    def export_get_vm_nic_mode(self, vm_name, nic_index):
        """
        Return the nic mode of a guest.

        @param vm_name: Name of the guest.
        @param nic_index: Index of NIC.
        """
        nic_name = virt_utils.get_sub_dict_names(self.params,
                                                "nics")[nic_index]
        nic_params = virt_utils.get_sub_dict(self.params, nic_name)
        mode = nic_params.get("nic_mode")
        if mode != '':
            return nic_params.get("nic_mode")
        return "None"

    def export_get_vm_port(self, vm_name, port, nic_index=0):
        """
        Return the port in host space corresponding to port in guest space.

        @param vm_name: Name of the guest.
        @param port: Port number in host space.
        @param nic_index: Index of the NIC.
        @return: If port redirection is used, return the host port redirected
                to guest port port. Otherwise return port.
        """
        vm = virt_test_utils.get_living_vm(self.env, vm_name)
        p = vm.get_port(port, nic_index)
        return p

    def export_get_vm_command_status_output(self, vm_name, cmd, timeout):
        """
        Send a command and return its exit status and output.

        @param vm_name: Name of the guest.
        @param cmd: Command to send (must not contain newline characters)
        @param timeout: The duration (in seconds) to wait until a match is
                found

        @return: A tuple (status, output) where status is the exit status or
                None if no exit status is available (e.g. timeout elapsed), and
                output is the output of command.
        """
        vm = self.env.get_vm(vm_name)
        vm.verify_alive()
        session = vm.wait_for_login(timeout=timeout)

        if not session:
            return (None, None)
        ret = session.get_command_status_output(cmd)
        session.close()
        logging.debug("command return %d, output: %s", ret[0], ret[1])
        return ret

    def export_get_vm_command_output(self, vm_name, cmd, timeout):
        """
        Send a command and return its output.

        @param vm_name: Name of the guest.
        @param cmd: Command to send
        @param timeout: The duration (in seconds) to wait until a match is
                found
        """
        _, o = self.export_get_vm_command_status_output(vm_name, cmd, timeout)
        return o

    def export_get_vm_command_status(self, vm_name, cmd, timeout):
        """
        Send a command and return its exit status.

        @param vm_name: Name of the guest.
        @param cmd: Command to send
        @param timeout: The duration (in seconds) to wait until a match is
                found

        @return: Exit status or -1 if no exit status is available (e.g.
                timeout elapsed).
        """
        s, _ = self.export_get_vm_command_status_output(vm_name, cmd, timeout)
        if s is None:
            return -1
        return s

    def export_check_vm_ssh_ready(self, vm_name):
        """
        Check sshd of the guest is ready for serve.

        @param vm_name: Name of the guest.
        """
        try:
            vm = virt_test_utils.get_living_vm(self.env, vm_name)
        except:
            return False

        session = vm.wait_for_login(timeout=360)
        if session:
            logging.debug("guest is ready.")
            session.close()
            return True
        else:
            logging.debug("Emmm, you should wait for a second.")
            session.close()
            return False

    def export_get_vm_monitors(self, vm_name):
        logging.debug("Try to get monitors of vm %s", vm_name)
        vm = self.env.get_vm(vm_name)
        if not vm:
            logging.error("Could not find vm %s in env.", vm_name)
            return "None"
        monitors = []
        for m in vm.monitors:
            monitors.append(m.name)
        return monitors

    def _get_monitor_by_name(self, vm_name, monitor_name):
        logging.debug("Try to get monitor %s of vm %s", monitor_name, vm_name)
        try:
            vm = self.env.get_vm(vm_name)
        except:
            logging.error("Could not find vm %s in env", vm_name)
        else:
            for m in vm.monitors:
                if m.name == monitor_name:
                    return m
        logging.error("Could not find monitor %s in vm %s",
                      monitor_name, vm_name)

    def export_monitor_cmd(self, vm_name, monitor_name, cmd, timeout):
        logging.debug("Run cmd %s via %s of vm %s", cmd, monitor_name, vm_name)
        monitor = self._get_monitor_by_name(vm_name, monitor_name)
        if monitor:
            ret = monitor.cmd(cmd, timeout)
            if ret is None:
                ret = "None"
            return ret

        return False

    def export_monitor_is_responsive(self, vm_name, monitor_name):
        monitor = self._get_monitor_by_name(vm_name, monitor_name)
        if monitor:
            return monitor.is_responsive()
        return False

    def export_monitor_migrate(self, vm_name, monitor_name, uri, full_copy,
                               incremental_copy, wait):
        logging.debug("Migrating vm %s ...", vm_name)
        monitor = self._get_monitor_by_name(vm_name, monitor_name)
        if monitor and monitor.is_responsive():
            return monitor.migrate(uri, full_copy, incremental_copy, wait)

        return False

    def export_set_vm_property(self, vm_name, property_name, value):
        if value == "None":
            value = None
        vm = self.env.get_vm(vm_name)
        if not vm:
            logging.error("Could not find vm %s in env.", vm_name)
            return False
        if property_name in dir(vm):
            vm.__dict__[property_name] = value
            return True
        return False

    def export_update_vm_address_cache(self, vm_name, address_cache):
        vm = self.env.get_vm(vm_name)
        if not vm:
            logging.error("Could not find vm %s in env.", vm_name)
            return False
        vm.address_cache.update(address_cache)
        return True

    def export_get_vm_property(self, vm_name, property_name):
        vm = self.env.get_vm(vm_name)
        if not vm:
            logging.error("Could not find vm %s in env.", vm_name)
            return "None"
        return getattr(vm, property_name)

    def export_create_vm(self, name, params, root_dir, timeout, migration_mode,
                         migration_exec_cmd, mac_source):
        logging.debug("Create vm %s in local host.", name)

        if migration_mode == "None": migration_mode = None
        if migration_exec_cmd == "None": migration_exec_cmd = None
        if mac_source == "None":
            mac_source = None
        else:
            mac_source = self.MacSource(mac_source)

        vm = self.env.get_vm(name)
        if not vm:
            logging.error("Could not find vm %s in env.", name)
            return False
        return vm.create(name, vm.params, root_dir, timeout, migration_mode,
                         migration_exec_cmd, mac_source)

    def export_destroy_vm(self, name, gracefully=True, free_mac_addresses=True):
        vm = self.env.get_vm(name)
        if not vm:
            logging.error("Could not find vm %s in env.", name)
            return False
        vm.destroy(gracefully, free_mac_addresses)
        return True

    def export_clone_vm(self, name, params, root_dir, address_cache):
        logging.debug("clone vm %s in local host.", name)
        return kvm_vm.VM(name, params, root_dir, address_cache)


class RemoteHost(kvm_vm.VM):
    """
    This class handles basic Remote Host operations.
    With this class, we can operate remote host like a VM.
    """
    def __init__(self, address, params, xmlrpc_port=None, timeout=360):
        """

        @param address:     ip address of remote host.
        @param xmlrpc_port: port of XMLRPC server on remote host.
                            NOTE: RemoteHost object could be initiated without
                            xmlrpc, but some method of it will raise a
                            exception if 'self.controller' is None.
        @param params:      Dict for test parameters.
                            NOTE: Keep it! some methods for VM need it.
        @param timeout:     timeout for remote connection.
        """
        self.name = address
        self.address = address
        self.params = params
        self.test_bindir = params.get("test_bindir")
        if xmlrpc_port is not None:
            self.init_controller(xmlrpc_port)
        self.timeout = timeout

    def init_controller(self, xmlrpc_port):
        self.controller = xmlrpclib.ServerProxy("http://%s:%d" %
                                        (self.address, xmlrpc_port))

    def make_qemu_command(self, name=None, params=None, root_dir=None):
        logging.warn("This function is not support now.")

    def is_controller_ready(self):
        try:
            # Check if remote XMLRPC server is ready.
            if self.controller.server_ready(): return True
        except: return False

    def wait_for_controller_ready(self):
        if self.controller is None:
            raise error.TestError("XMLRPC client could not be None before you"
                                  "call this method.")
        return virt_utils.wait_for(self.is_controller_ready, self.timeout)

    def get_params(self):
        logging.debug("Try to get params of remote host %s",
                    self.address)
        if self.controller is None:
            raise error.TestError("XMLRPC client could not be None before you"
                                  "call this method.")
        self.wait_for_controller_ready()
        return virt_utils.wait_for(self.controller.get_params, self.timeout)

    def get_vms_list(self):
        logging.debug("Getting remote vm list.")
        if self.controller is None:
            raise error.TestError("XMLRPC client could not be None before you"
                                  "call this method.")
        remote_vm_list = []
        vms_list = virt_utils.wait_for(self.controller.get_vms_list,
                                    self.timeout)
        for vm in vms_list:
            remote_vm_list.append(RemoteVM(self, vm, self.timeout))
        logging.debug("remote_vm_list %s", str(remote_vm_list))
        return remote_vm_list

    def shutdown_xmlrpc_server(self):
        logging.info("Shutting down remote XMLRPC server.")
        if self.controller is None:
            raise error.TestError("XMLRPC client could not be None before you"
                                  "call this method.")
        virt_utils.wait_for(self.controller.shutdown_xmlrpc_server,
                        self.timeout)

    def is_alive(self):
        session = self.remote_login()
        if session:
            session.close()
            return True
        else:
            return False

    def get_address(self, nic_index=0):
        return self.address

    def get_port(self, port, nic_index=0):
        return "22"

    def mount_nfs_fs(self, host, root_dir, mount_point, args=None):
        logging.debug("mount_nfs_fs: host: %s, root_dir: %s, mount_point: %s,"
                      "args: %s" % (host, root_dir, mount_point, args))
        if args:
            o = commands.getoutput("mount -o %s %s:%s %s" % (args, host,
                                root_dir, mount_point))
        else:
            o = commands.getoutput("mount %s:%s %s" % (host, root_dir,
                                mount_point))
        logging.debug("mount cmd returns %s", str(o))

    def migrate(self, vm, mig_timeout=3600, mig_protocol="tcp",
                during_migrate=[]):
        """
        Migrate to remote host.

        @param vm:           VM to migration on local host.
        @param mig_timeout:  timeout for migration.
        @param mig_protocol: migration protocol.
        @param during_migrate:  list of functions running during migration.

        @return new VM.
        """
        #XXX: lots of duplication with kvm_test_utils.migrate, need merge to it
        def mig_finished():
            try:
                o = vm.monitor.info("migrate")
                logging.debug("%s", o)
                if isinstance(o, str):
                    return "status: active" not in o
                else:
                    return o.get("status") != "active"
            except:
                pass

        def mig_succeeded():
            o = vm.monitor.info("migrate")
            if isinstance(o, str):
                return "status: completed" in o
            else:
                return o.get("status") == "completed"

        def mig_failed():
            o = vm.monitor.info("migrate")
            if isinstance(o, str):
                return "status: failed" in o
            else:
                return o.get("status") == "failed"

        def mig_cancelled():
            o = vm.monitor.info("migrate")
            if isinstance(o, str):
                return ("Migration status: cancelled" in o or
                        "Migration status: canceled" in o)
            else:
                return (o.get("status") == "cancelled" or
                        o.get("status") == "canceled")

        def wait_for_migration():
            if not virt_utils.wait_for(mig_finished, mig_timeout, 2, 2,
                                      "Waiting for migration to finish..."):
                raise error.TestFail("Timeout expired while waiting for migration "
                                     "to finish")

        dest_vm = RemoteVM(self, vm.name)
        dest_vm.update_address_cache(vm.address_cache)
        if mig_protocol == "exec":
            exec_file = "/tmp/exec-%s.gz" % virt_utils.generate_random_string(8)
            exec_cmd = "gzip -c -d %s" % exec_file
            uri = '"exec:gzip -c > %s"' % exec_file
            try:
                vm.monitor.cmd("stop")
                vm.monitor.migrate(uri)
                # run some functions during migration.
                for f in during_migrate:
                    f()
                wait_for_migration()

                # copy exec file to remote host.
                if self.copy_files_to(exec_file, exec_file):
                    ret = dest_vm.create(migration_mode=mig_protocol,
                                   migration_exec_cmd=exec_cmd, mac_source=vm)
                    if not ret:
                        raise error.TestError("Could not create dest VM")
            finally:
                logging.debug("Removing migration file %s", exec_file)
                try:
                    os.remove(exec_file)
                except OSError:
                    pass
        elif mig_protocol == "tcp":
            ret = dest_vm.create(migration_mode=mig_protocol, mac_source=vm)
            if not ret:
                raise error.TestError("Could not create dest VM")
            try:
                uri = "tcp:%s:%d" % (self.address, dest_vm.migration_port)
                vm.monitor.migrate(uri)
                # run some function during migration.
                for f in during_migrate:
                    f()
                wait_for_migration()
            except:
                dest_vm.destroy()
                raise
        else:
            raise error.TestError("Unsupported migration type: %s"
                                  % mig_protocol)

        # Report migration status
        if mig_succeeded():
            logging.info("Migration finished successfully")
        elif mig_failed():
            raise error.TestFail("Migration failed")
        else:
            raise error.TestFail("Migration ended with unknown status")

        if dest_vm.monitor.is_responsive():
            if "paused" in dest_vm.monitor.info("status"):
                logging.debug("Destination VM is paused, resuming it...")
                dest_vm.monitor.cmd("cont")

        # Kill the source VM
        vm.destroy(gracefully=False, free_mac_addresses=False)

        # Return the new cloned VM
        return dest_vm

class RemoteVM(kvm_vm.VM):
    """
    This class handles basic Remote VM operations.
    With this class, we can operate remote host like a VM.
    """
    def __init__(self, host, name, timeout=None):
        """

        @param host:    'RemoteHost' object which this VM runs on.
        @param name:     this VM's name.
        @param timeout:  timeout for remote connection to this VM.
        """
        self.process = None
        self.serial_console = None
        self.redirs = None
        self.monitors = []
        self.pci_assignable = None
        self.netdev_id = []
        self.uuid = None

        self.vnc_port = 5900
        self.spice_port = 8000
        self.host = host
        self.name = name
        if timeout is None:
            self.timeout = host.timeout
        else:
            self.timeout = timeout
        # here we should get remote params
        self.params = self.host.get_params()
        self.root_dir = self.host.test_bindir
        self.address_cache = None
        self.migration_port = None

    def make_qemu_command(self, name=None, params=None, root_dir=None):
        logging.warn("This function is not support for remote VM.")

    def get_mac_address(self, nic_index=0):
        logging.debug("Trying to get mac address, NIC %d, guest %s(@%s)",
                    nic_index, self.name, self.host.address)
        self.host.wait_for_controller_ready()
        func = lambda: self.host.controller.get_vm_mac_address(self.name,
                                                               nic_index)
        mac = virt_utils.wait_for(func, self.timeout)
        if mac == 'None':
            raise error.TestFail("Could not get mac address, guest %s(@%s)" % \
                                 (self.name, self.host.address))
        logging.debug("guest mac address is %s", mac)

        return mac


    def get_address(self, nic_index=0):
        logging.debug("Try to get ip address of %s(@%s), timeout %ds",
                    self.name, self.host.address, self.timeout)
        self.host.wait_for_controller_ready()
        func = lambda: self.host.controller.get_vm_address(self.name)
        address = virt_utils.wait_for(func, self.timeout)
        if address == "None":
            return None
        logging.debug("guest ip address is %s", address)

        return address

    def set_property(self, property_name, value):
        logging.debug("Try to set remote VM property %s to %s",
                      property_name, value)
        if value is None:
            value = "None"
        self.host.wait_for_controller_ready()
        c = self.host.controller
        func = lambda: c.set_vm_property(self.name, property_name, value)
        ret = virt_utils.wait_for(func, self.timeout)
        if ret:
            self.__dict__[property_name] = value
        return ret

    def update_address_cache(self, address_cache):
        logging.debug("Try to set remote VM address_cache to %s",
                      address_cache)
        if address_cache is None:
            return True
        self.host.wait_for_controller_ready()
        c = self.host.controller
        func = lambda: c.update_vm_address_cache(self.name, address_cache)
        ret = virt_utils.wait_for(func, self.timeout)
        if ret:
            self.address_cache = address_cache
        return ret

    def get_property(self, property_name):
        logging.debug("Try to get remote guest property %s", property_name)
        self.host.wait_for_controller_ready()
        c = self.host.controller
        func = lambda: c.get_vm_property(self.name, property_name)
        ret = virt_utils.wait_for(func, self.timeout)
        if ret == "None":
            ret = None
        self.__dict__[property_name] = ret
        return ret

    def _get_monitors(self):
        """
        Get monitors of a VM via xmlrpc, and convert them to RemoteMonitor.
        """
        self.host.wait_for_controller_ready()
        func = lambda: self.host.controller.get_vm_monitors(self.name)
        monitors = virt_utils.wait_for(func, self.timeout)
        if monitors == "None":
            return

        self.monitors = []
        for m in monitors:
            remote_monitor = RemoteMonitor(self, m, self.timeout)
            self.monitors.append(remote_monitor)

    @property
    def monitor(self):
        """
        Return RemoteMonitor object, if main_monitor isn't defined,
        return the first monitor.
        """
        self._get_monitors()
        for m in self.monitors:
            if m.name == self.params.get("main_monitor"):
                return m
        if self.monitors and not self.params.get("main_monitor"):
            return self.monitors[0]

    def is_alive(self):
        logging.debug("Try to check remote vm %s(@%s)is alive.", self.name,
                    self.host.address)
        self.host.wait_for_controller_ready()
        return virt_utils.wait_for(
                        lambda: self.host.controller.is_vm_alive(self.name),
                        self.timeout)

    def wait_for_ssh_ready(self):
        logging.info("Wait until sshd ready on remote guest.")
        session = virt_utils.wait_for(self.remote_login, self.timeout)
        if session:
            session.close()

    def copy_files_to(self, local_path, remote_path, nic_index=0,
                            timeout=600):
        logging.debug("Copy file to remote VM %s(@%s)", self.name,
                    self.host.name)
        self.wait_for_ssh_ready()
        return super(RemoteVM, self).copy_files_to(local_path, remote_path,
                                                nic_index, timeout)

    def copy_files_from(self, remote_path, local_path,
                        nic_index=0, timeout=600):
        self.wait_for_ssh_ready()
        return super(RemoteVM, self).copy_files_from(remote_path, local_path,
                                                    nic_index, timeout)

    def create(self, name=None, params=None, root_dir=None, timeout=5.0,
               migration_mode=None, migration_exec_cmd=None, mac_source=None):

        if name: self.name = name
        else: name = self.name

        if params: self.params = params
        else: params = self.params

        if root_dir: self.root_dir = root_dir
        else: root_dir = self.root_dir

        if not migration_mode: migration_mode = "None"
        if not migration_exec_cmd: migration_exec_cmd = "None"
        if not mac_source:
            macs = "None"
        else:
            # 'kvm_vm.create()' nees mac_source is a vm object.  # but
            # 'vm.get_mac_address()' depends on address_pool file in local
            # host, it can't be copyed to remote host. just use a wrapper
            # class provide a 'get_mac_address()' to cheat 'kvm_vm.create()'
            macs = []
            num_nics = len(virt_utils.get_sub_dict_names(params, "nics"))
            for nic in range(num_nics):
                mac = mac_source.get_mac_address(nic)
                macs.append(mac)

        logging.info("Creating VM %s(@%s)", name, self.host.name)
        self.host.wait_for_controller_ready()
        c = self.host.controller
        func = lambda: c.create_vm(name, params, root_dir, timeout,
                                   migration_mode, migration_exec_cmd, macs)
        ret =  virt_utils.wait_for(func, self.timeout)
        if ret:
            self.instance = self.get_property("instance")
            if migration_mode == "tcp":
                # migration port is generated in 'kvm_vm.create()', we can only
                # get this parameter after remote vm created.
                self.migration_port = self.get_property("migration_port")
        return ret

    def destroy(self, gracefully=True, free_mac_addresses=True):
        logging.info("Destroying remote VM %s(@%s)", self.name, self.host.name)
        self.host.wait_for_controller_ready()
        func = lambda: self.host.controller.destroy_vm(self.name, gracefully,
                                                       free_mac_addresses)
        virt_utils.wait_for(func, self.timeout)

    def clone(self, name=None, params=None, root_dir=None,
              address_cache=None):
        if name is None:
            name = self.name
        if params is None:
            params = self.params
        if root_dir is None:
            root_dir = self.root_dir
        if address_cache is None:
            address_cache = self.address_cache
        logging.info("cloning remote vm %s(@%s) to local %s",
                     self.name, self.host.name, name)
        new_vm = kvm_vm.VM(name, params, root_dir, address_cache)
        new_vm.instance = self.instance
        return new_vm

class RemoteMonitor(object):
    def __init__(self, vm, name, timeout):
        self.vm = vm
        self.name = name
        self.timeout = timeout

    def __del__(self):
        pass

    def is_responsive(self):
        self.vm.host.wait_for_controller_ready()
        c = self.vm.host.controller
        func = lambda: c.monitor_is_responsive(self.vm.name, self.name)
        return virt_utils.wait_for(func, self.timeout)

    def info(self, what):
        return self.cmd("info %s" % what)

    def cmd(self, cmd, timeout=20):
        logging.debug("Sending monitor cmd '%s' to %s(@%s)", cmd,
                      self.vm.name, self.vm.host.address)
        self.vm.host.wait_for_controller_ready()
        c = self.vm.host.controller
        ret = c.monitor_cmd(self.vm.name, self.name, cmd, timeout)
        if ret == "None":
            ret = None
        return ret

    def migrate(self, uri, full_copy=False, incremental_copy=False, wait=False):
        logging.debug("Migrate %s(@%s), uri=%s",
                      self.vm.name, self.vm.host.address, uri)
        self.vm.host.wait_for_controller_ready()
        c = self.vm.host.controller
        func = lambda: c.monitor_migrate(self.vm.name, self.name, uri,
                                         full_copy, incremental_copy, wait)
        return virt_utils.wait_for(func, self.timeout)
