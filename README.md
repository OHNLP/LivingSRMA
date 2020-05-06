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

For the Ubuntu 18.04 system, update and install

```bash
$ sudo apt update
$ sudo apt install nginx
```

## Nginx

Before having a domain name, we can use the self-signed certification: 

```bash
$ sudo mkdir /etc/nginx/ssl/ && sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj "/C=US/ST=Minnesota/L=Rochester/O=LINMA/OU=ATA/CN=LNMAServer" -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt
```

Then edit config file:

```bash
$ sudo vim /etc/nginx/sites-enabled/default
```

add ssl related configs in server:

    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;

and then restart nginx:

    sudo service nginx restart

## MySQL database

We can use local MySQL as the start.

## R Packages

To install the backend R packages, install some dependency packages first:

```bash
$ sudo apt install jags libglpk-dev libxml2-dev libcurl4-openssl-dev libssl-dev build-essential libcurl4-gnutls-dev
```

Then add CRAN repository:

```bash
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
$ sudo add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/'
$ sudo apt update
$ sudo apt install r-base
$ sudo apt install r-base --fix-missing
```

Then install packages for LNMA (for whole system). The `dmetar` package is required to calculate the SUCRA, but this can also be done by Python.

```bash
$ sudo R

> install.packages('netmeta')
> install.packages('jsonlite')
> install.packages("rjags")
> install.packages("gemtc")
> install.packages('tableHTML')
> install.packages('Rglpk')
> install.packages("devtools")
> devtools::install_github("MathiasHarrer/dmetar")

```

### BUGSnet

The BUGSnet packages requires more packages, first install the following dependency:

```bash
$ sudo add-apt-repository ppa:jonathonf/gcc-7.1
$ sudo apt-get update
$ sudo apt-get install gcc-7 g++-7
$ sudo apt-get install gfortran-7
```

Then install the following:

```bash
$ sudo R
> install.packages('igraph')
> install.packages(c("remotes", "knitr"))
> remotes::install_github("audrey-b/BUGSnet@v1.0.3", upgrade = TRUE, build_vignettes = TRUE)
```

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
