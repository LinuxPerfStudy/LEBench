run "crontab -e" and add the following entries:

LEBENCH_DIR=<path>/LEBench/
PATH=/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
@reboot python <path>/LEBench/run.py >> <path>/LEBench.out 2>&1

run "python get_kern.py" to generate the kernel list

run "sudo python run.py"

results will be saved in .csv files in the LEBench folder
