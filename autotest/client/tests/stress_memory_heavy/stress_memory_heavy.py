import os
from autotest_lib.client.bin import test, utils


class stress_memory_heavy(test.test):
    """
    Calls stress, a simple program which aims to impose certain types of
    computing stress on the target machine.
    @author: Yi Yang (yang.y.yi@gmail.com)

    In order to verify at a glance the options supported by the program stress,
    check out the options summary located at the stress example control file.
    """
    version = 1

    def initialize(self):
        self.job.require_gcc()


    # http://weather.ou.edu/~apw/projects/stress/stress-1.0.0.tar.gz
    def setup(self, tarball = 'stress-1.0.0.tar.gz'):
        tarball = utils.unmap_url(self.bindir, tarball, self.tmpdir)
        utils.extract_tarball_to_dir(tarball, self.srcdir)
        os.chdir(self.srcdir)

        utils.configure()
        utils.make()


    def run_once(self, args = '', stress_length=60):
        if not args:
            # We will use 2 workers of each type for each CPU detected
            threads = 2 * utils.count_cpus()

            mem = utils.memtotal() / 1024 / 512
            memory_per_thread = 256 * 1024

            # Even though unlikely, it's good to prevent from allocating more
            # disk than this machine actually has on its autotest directory
            # (limit the amount of disk used to max of 90 % of free space)
            free_disk = utils.freespace(self.srcdir)
            file_size_per_thread = 1024 ** 2
            if (0.9 * free_disk) < file_size_per_thread * threads:
                file_size_per_thread = (0.9 * free_disk) / threads

            # Number of CPU workers spinning on sqrt()
            args = '--cpu %d ' % threads
            # Number of IO workers spinning on sync()
            args += '--io %d ' % threads
            # Number of Memory workers spinning on malloc()/free()
            args += '--vm %d ' % mem
            # Amount of memory used per each worker
            args += '--vm-bytes %d ' % memory_per_thread
            # Number of HD workers spinning on write()/ulink()
            args += '--hdd %d ' % threads
            # Size of the files created by each worker in bytes
            args += '--hdd-bytes %d ' % file_size_per_thread
            # Time for which the stress test will run
            args += '--timeout %d ' % stress_length
            # Verbose flag
            args += '--verbose'

        utils.system(self.srcdir + '/src/stress ' + args)
