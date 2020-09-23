# LEBench

### Setup cron job

Run
```shell
crontab -e
```

and add the following entries:

```shell
LEBENCH_DIR=<path>/LEBench/
PATH=/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
@reboot python <path>/LEBench/run.py >> <path>/LEBench.out 2>&1
```



### Generate kernel list

```shell
cd $LEBench_ROOT
python get_kern.py
```



### Run LEBench

```shell
cd $LEBench_ROOT
sudo python run.py
```

The results will be saved in `output.<version>.csv` files in the LEBench folder.



Detailed instructions for reproducing the main results in our study can be found [here](https://github.com/LinuxPerfStudy/LEBench/blob/master/EXPERIMENTS.md).