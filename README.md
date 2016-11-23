# Collective Knowledge repository for optimising Caffe-based designs

## Introduction

[CK-Caffe](https://github.com/dividiti/ck-caffe) is an open framework for
collaborative and reproducible optimisation of convolutional neural networks.
It's based on the [Caffe](http://caffe.berkeleyvision.org) framework from the
Berkeley Vision and Learning Center ([BVLC](http://bvlc.eecs.berkeley.edu)) and
the [Collective Knowledge](http://cknowledge.org) framework from the [cTuning
Foundation](http://ctuning.org). In essence, CK-Caffe is simply a suite of
convenient wrappers for building, evaluating and optimising performance of
Caffe.

As outlined in our [vision](http://dx.doi.org/10.1145/2909437.2909449), we
invite the community to collaboratively design and optimize convolutional
neural networks to meet the performance, accuracy and cost requirements for
deployment on a range of form factors - from sensors to self-driving cars. To
this end, CK-Caffe leverages the key capabilities of CK to crowdsource
experimentation across diverse platforms, CNN designs, optimization
options, and so on; exchange experimental data in a flexible JSON-based format;
and apply leading-edge predictive analytics to extract valuable insights from
the experimental data.

## License
* [BSD](https://github.com/dividiti/ck-caffe/blob/master/LICENSE) (3 clause)

## Authors/contributors

* Anton Lokhmotov, [dividiti](http://dividiti.com)
* Grigori Fursin, [dividiti](http://dividiti.com) / [cTuning foundation](http://ctuning.org)
* Unmesh Bordoloi, [General Motors](http://gm.com)

## Quick/minimal installation (Ubuntu)

### General dependencies
Installing dependencies via apt:

```
$ sudo apt install coreutils \
                   build-essential \
                   make \
                   cmake \
                   wget \
                   python \
                   python-pip
```

### Caffe dependencies
```
$ sudo apt install libboost-all-dev \
                   libgflags-dev \
                   libgoogle-glog-dev \
                   libhdf5-serial-dev \
                   liblmdb-dev \
                   libleveldb-dev \
                   libprotobuf-dev \
                   protobuf-compiler \
                   libsnappy-dev \
                   libopencv-dev
$ sudo pip install protobuf
```

### CK installation

```
$ sudo pip install ck
$ ck version
```

### Installing CK-Caffe repository

```
$ ck pull repo:ck-caffe --url=https://github.com/dividiti/ck-caffe
```

### Installing Caffe and all dependencies

The first time you run caffe benchmark, CK will 
build and install all missing dependencies for your machine,
download required data sets and will start benchmark:


```
$ ck run program:caffe
```

### Testing installation via image classification

```
 $ ck compile program:caffe-classification --speed
 $ ck run program:caffe-classification
```

Note, that you will be asked to select a jpeg image from available CK data sets.
We added standard demo images (cat.jpg, catgrey.jpg, fish-bike.jpg, computer_mouse.jpg)
to the ['ctuning-datasets-min' repository](https://github.com/ctuning/ctuning-datasets-min).

You can list them via
```
 $ ck pull repo:ctuning-datasets-min
 $ ck search dataset --tags=dnn
```

### Testing beta crowd-benchmarking
It is now possible to participate in crowd-benchmarking of Caffe
(early prototype):
```
$ ck crowdbench caffe --user={your email or ID to acknowledge contributions} --env.CK_CAFFE_BATCH_SIZE=2
```

You can also use this [Android app](https://play.google.com/store/apps/details?id=openscience.crowdsource.video.experiments)
to crowdsource benchmarking of ARM-based Caffe libraries for image recognition (beta version).

You can see continuously aggregated results in the 
[public Collective Knowledge repository](http://cknowledge.org/repo)
under 'crowd-benchmark Caffe library' scenario.

Note, that this is an on-going, heavily evolving and long-term project
to enable collaborative and systematic benchmarking
and tuning of realistic workloads across diverse hardware 
([ARM TechCon'16 talk](http://schedule.armtechcon.com/session/know-your-workloads-design-more-efficient-systems), 
[ARM TechCon'16 demo](https://github.com/ctuning/ck/wiki/Demo-ARM-TechCon'16), 
[DATE'16](http://tinyurl.com/zyupd5v), [CPC'15](http://arxiv.org/abs/1506.06256)).
We also plan to add crowd-benchmarking and crowd-tuning of Caffe, TensorFlow 
and other DNN frameworks to our 
[Android application](https://play.google.com/store/apps/details?id=openscience.crowdsource.experiments) 
soon - please stay tuned!

```

### Advanced Installation

You can read about advanced CK-Caffe installation (for example, for Android) [here](http://github.com/dividiti/ck-caffe/wiki/Installation)

## Examples

### Compare accuracy of 4 CNNs

In this [Jupyter
notebook](https://github.com/dividiti/ck-caffe/blob/master/script/explore-accuracy/explore_accuracy.20160808.ipynb),
we compare the Top-1 and Top-5 accuracy of 4 CNNs:

- [AlexNet](https://github.com/BVLC/caffe/tree/master/models/bvlc_alexnet)
- [SqueezeNet 1.0](https://github.com/DeepScale/SqueezeNet/tree/master/SqueezeNet_v1.0)
- [SqueezeNet 1.1](https://github.com/DeepScale/SqueezeNet/tree/master/SqueezeNet_v1.1)
- [GoogleNet](https://github.com/BVLC/caffe/tree/master/models/bvlc_googlenet)

on the [Imagenet validation set](http://academictorrents.com/details/5d6d0df7ed81efd49ca99ea4737e0ae5e3a5f2e5) (50,000 images).

We have thus independently verified that on this data set [SqueezeNet](https://arxiv.org/abs/1602.07360) matches (and even slightly exceeds) the accuracy of [AlexNet](https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf).

The experimental data is stored in the main CK-Caffe repository under '[experiment](https://github.com/dividiti/ck-caffe/tree/master/experiment)'.

### Compare performance of 4 CNNs on Chromebook 2

This
[notebook](https://github.com/dividiti/ck-caffe-explore-batch-size-chromebook2/blob/master/script/explore-batch-size/explore_batch_size.20160809.ipynb)
investigates effects on inference performance of varying the batch size:

- across the same 4 **CNNs**;
- with 4 BLAS **libraries**:
  - [CPU] [OpenBLAS](https://github.com/xianyi/OpenBLAS) 0.2.18 (one thread per core);
  - [GPU] [clBLAS](https://github.com/clMathLibraries/clBLAS) 2.4 (OpenCL 1.1 compliant);
  - [GPU] [CLBlast](https://github.com/CNugteren/CLBlast) dev (35623cd > 0.8.0);
  - [GPU] [CLBlast](https://github.com/CNugteren/CLBlast) dev (35623cd > 0.8.0) with Mali-optimized [overlay](https://github.com/intelfx/CLBlast/tree/mali-overlay) (641bb07);
- on the [Samsung Chromebook 2](http://www.samsung.com/us/computing/chromebooks/under-12/samsung-chromebook-2-11-6-xe503c12-k01us/) **platform**:
  - [CPU] quad-core ARM Cortex-A15 (@ 1900 MHz);
  - [GPU] quad-core ARM Mali-T628 (@ 600 MHz);
  - [GPU] OpenCL driver 6.0 (r6p0); OpenCL standard 1.1.

Finally, this
[notebook](https://github.com/dividiti/ck-caffe-explore-batch-size-chromebook2/blob/master/script/compare-time-fw/compare_time_fw.20160809.ipynb)
compares the best performance per image across the CNNs and BLAS libraries.
When using OpenBLAS, SqueezeNet 1.1 is 2 times faster than SqueezeNet 1.0 and
2.4 times faster than AlexNet, broadly in line with expectations set by the
[SqueezeNet](http://arxiv.org/abs/1602.07360) paper.

When using OpenCL BLAS libraries, however, SqueezeNet 1.0 is not necessarily
faster than AlexNet, despite roughly 500 times reduction in the weights' size.
This suggests that an optimal network design for a given task may depend on the
software stack as well as on the hardware platform. Moreover, design choices
may well shift over time, as software matures and new hardware becomes
available. That's why we believe it is necessary to leverage community effort
to collectively grow design and optimisation knowledge.

The experimental data and visualisation notebooks are stored in a separate
repository which can be obtained as follows:
```
ck pull repo:ck-caffe-explore-batch-size-chromebook2 \
    --url=https://github.com/dividiti/ck-caffe-explore-batch-size-chromebook2.git
```
 


# Installing CK-Caffe (on desktop)

Before installing CK-Caffe on the target system, several libraries and programs
should be installed. So far, instructions for the following Linux flavours are
available:

- [Ubuntu](#ubuntu-installing-deps)
- [Gentoo](#gentoo-installing-deps)
- [Yocto](#yocto-installing-deps)

## Conventions

In this guide, shell commands prefixed with `'$'` should be run as user,
whereas commands prefixed with `'#'` should be run as root (or as user with
`'sudo'`).

For example, to install the `'pip'` package manager and then
[Jupyter](http://jupyter.org) on Ubuntu, run as root:

```
# apt install python-pip
# pip install jupyter
```
or as user:
```
$ sudo apt install python-pip
$ sudo -H pip install jupyter
```

<a name="ubuntu-installing-deps"></a>
## [Ubuntu] Installing CK-Caffe dependencies

Installing the dependencies is recommended via `'apt install'` (for standard
Ubuntu packages), or `'pip install'` (for standard Python packages, typically
of more recent versions than those available via `'apt install'`).  This can be
simply done by opening a Linux shell and copying-and-pasting commands from
cells below.

### [Ubuntu] Installing core CK dependencies

Collective Knowledge has only two dependencies: [Python](http://python.org)
(2.x and 3.x) and [Git](https://git-scm.com), which can be installed as
follows:

```
# apt install  \
    python-dev \
    git
```

### [Ubuntu] Installing common dependencies

Some CK packages and Caffe require common Linux utilities (e.g.
[make](https://www.gnu.org/software/make), [cmake](http://cmake.org),
[wget](https://www.gnu.org/software/wget)), which can be installed as follows:

```
# apt install \
    coreutils \
    build-essential \
    make \
    cmake \
    wget \
    python-pip
```

### [Ubuntu] Installing Caffe dependencies

The BVLC Caffe framework has quite a few dependencies. If you've already run
Caffe on your machine, it's likely that you've already satisfied all of them.
If not, however, you can easily install them [in one
gollop](https://books.google.co.uk/books?isbn=0224046918) as follows:

```
# apt install \
    libboost-all-dev \
    libgflags-dev \
    libgoogle-glog-dev \
    libhdf5-serial-dev \
    liblmdb-dev \
    libleveldb-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libsnappy-dev \
    libopencv-dev
# pip install \
    protobuf
```

### [Ubuntu] Installing optional dependencies

```
# apt install \
    libatlas-base-dev
# pip install \
    jupyter \
    pandas numpy scipy matplotlib \
    scikit-image scikit-learn \
    pyyaml
```

### [Ubuntu] Checking all dependencies

You can check all the dependencies on an Ubuntu system by running this
[notebook](https://github.com/dividiti/ck-caffe/blob/master/script/check-deps/check_deps.ipynb).
(View the output of this notebook on an [Odroid
XU3](http://odroid.com/dokuwiki/doku.php?id=en:odroid-xu3) board [here](
https://github.com/dividiti/ck-caffe/blob/master/script/check-deps/check_deps.xu3.20160808.ipynb).)

### [Ubuntu] Installing CK

Please proceed to <a href="#installing-ck">installing CK</a>.

<a name="gentoo-installing-deps"></a>
## [Gentoo] Installing CK-Caffe dependencies

Installing the dependencies is recommended via `'emerge'` (for standard
Gentoo packages), or `'pip install'` (for standard Python packages, typically
of more recent versions than those available via `'emerge'`).  This can be
simply done by opening a Linux shell and copying-and-pasting commands from
cells below.

### [Gentoo] Installing core CK dependencies

Collective Knowledge has only two dependencies: [Python](http://python.org)
(2.x and 3.x) and [Git](https://git-scm.com), which can be installed as
follows:

```
# emerge  \
    dev-lang/python \
    dev-vcs/git
```

### [Gentoo] Installing common dependencies

Some CK packages and Caffe require common Linux utilities (e.g.
[make](https://www.gnu.org/software/make), [cmake](http://cmake.org),
[wget](https://www.gnu.org/software/wget)), which can be installed as follows:

```
# emerge \
    sys-devel/gcc \
    sys-devel/make \
    dev-util/cmake \
    net-misc/wget \
    dev-python/pip
```

### [Gentoo] Installing Caffe dependencies

The BVLC Caffe framework has quite a few dependencies. If you've already run
Caffe on your machine, it's likely that you've already satisfied all of them.
If not, however, you can easily install them [in one
gollop](https://books.google.co.uk/books?isbn=0224046918) as follows:

```
# emerge \
    dev-libs/boost \
    dev-util/boost-build \
    dev-cpp/gflags \
    dev-cpp/glog \
    sci-libs/hdf5 \
    dev-db/lmdb \
    dev-libs/leveldb \
    dev-libs/protobuf \
    app-arch/snappy \
    media-libs/opencv
# pip install \
    protobuf
```

### [Gentoo] Installing optional dependencies

```
# emerge \
    sci-libs/atlas
# pip install \
    jupyter \
    pandas numpy scipy matplotlib \
    scikit-image scikit-learn \
    pyyaml
```

### [Gentoo] Installing CK

Please proceed to <a href="#installing-ck">installing CK</a>.


<a name="yocto-installing-deps"></a>
## [Yocto] Installing CK-Caffe dependencies

**NB:** This section is work-in-progress.

**NB:** Not all CK-Caffe dependencies can be automatically installed on Yocto.

Add the following Bitbake layers to your `bblayers.conf` (e.g. `build/build/conf/bblayers.conf`):
```
BBLAYERS ?= " \
  ${TOPDIR}/../poky/meta \
  ${TOPDIR}/../poky/meta-yocto \
  ${TOPDIR}/../poky/meta-yocto-bsp \
  ...
  ${TOPDIR}/../meta-linaro/meta-linaro-toolchain \
  ${TOPDIR}/../meta-openembedded/meta-oe \
  ${TOPDIR}/../meta-openembedded/meta-networking \
  ${TOPDIR}/../meta-openembedded/meta-multimedia \
  ${TOPDIR}/../meta-openembedded/meta-python \
  "
```

### [Yocto] Installing core CK dependencies

Collective Knowledge has only two dependencies: [Python](http://python.org)
(2.x and 3.x) and [Git](https://git-scm.com).

Add the following to your image recipes:
```
# Core CK dependencies.
IMAGE_INSTALL_append... = " \
    python \
    git \
"
```

### [Yocto] Installing common dependencies

Some CK packages and Caffe require common Linux utilities (e.g.
[make](https://www.gnu.org/software/make), [cmake](http://cmake.org),
[wget](https://www.gnu.org/software/wget)).

Add the following to your image recipes:

```
# Common CK-Caffe dependencies.
IMAGE_INSTALL_append... = " \
    gcc \
    make \
    cmake \
    wget \
    zlib \
    python-setuptools \
    python-pip \
"
```

### [Yocto] Installing Caffe dependencies

The BVLC Caffe framework has quite a few dependencies. If you've already run
Caffe on your machine, it's likely that you've already satisfied all of them.
If not, however, you may need to install some of them manually.

#### [Yocto] Installing Caffe dependencies automatically

You can install _some_ of the Caffe dependencies automatically by adding the
following to your image recipes:

```
# Caffe dependencies.
IMAGE_INSTALL_append... = " \
    boost \
    libunwind \
    glog \
    protobuf \
    leveldb \
    opencv \
    opencv-samples \
    libopencv-core \
    libopencv-highgui \
    libopencv-imgproc \
    libopencv-features2d \
    libopencv-calib3d \
    libopencv-flann \
    libopencv-ocl \
"
```
**NB:** This list probably overapproximates the real dependencies.

Also, run:
```
# pip install \
    protobuf
```

#### [Yocto] Installing Caffe dependencies manually

##### [Yocto] hdf5

**TODO**

##### [Yocto] lmdb

```
$ cd tmp/
$ wget https://github.com/LMDB/lmdb/archive/LMDB_0.9.18.tar.gz
$ tar xvzf LMDB_0.9.18.tar.gz
$ cd lmdf-LMDB-0.9.18/libraries/liblmdb
$ make && make install
```
**NB:** Installs to `/usr/local/` by default.

##### [Yocto] gflags
```
$ cd /tmp
$ wget https://github.com/gflags/gflags/archive/v2.1.2.tar.gz
$ cd gflags-2.1.2
$ mkdir -p build && cd build
$ cmake .. -DCMAKE_CXX_FLAGS=-fPIC
```

##### [Yocto] snappy
```
$ cd /tmp
$ wget https://github.com/google/snappy/releases/download/1.1.3/snappy-1.1.3.tar.gz
$ tar xvzf snappy-1.1.3.tar.gz
$ cd snappy-1.1.3
$ ./configure
$ make -j4 && make install
```

**NB:** Installs to `/usr/local/` by default.


### [Yocto] Installing CK

Please proceed to <a href="#installing-ck">installing CK</a>.

<a name="installing-ck"></a>
## Installing CK

Clone CK from GitHub into e.g. `'$HOME/CK'`:
```
$ git clone https://github.com/ctuning/ck.git $HOME/CK
```

Add the following to your `'$HOME/.bashrc'` and run `'source ~/.bashrc'` after that:

```
# Collective Knowledge.
export CK_ROOT=${HOME}/CK
export CK_REPOS=${HOME}/CK_REPOS
export CK_TOOLS=${HOME}/CK_TOOLS
export PATH=${HOME}/CK/bin:$PATH
```

Install the Python interface to CK:
```
$ cd $HOME/CK && sudo python setup.py install
```

Test that both the command line and Python interfaces work:
```
$ ck version
V1.8.2dev
$ python -c "import ck.kernel as ck; print (ck.__version__)"
V1.8.2dev
```

## Installing CK Caffe

We are now ready to install and run CK-Caffe:
```
$ ck pull repo:ck-caffe --url=https://github.com/dividiti/ck-caffe
$ ck run program:caffe
```

## Testing installation via image classification

```
 $ ck compile program:caffe-classification --speed
 $ ck run program:caffe-classification
```

Note, that you will be asked to select a jpeg image from available CK data sets.
We added standard demo images (cat.jpg, catgrey.jpg, fish-bike.jpg, computer_mouse.jpg)
to the ['ctuning-datasets-min' repository](https://github.com/ctuning/ctuning-datasets-min).
You can list them via
```
 $ ck pull repo:ctuning-datasets
-min
 $ ck search dataset --tags=dnn
```

## Crowd-benchmarking
It is now possible to participate in crowd-benchmarking of Caffe
(early prototype):
```
$ ck crowdbench caffe --user={your email or ID to acknowledge contributions} --env.CK_CAFFE_BATCH_SIZE=2
```

You can also use this [Android app](https://play.google.com/store/apps/details?id=openscience.crowdsource.video.experiments)
to crowdsource benchmarking of ARM-based Caffe libraries for image recognition (beta version).

You can see continuously aggregated results in the 
[public Collective Knowledge repository](http://cknowledge.org/repo)
under 'crowd-benchmark Caffe library' scenario.

Note, that this is an on-going, heavily evolving and long-term project
to enable collaborative and systematic benchmarking
and tuning of realistic workloads across diverse hardware 
([ARM TechCon'16 talk](http://schedule.armtechcon.com/session/know-your-workloads-design-more-efficient-systems), 
[ARM TechCon'16 demo](https://github.com/ctuning/ck/wiki/Demo-ARM-TechCon'16), 
[DATE'16](http://tinyurl.com/zyupd5v), [CPC'15](http://arxiv.org/abs/1506.06256)).
We also plan to add crowd-benchmarking and crowd-tuning of Caffe, TensorFlow 
and other DNN frameworks to our 
[Android application](https://play.google.com/store/apps/details?id=openscience.crowdsource.experiments) 
soon - please stay tuned!

## Building Caffe for Android

CK automates building of workflows and packages 
(high-level version of CMake but in Python and with JSON API).
We provided all packages needed to build Caffe for Android
(used in our above Android application to crowd-benchmark
and crowd-tune Caffe across diverse hardware).

CK supports both Google or CrystaX Android NDK which you need 
to download and unzip in your home directory 
to be able to compile Caffe for Android:

* https://developer.android.com/ndk/index.html
* https://www.crystax.net/en/android/ndk

Normally, you should be able to build CPU-version of Caffe via CK 
targeting ARM64 in one click:
```
$ ck install package:lib-caffe-bvlc-master-cpu-android --target_os=android21-arm64
```

You can target older version of ARM or other micro-architecture by
changing --target_os (see "ck list os"):
```
$ ck install package:lib-caffe-bvlc-master-cpu-android --target_os=android21-arm
```

CK should detect available Android NDK and start building all dependencies
including Caffe itself.

If build finished successfully, you can then try to compile image classification
example as following:
```
$ ck compile --speed program:caffe-classification --target_os=android21-arm64
```

TODO: we need to be able to run classification on Android via CK 
     (for now you need to manually copy all files to /data/local/tmp via adb).

TODO: we need to add selection of different ABI to CK pipeline, not just default ones (via OS module)!

Please, send your feedback (problems or success) to http://groups.google.com/group/collective-knowledge .

## Misc hints

### Creating dataset subsets

The ILSVRC2012 validation dataset contains 50K images. For quick experiments,
you can create a subset of this dataset, as follows. Run:

```
$ ck install package:imagenet-2012-val-lmdb-256
```

When prompted, enter the number of images to convert to LMDB, say, `N` = 100.
The first `N` images will be taken.


## Setting environment variables

To set environment variables for running the program, use e.g.:

```
$ ck run program:caffe --env.CK_CAFFE_BATCH_SIZE=1 --env.CK_CAFFE_ITERATIONS=10
```

## Related projects and initiatives

We are working with the community to unify and crowdsource performance analysis 
and tuning of various DNN frameworks (or any realistic workload) 
using Collective Knowledge Technology:
* [CK-TensorFlow](https://github.com/dividiti/ck-tensorflow)
* [CK-TinyDNN](https://github.com/ctuning/ck-tiny-dnn)
* [Android app for DNN crowd-benchmarking and crowd-tuning](https://play.google.com/store/apps/details?id=openscience.crowdsource.video.experiments)
* [CK-powered ARM workload automation](https://github.com/ctuning/ck-wa)

## Open R&D challenges

We use crowd-benchmarking and crowd-tuning of such realistic workloads across diverse hardware for 
[open academic and industrial R&D challenges](https://github.com/ctuning/ck/wiki/Research-and-development-challenges.mediawiki) - 
join this community effort!

## Related Publications with long term vision

* <a href="https://github.com/ctuning/ck/wiki/Publications">All references with BibTex</a>
