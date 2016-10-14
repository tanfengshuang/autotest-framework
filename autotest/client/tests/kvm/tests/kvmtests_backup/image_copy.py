import os, logging, commands
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_utils

def run_image_copy(test, params, env):
    """
    Copy guest images from nfs server.
    1) Mount the NFS directory
    2) Check the existence of source image
    3) If existence copy the image from NFS

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    mount_dest_dir = params.get("dst_dir",'/mnt/linux')
    try:
        os.makedirs(mount_dest_dir)
    except OSError, err:
        logging.warn("mkdir %s error:\n%s" % (mount_dest_dir, err))

    if not os.path.exists(mount_dest_dir):
        raise error.TestError("Failed to mkdir %s" % mount_dest_dir)
    logging.debug("Dir %s exists." % mount_dest_dir)

    src = params['images_good']
    mnt_cmd = "mount %s %s -o ro" % (src, mount_dest_dir)
    pwd = os.path.join(os.environ['AUTODIR'],'tests/kvm/images')
    image = os.path.split(params['image_name'])[1]+'.'+params['image_format']
    src_path = os.path.join(mount_dest_dir, image)
    dst_path = os.path.join(pwd, image)
    cmd = "cp %s %s" % (src_path, dst_path)

    if virt_utils.mount(src, mount_dest_dir, "nfs", "ro") is not True:
        raise error.TestError("Fail to mount the %s to %s" % \
                              (src, mount_dest_dir))

    # Check the existence of source image
    if not os.path.exists(src_path):
        raise error.TestError("Could not found %s in src directory" % src_path)

    logging.debug("Copying image %s..." % image)
    s, o = commands.getstatusoutput(cmd)
    if s != 0:
        raise error.TestFail("Failed to copy image:%s; Reason: %s" % (cmd, o))
