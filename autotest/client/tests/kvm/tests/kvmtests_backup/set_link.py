import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt.tests import file_transfer
from autotest_lib.client.virt import virt_test_utils


def run_set_link(test, params, env):
    """
    KVM guest link test:
    1) Boot up guest with one nic
    2) Ping guest from host
    3) Disable guest link and ping guest from host
    4) Re-enable guest link and ping guest from host
    5) Do file transfer test

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()

    timeout = float(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=timeout)

    def set_link_test(linkid):
        """
        Issue set_link commands and test its function

        @param linkid: id of netdev or devices to be tested
        """
        ip = vm.get_address(0)

        vm.monitor.set_link(linkid, 'off')
        s, o = virt_test_utils.ping(ip, count=10, timeout=20)
        if virt_test_utils.get_loss_ratio(o) != 100:
            raise error.TestFail("Still can ping the %s after down %s" %
                                 (ip, linkid))

        vm.monitor.set_link(linkid, 'on')
        s, o = virt_test_utils.ping(ip, count=10, timeout=20)
        # we use 100% here as the notification of link status changed may be
        # delayed in guest driver
        if virt_test_utils.get_loss_ratio(o) == 100:
            raise error.TestFail("Packet loss during ping %s after up %s" %
                                 (ip, linkid))

    netdev_id = vm.netdev_id[0]
    device_id = vm.get_peer(netdev_id)
    logging.info("Issue set_link commands for netdevs")
    set_link_test(netdev_id)
    logging.info("Issue set_link commands for network devics")
    set_link_test(device_id)

    file_transfer.run_file_transfer(test, params, env)
    session.close()
