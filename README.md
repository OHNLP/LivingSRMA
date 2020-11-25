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
$ sudo apt upgrade
```

## Nginx

Before having a domain name, we can use the self-signed certification: 

```bash
$ sudo apt install nginx
$ sudo mkdir /etc/nginx/ssl/ && sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj "/C=US/ST=Minnesota/L=Rochester/O=LINMA/OU=ATA/CN=LNMAServer" -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt
```

Then, edit config file:

```bash
$ sudo vim /etc/nginx/sites-enabled/default
```

Then, add ssl related configs in server:

```bash
listen 443 ssl;
ssl_certificate /etc/nginx/ssl/nginx.crt;
ssl_certificate_key /etc/nginx/ssl/nginx.key;
```
and then restart nginx:

```bash
$ sudo service nginx restart
```

### SSL Certification

```bash
$ sudo apt-get update
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository universe
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt-get update
$ sudo apt-get install certbot python3-certbot-nginx
```

Add certifaction

```bash
$ sudo certbot --nginx 
```

## MySQL database

We can use local MySQL as the start.
Please follow the instruction on https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/ to install the MySQL 8.x:

```bash
$ sudo wget https://dev.mysql.com/get/mysql-apt-config_0.8.15-1_all.deb
$ sudo dpkg -i mysql-apt-config_0.8.15-1_all.deb
```
when we run above command like below prompt will open, click on Ok.
Then, update the system and install packages.
During installation, set the root password and use strong password encryption.

```bash
$ sudo apt-get update
$ sudo apt-get install mysql-server
```

### password policy

### Users and Database

```bash
mysql> create database lnma;
mysql> create user lnma@localhost identified with mysql_native_password by 'LNMA_password_12#$';
mysql> grant all on lnma.* to lnma@localhost;
```


## R Packages

To install the backend R packages, install some dependency packages first:

```bash
$ sudo apt install jags libglpk-dev libxml2-dev libcurl4-openssl-dev libssl-dev build-essential libcurl4-gnutls-dev
```

Then add CRAN repository, the last line may be not required if no errors.

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

> install.packages('meta')
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

The BUGSnet packages requires more packages, install the following:

```bash
$ sudo R
> install.packages('igraph')
> install.packages(c("remotes", "knitr"))
> remotes::install_github("audrey-b/BUGSnet@v1.0.3", upgrade = TRUE, build_vignettes = TRUE)
```

## Python Packages

First, we use miniconda to manage our virtual environments. Since the server won't have multiple users, this can be installed on the user folder.

```bash
$ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
$ chmod 755 Miniconda3-latest-Linux-x86_64.sh
$ ./Miniconda3-latest-Linux-x86_64.sh
```

May need to install mysql lib first:

```bash
$ sudo apt-get install libmysqlclient-dev
```

```bash
(py37lnma) $ pip install mysqlclient
```
### 

## Other

# Folder Structure

## $PROJECT_FOLDER/instance
After install the packages, an instance folder is needed for the flask web app (`$PROJECR_FOLDER` is where the lnma code is).
In addition, the a `pubdata` folder is needed for each NMA project.

```bash
cd $PROJECT_FOLDER
mkdir instance
mkdir instance/pubdata
cd instance
vim config.py
```

The content of the config.py could be as follows.
The password for the watcher is not blank, ask adminstrator.

```
DEBUG = True
SECRET_KEY = b'9s8@js-7sJx8-hXs73-&62hx-2aNxh'
DB_SERVER = 'localhost'

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'mysql://lnma:LNMA_password_12#$@127.0.0.1:3306/lnma'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# FILE STORAGE
PATH_FILE_STORAGE = '/data/lnma'

#
TMP_FOLDER = '/dev/shm/lnma'
UPLOAD_FOLDER = '/dev/shm/lnma'
UPLOAD_FOLDER_PDFS = '/dev/shm/lnma'

# For watcher settings
WATCHER_EMAIL_USERNAME = 'lisrbot2020@gmail.com'
WATCHER_EMAIL_PASSWORD = ''
```

## /dev/shm/lnma
LNMA use shm folder to make full use of the memory and improve the R/W performance:

```bash
mkdir /dev/shm/lnma
```

# RCT identifier

First, create a venv for RCT identifier:

```bash
conda create rctpy36 python=3.6
conda activate rctpy36
```

Then, install the package and upgrade the Keras to 2.1.6 to fix a bug.

```bash
(rctpy36) pip install -U https://github.com/ijmarshall/robotsearch/archive/master.zip
(rctpy36) pip install Keras==2.1.6
```

Last, install the web api package and wsgi server. The server script could found in the repo.

```bash
(rctpy36) pip install uvicorn
(rctpy36) pip install fastapi

(rctpy36) ./run.sh
```

# Data Structure

## Table `papers`

The `ss_st`, `ss_pr`, and `ss_rs` columns indicate which state a study is during screening.

- Screening State (ss) Start (st): for study screening, indicating where the study comes from: 
   - b10: batch import/search
   - b11: other, 
   - b12: other manual way, 
   - a10: automatic way, 
   - a11: auto search

- Screening State (ss) Process (pr): for study screening, indicating which process the study is in: 
   - p30: loaded meta info, 
   - p40: checked unique, 
   - p50: checked title, 
   - p60: checked full text, 
   - p70: checked sr, 
   - p80: checked ma

- Screening State (ss) Result (rs): for study screening, indicating what result for the study: 
   - e11: excluded for duplicate, 
   - e12: excluded for title, 
   - e13: excluded for full text, 
   - e14: excluded for updates, 
   - f1: included in sr, 
   - f2: included in ma, 
   - f3: included in sr and ma

# Usage

## Database migration

To copy the table schema from local server to the development server, we use flask-migrate to handle the schema update.

```bash
(py37lnma) $ pip install Flask-Migrate
```

On the dev side, we need to follow the tutorial on https://flask-migrate.readthedocs.io/en/latest/

```bash
$ export FLASK_APP=lnma
$ flask db init
$ flask db migrate -m "Initial migration."
$ flask db upgrade
```

After the first time, we only need to run migrate and upgrade in the future.

When modified the `model.py` in the development env, run the following:

```bash
$ export FLASK_APP=lnma
$ flask db migrate
$ flask db upgrade
```

On the server side, we don't need to init the migration folder.
The only thing we need to do is upgrade:

```bash
(py37lnma) $ flask db upgrade
```
# Update log

## 2020-10-07

Fixed a lot of things. Add a reverse parser for the dev site on development server for checking detailed log data.

## 2020-09-20

To support different types of measure of effects in SoF PMA, the followings are added:

1. URL parameter `msrs` for softable_pma and default values;
2. `tb_simple_sofpma` add `default_measure` and `measure_list` to hold the measures for rending;
3. Setting measures before init the `tb_simple_sofpma`.

And for the external base:

1. the data structure has to be changed to support HR.
2. a lot -_-|||