import os, re, logging, shutil
from autotest_lib.client.bin import utils, package, test
from autotest_lib.client.bin.test_config import config_loader
from autotest_lib.client.common_lib import error


class linpack(test.test):
    """
    """
    version = 1

    def run_once(self, config='./linpack.cfg'):
        cfg = config_loader(cfg=config, tmpdir=self.tmpdir, raise_errors=True)

        cachedir = os.path.join(self.bindir, 'cache')
        if not os.path.isdir(cachedir):
            os.makedirs(cachedir)

        logging.debug('Get and install linpack...')
        linpack_url = cfg.get('linpack', 'package_url')
        linpack_md5 = cfg.get('linpack', 'package_md5')
        linpack_pkg = utils.unmap_url_cache(cachedir, linpack_url, linpack_md5)

        package.install(linpack_pkg, nodeps=True)

        self.raw_result_file = os.path.join(self.resultsdir,
                                            'raw_output_%s' % self.iteration)
        raw_result = open(self.raw_result_file, 'w')

        logging.info('Running linpack perf test...')
        try:
            cmd = '(cd /mnt/tests/performance/linpack/certification/ && ' \
                  '/bin/bash runtest.sh)'
            results = utils.run(command=cmd, stdout_tee=raw_result,
                                stderr_tee=raw_result)
            self.results = results.stderr
            raw_result.close()
        except error.CmdError, e:
            raise error.TestError('Linpack perf test has failed: %s' % e)


    def postprocess_iteration(self):
        # move the results from /mnt/tests/performance/linpack/certification
        # to autotest result dir
        linpack_dir = '/mnt/tests/performance/linpack/certification/'
        linpack_result_archive = 'RHTSlinpack-results.tar.gz'
        linpack_result = os.path.join(linpack_dir, linpack_result_archive)

        shutil.move(linpack_result, self.resultsdir)
