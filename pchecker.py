# pchecker.py: parameter checker

import os
import sys

def check(filename, name = None, run = True):
    """ parameter, poor implementation , need to rewrite :)
    """
    case = ''
    argv = ''
    cfg = open(filename,'r')
    line = cfg.readline()
    lineno = 12
    while line:
        if '[' in line:
            if ']' not in line:
                print 'error in %s' % line
                os._exit(-1)
            try:
                testname = line.strip()[1:-1]
                if name == None or testname == name:
                    print '[Test name %s]' % testname
                line = cfg.readline()
                lineno += 1
                if testname == 'log':
                    continue
                if name != None and testname != name:
                    continue
                while line:
                    if '[' in line:
                        break
                    if line == '\n':                       
                        break;
                    try:
                        key, value = line.split('=')
                        value = value.strip()
                        if value == 'var':
                            value = raw_input('%s=' % key)
                        else:
                            value = value[1:-1]
                            
                            if key == 'path':
                                if not os.path.exists(value):
                                    print ('file not found %s' % value)
                                    os._exit(-1)
                                else:
                                    case = value
                            else:
                                value = value.split('|')[0]                        
                        
                        if key != 'path':
                            if value.isdigit():
                                argv += ' --%s=%d ' % (key, int(value))
                            else:
                                if ' ' in value:
                                    value = '\'' + value + '\''
                                argv += ' --%s=%s ' % (key, value)

                    except ValueError, message:
                        print ('format error %d %s %s' % (lineno, line, message))
                        os._exit(-1)
                    line = cfg.readline()
                    lineno += 1
                cmd = 'python %s %s' % (case,argv)
                print 'cmd is %s' % cmd
                if run:
                    os.system(cmd)
                case = ''
                argv = ''
                if '[' in line:
                    continue
            except IndexError:
                print ('index error in %d %s %s' % (lineno ,line , message))
        line = cfg.readline()
        lineno += 1

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc < 2:
        print "usage %s config [testname,[run=True/False]]" % sys.argv[0]
        os._exit(-1)
    if argc == 2:
        check(sys.argv[1])
    elif argc == 3:
        check(sys.argv[1],sys.argv[2])
    elif argc == 4:
        if sys.argv[3] == 'False':
            check(sys.argv[1],sys.argv[2],False)
        else:
            check(sys.argv[1],sys.argv[2])
    else:
        print "too many parameters"


