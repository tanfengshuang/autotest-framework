##@ Summary:    Configured TestSuite Launcher
##@ Description: Customized everything.
##@ Maintainer: Chen Cao <kcao@redhat.com>
##@ Updated:    Sun Sep 26, 2010
##@ Version:    1

import sys, os, logging, re
import common
from lib import dict_handler, virtlab, launcher

def fix_argv(argv, pattern):
    argv_str = ' '.join(argv)
    logging.info("match '%s' in '%s'" % (pattern, argv))
    match_cmd = re.findall(pattern, argv_str)
    if len(match_cmd) > 0:
        argv_list = argv_str.split(match_cmd[0])
        argv_str = ' '.join(argv_list)
        argv_list = argv_str.split()
        argv_list.append(match_cmd[0])
        logging.info("Matched given pattern, new argv list: %s" % argv_list)
        return argv_list
    logging.info("Not Matched given pattern")
    return None


if __name__ == "__main__":
    logging.info("sys.argv: %s" % str(sys.argv))

    # Build dict from argv
    dict = dict_handler.build_dict(sys.argv[1:])

    # do some fix for --custmozied_cmd
    argv_list = None
    if dict.get('use_customized_cmd') == 'yes':
        argv_list = fix_argv(sys.argv,"--customized_cmd=.* CUSTOMIZED_CMD_END")
    else:
        logging.error("Only support --use_customized_cmd=yes, exiting...")
        sys.exit(1)

    # Build dict from argv_list
    if argv_list is not None:
        dict = dict_handler.build_dict(argv_list[1:])

    logging.info("launch agent is: %s" % dict.get('launch_agent'))
    if dict.get('launch_agent') == "virtlab_cli":
        logging.info('Not in virtlab, submit from CLI.')
        virtlab.parse_run(dict, argv=sys.argv)

    elif dict.get('launch_agent') == "loop":
        logging.info("run loop...")
        launcher.run_loop(dict)

    elif dict.get('launch_agent') == "alt_autotest":
        tree = dict.get('autotest_tree')
        cmd = dict.get('customized_cmd')
        branch = dict.get('autotest_branch')

        logging.info("run customized autotest, "
                     "with:\ntree: %s\ncommand: %s\nbranch: %s" % \
                     (tree, cmd, branch))
        launcher.run_customized_autotest(tree, cmd, branch)
    elif dict.get('launch_agent') == "alt_launcher":
        launcher_tree = dict.get('launcher_tree')
        launcher_branch = dict.get('launcher_branch')
        autotest_tree = dict.get('autotest_tree')
        autotest_branch = dict.get('autotest_branch')
        cmd = dict.get('customized_cmd')

        logging.info("run customized launcher, "
                     "with:\nlauncer_tree: %s\nlauncher_branch: %s"
                     "\nautotest_tree: %s\nautotest_branch: %s"
                     "\ncustomized command: %s " % \
                     (launcher_tree, launcher_branch,
                      autotest_tree, autotest_branch, cmd))

        launcher.run_customized_launcher(launcher_tree, launcher_branch,
                                         autotest_tree, autotest_branch, cmd)

