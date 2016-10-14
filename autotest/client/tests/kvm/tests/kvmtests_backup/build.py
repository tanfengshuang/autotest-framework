from autotest_lib.client.virt import kvm_installer


class BrewInstaller:
    """
    Class that handles installing KVM from the brew build service.
    It uses yum to install and remove packages.
    """
    def __init__(self, test, params):
        """
        Class constructor. Sets default paths, and sets up class attributes

        @param test: kvm test object
        @param params: Dictionary with test arguments
        """
        default_pkg_list = 'kmod-kvm kvm kvm-qemu-img kvm-tools'
        default_qemu_bin_paths = '/usr/bin/qemu-kvm /usr/bin/qemu-img'
        default_base_url = 'http://download.devel.redhat.com/brewroot/'\
                                                           'packages/'
        default_release = 'kvm-83-142.el5'
        default_extra_modules = None

        # Checking if all required dependencies are available
        os_dep.command("rpm")
        os_dep.command("yum")

        self.pkg_list = params.get("pkg_list", default_pkg_list).split()
        self.base_url = params.get("base_pgk_url", default_base_url)
        self.qemu_bin_paths = params.get("qemu_bin_paths",
                                         default_qemu_bin_paths).split()
        self.release = params.get('release',default_release)
        # Are we going to load modules?
        load_modules = params.get('load_modules')
        if not load_modules:
            self.load_modules = True
        elif load_modules == 'yes':
            self.load_modules = True
        elif load_modules == 'no':
            self.load_modules = False
        self.extra_modules = params.get("extra_modules", default_extra_modules)

        self.srcdir = test.srcdir
        self.test_bindir = test.bindir


    def __clean_previous_installs(self):
        """
        Remove all rpms previously installed.
        """
        kill_qemu_processes()
        removable_packages = ""
        for pkg in self.pkg_list:
            removable_packages += " %s" % pkg
        utils.system("yum remove -y %s" % removable_packages)


    def __get_packages(self):
        """
        Downloads the packages using wget from brew source.
        """
        if not os.path.isdir(self.srcdir):
            os.makedirs(self.srcdir)
        os.chdir(self.srcdir)
        old_rpm_list = glob.glob("*.rpm")
        for rpm in old_rpm_list:
            os.remove(rpm)
        arch = utils.get_arch()
        built_list = self.release.split('-')
        for i in built_list:
            self.base_url = self.base_url + i + '/'
        self.base_url = self.base_url + arch + '/'
        for i in self.pkg_list:
            pkg_url = self.base_url + i + '-' + '-'.join(built_list[1:]) + \
                                        '.' + arch + '.rpm'
            os.system("wget -q " + pkg_url)


    def __install_packages(self):
        """
        Install all relevant packages that was just downloaded.
        """
        os.chdir(self.srcdir)
        installable_packages = ""
        rpm_list = glob.glob("*.rpm")
        for rpm in rpm_list:
            installable_packages += " %s" % rpm

        utils.system("yum install --nogpgcheck -y %s" % installable_packages)



    def install(self):
        self.__clean_previous_installs()
        self.__get_packages()
        self.__install_packages()
        create_symlinks(test_bindir=self.test_bindir,
                        bin_list=self.qemu_bin_paths)
        if self.load_modules:
            load_kvm_modules(load_stock=True, extra_modules=self.extra_modules)

def run_build(test, params, env):
    """
    Installs KVM using the selected install mode. Most install methods will
    take kvm source code, build it and install it to a given location.

    @param test: kvm test object.
    @param params: Dictionary with test parameters.
    @param env: Test environment.
    """
    srcdir = params.get("srcdir", test.srcdir)
    params["srcdir"] = srcdir

    try:
        installer_object = kvm_installer.make_installer(params)
        installer_object.set_install_params(test, params)
        installer_object.install()
        env.register_installer(installer_object)
    except Exception, e:
        # if the build/install fails, don't allow other tests
        # to get a installer.
        msg = "KVM install failed: %s" % (e)
        env.register_installer(kvm_installer.FailedInstaller(msg))
        raise
