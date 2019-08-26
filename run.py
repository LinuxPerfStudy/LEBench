#!/usr/bin/env python
import os
import signal
import platform
import sys
from subprocess import check_call, check_output, call
from os.path import join
from datetime import datetime

DEBUG            = True

GRUB_CFG_FILE    = '/boot/grub/grub.cfg'
GRUB_FILE        = '/etc/default/grub' 

WORKING_DIR      = ''
KERN_INDEX_FILE  = '/iteration' 
LOCAL_GRUB_FILE  = '/grub'
KERN_LIST_FILE   = '/kern_list' 
RESULT_DIR       = '/RESULT_DIR/'
TEST_DIR         = '/TEST_DIR/'
TEST_NAME        = 'OS_Eval'


""" Grabs the ith kernel from KERN_LIST_FILE.
"""
def get_kern_list(idx):
    with open(KERN_LIST_FILE, 'r') as fp:
        lines = fp.readlines()

        if -1 < idx < len(lines):
            return lines[idx].strip()
        elif idx >= len(lines):
            print '[INFO] LEBench run concluded, finished testing on ' + str(len(lines)) + 'kernels.'
            os.remove(KERN_INDEX_FILE)
        else:
            raise ValueError('Kernel index out of range, '
                        'expect index to be between 0 and ' + str(len(lines)))


""" Modifies the grub file to boot into the target kernel the next time.
"""
def generate_grub_file(f, target_kern):
    if DEBUG: print '[DEBUG]    Preparing grub for kernel: ' + target_kern 
    if DEBUG: print '[DEBUG]--------------------------------------------------'

    if not os.path.exists(f):
        raise ValueError("File %s does not exist." % f)

    kern_image_name = 'vmlinuz-%s' % target_kern
    if not os.path.exists(os.path.join('/', 'boot', kern_image_name)):
        raise ValueError('Kernel image %s does not exist' % kern_image_name)

    print '[INFO] Setting boot version to ' +  target_kern + '.'
    with open(f, 'r') as fp:
        lines = fp.readlines()

        for idx, line in enumerate(lines):
            if line.startswith('GRUB_DEFAULT'):
                line = 'GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux %s"\n' % target_kern
                lines[idx] = line
        
    with open(LOCAL_GRUB_FILE, 'w+') as fp:
        fp.writelines(lines)
    
    return True

"""Sets up grub using configtured grub file and shell cmds
"""
def install_grub_file():
    if DEBUG: print "[DEBUG] Copying GRUB config to %s" % GRUB_FILE
    call(['sudo', 'cp', LOCAL_GRUB_FILE, GRUB_FILE])
    if DEBUG: print "[DEBUG] Configuring boot"
    call(['sudo', 'grub-install', '--force', '--target=i386-pc', '/dev/sda1'])
    if DEBUG: print "[DEBUG] Making grub config"
    call(['sudo', 'grub-mkconfig', '-o', GRUB_CFG_FILE])

def restart():
    print '[INFO] Restarting the machine now.'
    call(['sudo', 'reboot'])


""" Running the LEBench tests for the current kernel version.
"""
def run_bench():

    print '[INFO] --------------------------------------------------'
    print '[INFO]              Starting LEBench tests'
    print '[INFO]              Current time: ' + str(datetime.now().time())

    kern_version = platform.uname()[2]
    print '[INFO] current kernel version: ' + kern_version + '.'

    test_file = join(TEST_DIR, TEST_NAME)
    print '[INFO] Preparing to run test ' + TEST_NAME + '.'

    print '[INFO] Compiling test ' + TEST_NAME + ".c."
    call(('make -C ' + TEST_DIR).split())


    result_path = join(RESULT_DIR, kern_version) 
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    result_filename = join(RESULT_DIR, kern_version, TEST_NAME)
    result_error_filename = join(RESULT_DIR, kern_version, TEST_NAME + '_err')

    result_fp = open(result_filename, 'w+')
    result_error_fp = open(result_error_filename, 'w+')
    test_cmd = [TEST_DIR + TEST_NAME, '0', kern_version]
    print '[INFO] Running test with command: ' + ' '.join(test_cmd)
    ret = call(test_cmd, stdout=result_fp, stderr=result_error_fp)

    print '[INFO]              Finished running test ' + TEST_NAME + \
            ', test returned ' + str(ret) + ', log written to: ' + result_path + "."
    print '[INFO]              Current time: ' + str(datetime.now().time())
    with open(result_error_filename, 'r') as fp:
        lines = fp.readlines()
        if len(lines) > 0:
            for line in lines:
                print line
            raise Exception('[FATAL] test run encountered error.')


if __name__ == '__main__':

    # Setting up working directory and sanity checks.
    if not os.geteuid() == 0:
        raise Exception('This script should be run with "sudo".')

    try:
        WORKING_DIR = os.environ['LEBENCH_DIR']
    except:
        raise ValueError('$LEBENCH_DIR is not set. Example: "/home/username/LEBench/".')

    if 'LEBench' not in WORKING_DIR:
        raise ValueError('$LEBENCH_DIR should point to the directory containing LEBench. Example: "/home/username/LEBench/".')

    KERN_INDEX_FILE = WORKING_DIR + KERN_INDEX_FILE
    LOCAL_GRUB_FILE = WORKING_DIR + LOCAL_GRUB_FILE
    KERN_LIST_FILE  = WORKING_DIR + KERN_LIST_FILE
    RESULT_DIR      = WORKING_DIR + RESULT_DIR
    TEST_DIR        = WORKING_DIR + TEST_DIR

    if not os.path.exists(KERN_LIST_FILE):
        raise IOError('Cannot open "kern_list" file. If it\'s not present, '
                'run "get_kern.py" to generate this file by grepping all install kernels.')

    with open(KERN_LIST_FILE, 'r') as fp:
        lines = fp.readlines()
        if len(lines) == 0:
            raise ValueError('"kern_list" file is empty, '
                'run "get_kern.py" to generate this file by grepping all install kernels.')

    # For running LEBench on one specified kernel version.
    if len(sys.argv) > 1:
        kern_version = sys.argv[1]
        print "[INFO] Configuring to boot into " + kern_version + "."
        generate_grub_file(WORKING_DIR + 'template/grub', kern_version)
        install_grub_file()
        sys.exit(0)


    # For running LEBench on a list of specified kernel versions.
    if not os.path.exists(KERN_INDEX_FILE):
        with open(KERN_INDEX_FILE, 'w') as f:
            f.write("-1\n")

    with open(KERN_INDEX_FILE, 'r') as f:
        kern_idx = int(f.read())
    next_kern_idx = kern_idx + 1
    if DEBUG: print '[DEBUG] Running at kernel index: ' + str(kern_idx)
    
    with open(KERN_INDEX_FILE, 'w') as fp:
        fp.write(str(next_kern_idx).strip())

    if DEBUG: print '[DEBUG] Done writing kernel index %d for the next iteration' % next_kern_idx + '.'

    if next_kern_idx == 0:
        # Need to boot into the right kernel version first.
        print '[INFO] LEBench tests will start after booting into the first kernel.'
    else:
        # We are at the right kernel version, actually run LEBench.
        run_bench()

    if DEBUG: print '[DEBUG] Preparing to modify grub.'
    if generate_grub_file(WORKING_DIR + 'template/grub', get_kern_list(next_kern_idx)):
        install_grub_file()
        if DEBUG: print '[DEBUG] Done configuring grub for the next kernel.'
        restart()


