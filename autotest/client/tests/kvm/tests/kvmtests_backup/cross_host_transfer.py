import logging, time
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_env_process
from autotest_lib.client.tests.kvm import kvm_cross_host_utils

def run_cross_host_transfer(test, params, env):
    """
    Test file transfer function between host and guest on another host.

    @param test: Kvm test object
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """

    def slaver_peer_func():
        # start vm after we mount images via nfs.
        params["start_vm"] = "yes"
        for vm in params.get("vms").split():
            virt_env_process.preprocess_vm(test, params, env, vm)

    login_timeout = int(params.get("login_timeout", 360))

    remote_host, xmlrpc_server = kvm_cross_host_utils.test_init(test, params,
                                                                env)

    if params.get("slaver_peer") == "yes":
        slaver_peer_func()

    remote_vm_list = remote_host.get_vms_list()

    dir_name = test.tmpdir
    transfer_timeout = int(params.get("transfer_timeout"))
    guest_path = params.get("tmp_dir", "/tmp/")
    clean_cmd = params.get("clean_cmd", "rm -f")
    file_size = int(params.get("file_size", 4000))

    # generate a file for test.
    #TODO: add a new utils to generate files for transfering
    cmd = "dd if=/dev/urandom of=%s/src.out bs=1M count=%d" % \
            (dir_name, file_size)
    logging.debug("Generate a file for test.")
    utils.system(cmd)
    file_hash = utils.hash_file("%s/src.out" % dir_name, method="md5")
    logging.debug("file md5 hash: %s", file_hash)

    try:
        for remote_vm in remote_vm_list:
            logging.info("Transfering: host -> guest (%s), timeout: %ss",
                         remote_vm.name, transfer_timeout)
            t_begin = time.time()
            success = remote_vm.copy_files_to("%s/src.out" % dir_name,
                                        guest_path + "/dest.out",
                                        timeout=transfer_timeout)
            t_end = time.time()
            throughput = file_size / (t_end - t_begin)
            if not success:
                raise error.TestFail("fail to transfer from host to guest")
            logging.info("Transfer succeed: host -> guest (%s) succeed, "
                         "estimated throughput: %.2fmb/s",
                         remote_vm.name, throughput)

            logging.info("Transfering: guest (%s) -> host, timeout: %ss",
                         remote_vm.name, transfer_timeout)
            t_begin = time.time()
            success = remote_vm.copy_files_from(guest_path + "/dest.out",
                                             "%s/c.out" % dir_name,
                                             timeout=transfer_timeout)
            t_end = time.time()
            throughput = file_size / (t_end - t_begin)
            if not success:
                raise error.TestFail("fail to transfer from guest to host")
            logging.info("transfer succeed guest (%s) -> host succeed, "
                         "estimated throughput: %.2fmb/s",
                         remote_vm.name, throughput)

            file_hash_new = utils.hash_file("%s/c.out" % dir_name)
            if file_hash != file_hash_new:
                raise error.TestFail("File changed after transfer host "
                                     "-> guest and guest -> host")

            logging.info('Cleaning temp file on guest...')
            session = remote_vm.wait_for_login(timeout=login_timeout)
            s, o = session.get_command_status_output(
                                    clean_cmd + " %s/dest.out" % guest_path,
                                    timeout=login_timeout)
            if s:
                logging.warning("Failed to clean remote file %s, output:%s",
                                guest_path, o)
    finally:
        logging.info('Cleaning temp files on host...')
        utils.system(clean_cmd + " %s/c.out" % dir_name)
        kvm_cross_host_utils.test_finish(remote_host, xmlrpc_server,
                                         login_timeout)
