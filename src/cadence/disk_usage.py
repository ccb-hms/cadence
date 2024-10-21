#!/home/andreas/gitrepos/cadence/.venv/bin/python

import shutil

def check_disk_usage(disk, min_absolute, min_percent):
    """ Returns True if there is enough disk free space, false otherwise"""
    du = shutil.disk_usage(disk)
    # Calculate the percentage of free space
    percent_free = 100*du.free / du.total
    # Calculate how many free gigabytes
    gigabytes_fee = du.free/2**30
    if percent_free < min_percent or gigabytes_fee < min_absolute:
        return False
    return True

if __name__ == "__main__":
    if not check_disk_usage(disk='/', min_absolute=2*2**30, min_percent=10):
        print('ERROR: Not enough disk space')
        return 1

    print('Everything is ok')
    return 0
