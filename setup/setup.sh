
# Install oh my bash
sudo su
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

cd /
git clone https://github.com/GindaChen/LEBench.git

crontab -e
# Copy these into crontab
```
LEBENCH_DIR=/LEBench/
PATH=/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
@reboot python /LEBench/run.py >> /LEBench.out 2>&1
```

# Run LEBench (without any configuration)
cd /LEBench
python get_kern.py
LEBENCH_DIR=/LEBench/ PATH=/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin sudo python run.py
# LEBENCH_DIR=/LEBench/ PATH=/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin /LEBench/TEST_DIR/OS_Eval 0 4.15.0-101-generic

# Compile the linux kernel
cd /mydata
git clone git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git
git checkout v4.12
make menuconfig
make -j `getconf _NPROCESSORS_ONLN` deb-pkg LOCALVERSION=-custom
sudo sudo dpkg -i *.deb