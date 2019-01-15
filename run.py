#!/usr/bin/env python
import os
import signal
import platform
import sys
from subprocess import check_call, check_output, call
from os.path import join
from datetime import datetime

KERN_COUNTS = 89

WD='/LEBench/'
ITER_FILE = '/LEBench/iteration' 
LOCAL_GRUB_NAME = '/LEBench/grub'
GRUB_LOCATION = '/etc/default/grub' 
GRUB_CFG_LOCATION = '/boot/grub/grub.cfg'
KERN_LIST_FILE = '/LEBench/kern_list' 
RESULT_DIR = '/LEBench/RESULT_DIR'
TEST_FILES_DIR = '/LEBench/TEST_DIR'

GCC_CMD_TEMPLATE  = 'gcc -pthread %s -o %s'

def get_kern_list(idx):
    with open(KERN_LIST_FILE, 'r') as fp:
        if -1 < idx < KERN_COUNTS:
            return fp.readlines()[idx].strip()
        else:
            print 'Kern index %d out of range (%d)' % (idx, KERN_COUNTS)
            raise ValueError('Kernel index out of range, iteration stops')


def modify_grub(f, target_kern):
    print "    Preparing for kern:i " + target_kern 
    print "--------------------------------------------------"

    if not os.path.exists(f):
        print "File %s does not exist." % f
        return False

    kern_image_name = 'vmlinuz-%s' % target_kern
    if not os.path.exists(os.path.join('/', 'boot', kern_image_name)):
        print "Kernel image %s does not exist" % kern_image_name
        return False

    print "Setting boot version to %s" % target_kern
    with open(f, 'r') as fp:
        lines = fp.readlines()

        for idx, line in enumerate(lines):
            if line.startswith('GRUB_DEFAULT'):
                line = 'GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux %s"\n' % target_kern
                lines[idx] = line
        
    with open(LOCAL_GRUB_NAME, 'w+') as fp:
        fp.writelines(lines)
    
    return True

"""This function sets up grub using configtured grub file and shell cmds
"""
def configure_boot():
    print "Copying GRUB config to %s" % GRUB_LOCATION
    call(['sudo', 'cp', LOCAL_GRUB_NAME, GRUB_LOCATION])
    print "Configuring boot"
    call(['sudo', 'grub-install', '--force', '--target=i386-pc', '/dev/sda1'])
    print "Making grub config"
    call(['sudo', 'grub-mkconfig', '-o', GRUB_CFG_LOCATION])


def run_tests(idx):
    print "Running tests"
    test_files = os.listdir(TEST_FILES_DIR)
    kern_version = platform.uname()[2]
    print "Tests: "
    print test_files
    print "Test: got kern_version " + kern_version
    for test_file in test_files:
        test_file = join(TEST_FILES_DIR, test_file.strip())
        if 'OS_Eval' in test_file:
            run_test(test_file, '0', kern_version)


def run_test(c_filename, *args):
    print "Running specific test"
    kern_version = platform.uname()[2]
    print "Got kernel " + kern_version
    result_path = join(RESULT_DIR, kern_version) 

    if not os.path.exists(result_path):
        os.makedirs(result_path)

    test_bin_name = test_name = os.path.basename(c_filename).split('.')[0]  
    result_filename = join(RESULT_DIR, kern_version, test_name)

    print '| Compiling test ' + test_name
    gcc_cmd = GCC_CMD_TEMPLATE % (c_filename, test_bin_name)
    print gcc_cmd
    call(gcc_cmd.split())

    print '| Running test ' + test_name
    with open(result_filename, 'w+') as fp:
        test_cmd = [WD+test_bin_name] + list(args)
        print test_cmd
        ret = call(test_cmd, stdout=fp, stderr=fp)

    print '| Finished running test ' + test_name + ' return ' + str(ret) + ' log written to\n| ' + result_filename


def test_loop():
    print "--------------------------------------------------"
    print "             linux kernel tests"
    print "             current time: " + str(datetime.now().time())

    with open(ITER_FILE, 'r') as f:
        kern_idx = int(f.read())
    next_kern_idx = kern_idx + 1
    print "     Running at iteration " + str(kern_idx)
    
    with open(ITER_FILE, 'w') as fp:
        fp.write(str(next_kern_idx).strip())

    print "Done writing %d to next iteration" % next_kern_idx

    if next_kern_idx == 0:
        print "At first iteration"
    else:
        print "Calling run test"
        run_tests(kern_idx)

    print "Prepare modifying grub"
    if modify_grub(WD+'template/grub', get_kern_list(next_kern_idx)):
        configure_boot()
        print "Done config kernel swap"
        restart()


def restart():
    print '| Shutting down'
    call(['sudo', 'reboot'])


if __name__ == '__main__':
    HOME=os.environ['LEBENCH_DIR']
    WD = HOME + WD
    ITER_FILE = HOME + ITER_FILE
    LOCAL_GRUB_NAME = HOME + LOCAL_GRUB_NAME
    KERN_LIST_FILE = HOME + KERN_LIST_FILE
    RESULT_DIR = HOME + RESULT_DIR
    TEST_FILES_DIR = HOME + TEST_FILES_DIR

    if len(sys.argv) > 1:
        kern_ver = sys.argv[1]
        print "Configuring boot with " + kern_ver
        modify_grub(WD+'template/grub', kern_ver)
        configure_boot()
        sys.exit(0)

    print "Running script"
    test_loop()
