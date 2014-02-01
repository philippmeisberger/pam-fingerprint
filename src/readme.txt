## Important: You have to add the application root to PYTHONPATH variable first:
~$ cd /path/to/root/
~$ export PYTHONPATH=$PYTHONPATH:$(pwd)


## Serial connection permission:
~# usermod -a -G dialout username
~# reboot