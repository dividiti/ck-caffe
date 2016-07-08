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




Misc
====
If you want to use different number of images, you can differentiate environment by specifying
extra version during installation, for example:
$ ck install package:imagenet-2012-val-lmdb-256-no-shuffle --extra_version=_99images
