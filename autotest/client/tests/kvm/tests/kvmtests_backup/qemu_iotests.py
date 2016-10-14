import re, os, logging, commands
from autotest_lib.client.common_lib import utils, error

def run_qemu_iotests(test, params, env):
    """
    Run qemu_iotests:
    1). git qemu-iotests-rhel6 from server
    2). cd qemu-iotests-rhel6
    3). run test, the cmd format is ./check [iamge_format] [list]

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    def iotest(image_type=None, test_list=None):
        """
        check options
            -raw                test raw (default)
            -cow                test cow
            -qcow               test qcow
            -qcow2              test qcow2
            -qed                test qed
            -vdi                test vdi
            -vpc                test vpc
            -vmdk               test vmdk
            -rbd                test rbd
            -sheepdog           test sheepdog
            -xdiff		graphical mode diff
            -nocache		use O_DIRECT on backing file
            -misalign		misalign memory allocations
            -n			show me, do not run tests
            -T			output timestamps
            -r 			randomize test order

        testlist options
            -g group[,group...]	include tests from these groups
            -x group[,group...]	exclude tests from these groups
            NNN			include test NNN
            NNN-NNN		include test range (eg. 012-021)
        """
        cmd = "./check"
        if image_type:
            cmd += " -" + image_type
        if test_list:
            cmd += test_list

        try:
            utils.system(cmd)
        except error.CmdError, e:
            log_file = os.path.join(test.outputdir, "qemu_iotests.log")
            open(log_file, "w").write("Test Failed:\n %s" % str(e))
            msg = "Test Failed. Please refer to qemu_iotests.log for details!"
            raise error.TestFail(msg)

    src_dir = os.path.join(test.bindir, "tests_src/qemu-iotests-rhel6")
    download_cmd = "%s %s %s" % (params.get("download_cmd"),
                              params.get("rsc_server"), src_dir)

    if not os.path.exists(src_dir):
        logging.info("downloading qemu-iotests-rhel6 ...")
        s, o = commands.getstatusoutput(download_cmd)
        if s != 0:
            raise error.TestFail("Failed to download source package")

    test_dir = os.path.join(src_dir, "scratch")
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    os.chdir(src_dir)
    image_type = params.get("image_type", "")
    test_list = params.get("test_list", "")

    iotest(image_type=image_type, test_list=test_list)
