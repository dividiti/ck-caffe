Collective Knowledge repository for optimising Caffe 
====================================================

Status
======
Unstable - heavy development phase

Prerequisites
=============
* Collective Knowledge framework ([@GitHub](http://github.com/ctuning/ck))

To satisfy the Caffe dependencies on Ubuntu:
```
sudo apt-get install \
    build-essential \
    cmake \
    git \
    wget \
    libatlas-base-dev \
    libboost-all-dev \
    libgflags-dev \
    libgoogle-glog-dev \
    libhdf5-serial-dev \
    libleveldb-dev \
    liblmdb-dev \
    libopencv-dev \
    libprotobuf-dev \
    libsnappy-dev \
    protobuf-compiler \
    python-dev \
    python-numpy \
    python-pip \
    python-scipy \
    python-matplotlib
```
To satisfy the Python interface dependencies (needed for some compressed networks):
```
sudo -H pip install \
    scikit-image \
    protobuf \
    pyyaml
```

Authors
=======

* Anton Lokhmotov, dividiti (UK)
* Grigori Fursin, dividiti (UK)

License
=======
* BSD, 3-clause

Installation
============
```
 $ ck pull repo --url=https://github.com/dividiti/ck-caffe
```
or
```
 $ ck pull repo --url=git@github.com:dividiti/ck-caffe
```

## Misc

### Creating dataset subsets

The ILSVRC2012 validation dataset contains 50K images. For quick experiments, you can create a subset of this dataset, as follows. Run:

```
$ ck install package:imagenet-2012-val-lmdb-256
```
When prompted, enter the number of images to convert to LMDB, say, `N` = 100. The first `N` images will be taken.


## Setting environment variables

To set environment variables for running the program, use e.g.:

```
$ ck run program:caffe --env.CK_CAFFE_BATCH_SIZE=1 --env.CK_CAFFE_ITERATIONS=10
```
