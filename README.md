# Living Network Meta Analysis

The Living Network Meta Analysis System is a platform for researchers 

# Production Environment Setup

## System

The B4ms VM contains 3 disks, /dev/sda and /dev/sdb and /dev/sdc. 

```bash
$ sudo fdisk /dev/sdc

Device does not contain a recognized partition table.
Created a new DOS disklabel with disk identifier 0xb9bc5938.

Command (m for help): n
Partition type
   p   primary (0 primary, 0 extended, 4 free)
   e   extended (container for logical partitions)
Select (default p): p
Partition number (1-4, default 1):
First sector (2048-268435455, default 2048):
Last sector, +sectors or +size{K,M,G,T,P} (2048-268435455, default 268435455):

Created a new partition 1 of type 'Linux' and of size 128 GiB.

Command (m for help): p
Disk /dev/sdc: 128 GiB, 137438953472 bytes, 268435456 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: dos
Disk identifier: 0xb9bc5938

Device     Boot Start       End   Sectors  Size Id Type
/dev/sdc1        2048 268435455 268433408  128G 83 Linux

Command (m for help): w
The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.

$ sudo mkfs -t ext4 /dev/sdc1
$ sudo mkdir /data1
$ sudo mount /dev/sdc1 /data1

```

## Linux System

```bash
$ sudo apt update
$ sudo apt install nginx
```

## R Packages

## Python Packages

```bash
$ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
$ chmod 755 Miniconda3-latest-Linux-x86_64.sh
$ sudo ./Miniconda3-latest-Linux-x86_64.sh
```

## Other

# Folder Structure

# Usage

# Others
