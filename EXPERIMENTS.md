This document describes the details of the experiments we carried out to obtain the main results in [our SOSP'19 paper](https://dl.acm.org/citation.cfm?id=3359640).

## Hardware Setup

* server: HP DL160 G9
* processor: 2.40GHz Intel Xeon E5-2630 v3
* memory: 128GB 1866MHz DDR4
* disk: HP 816876-004/MZ-7LM9600, 960GB SSD


## Software Versions

Ubuntu version: `Ubuntu 16.04.6 LTS`

Ubuntu kernel versions (64bit): 
`3.0.7-030007-generic, 3.1.7-030107-generic, 3.2.11-030211-generic, 3.3.6-030306-generic, 3.4.6-030406-generic, 3.5.4-030504-generic, 3.6.10-030610-generic, 3.7.9-030709-generic, 3.8.10-030810-generic, 3.9.8-030908-generic, 3.10.10-031010-generic, 3.11.6-031106-generic, 3.12.8-031208-generic, 3.13.7-031307-generic, 3.14.6-031406-generic, 3.15.8-031508-generic, 3.16.3-031603-generic, 3.17.6-031706-generic, 3.18.6-031806-generic, 3.19.3-031903-generic, 4.0.5-040005-generic, 4.1.6-040106-generic, 4.2.5-040205-generic, 4.3.3-040303-generic, 4.4.5-040405-generic, 4.5.4-040504-generic, 4.6.4-040604-generic, 4.7.6-040706-generic, 4.8.14-040814-generic, 4.9.11-040911-generic, 4.10.13-041013-generic, 4.11.8-041108-generic, 4.12.10-041210-generic, 4.13.12-041312-generic, 4.14.15-041415-generic, 4.15.15-041515-generic, 4.16.13-041613-generic, 4.17.14-041714-generic, 4.18.16-041816-generic, 4.19.11-041911-generic, 4.20.13-042013-generic`

We originally downloaded the kernels from [here](https://kernel.ubuntu.com/~kernel-ppa/mainline/).
However, some of the kernels are no longer hosted. We backed up the kernels [here](https://github.com/LinuxPerfStudy/ExperimentSetup/tree/master/default_ubuntu_kernels) and kernel configurations [here](https://github.com/LinuxPerfStudy/ExperimentSetup/tree/master/default_ubuntu_kernel_configs). 
We had to backport patches to the 3.0.7 and 3.1.7 kernels to fix compatibility issues that prevent booting. The patches can be found [here](https://github.com/LinuxPerfStudy/ExperimentSetup/tree/master/boot_patches).

## Bechmark

LEBench can be downloaded from [here](https://github.com/LinuxPerfStudy/LEBench). 
Instructions for running LEBench can be found [here](https://github.com/LinuxPerfStudy/LEBench/blob/master/README.md).

## Disabling the Root Causes 

We identified 11 root causes that account for most of the performance changes observed in our experiments, they are described in section 3&4 of the paper.
Here is how to disable each of the 11 root causes:
 
* **Kernel page-table isolation (Meltdown patch)**: unset the `CONFIG_PAGE_TABLE_ISOLATION` build configuration option
* **Avoid indirect branch speculation (Spectre patch)**: unset the `CONFIG_RETPOLINE` build configuration option
* **SLAB freelist randomization**: unset the `CONFIG_SLAB_FREELIST_RANDOM` build configuration option
* **Hardened usercopy**: unset the `CONFIG_HARDENED_USERCOPY` build configuration option
* **Fault around**: apply this [patch](https://github.com/LinuxPerfStudy/ExperimentSetup/tree/master/root_causes/fault_around)
* **Control group memory controller**: unset the `CONFIG_MEMCG` build configuration option
* **Disabling transparent huge pages**: set the `CONFIG_TRANSPARENT_HUGEPAGE_ALWAYS`  build configuration option to `y`
* **Userspace page fault handling**: unset the `CONFIG_USERFAULTFD`  build configuration option
* **Forced context tracking**: unset the `CONFIG_CONTEXT_TRACKING_FORCE`  build configuration option
* **TLB layout specification**: apply this [patch](https://github.com/LinuxPerfStudy/ExperimentSetup/tree/master/root_causes/tlb_layout)
* **Missing CPU power-saving states**: apply this [patch](https://github.com/LinuxPerfStudy/ExperimentSetup/tree/master/root_causes/cpu_power_saving_states)
 

## Custom Building a Kernel
* Download the kernel codebase: `git clone git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git` and checkout the version of choice, for example: `git checkout v4.0.1`.
* To use a particular configuration file to build the kernel, copy the configuration file into the Linux codebase directory, and rename the file to `.config`.
* To edit the configuration file, run: `make menuconfig`, then change the appriopriate configuration option and save. The updated configuration should be reflected in the `.config` file. 
* To apply a patch, run: `git apply <name>.patch`.
* To compile a custom kernel, run: ``make -j `getconf _NPROCESSORS_ONLN` deb-pkg LOCALVERSION=-custom`` in the Linux codebase directory. (Newer kernels can be compiled on Ubuntu 16 without a problem; some older kernels need to be compiled using Ubuntu 14 for libc compatibility.)
* To install the custom kernel, run: `sudo dpkg -i *.deb`.

([Reference](https://wiki.ubuntu.com/KernelTeam/GitKernelBuild))