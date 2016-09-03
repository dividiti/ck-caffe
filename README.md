# Collective Knowledge repository for optimising Caffe-based designs

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
 
## Contributors

* Anton Lokhmotov, [dividiti](http://dividiti.com)
* Grigori Fursin, [dividiti](http://dividiti.com) / [cTuning foundation](http://ctuning.org)
* Unmesh Bordoloi, [General Motors](http://gm.com)

## License
* [BSD](https://github.com/dividiti/ck-caffe/blob/master/LICENSE) (3 clause)

## Status
Under development.


# Installing CK-Caffe on Ubuntu

Before installing CK-Caffe on the target system, several libraries and programs
should be installed. So far, instructions for the following Linux flavours are
available:

- [Ubuntu](#installing-deps-ubuntu)
- [Gentoo](#installing-deps-gentoo)

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

<a name="installing-deps-ubuntu"></a>
## Installing CK-Caffe dependencies on Ubuntu

Installing the dependencies is recommended via `'apt install'` (for standard
Ubuntu packages), or `'pip install'` (for standard Python packages, typically
of more recent versions than those available via `'apt install'`).  This can be
simply done by opening a Linux shell and copying-and-pasting commands from
cells below.

### Installing core CK dependencies

Collective Knowledge has only two dependencies: [Python](http://python.org)
(2.x and 3.x) and [Git](https://git-scm.com), which can be installed as
follows:

```
# apt install  \
    python-dev \
    git
```

### Installing common dependencies

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

### Installing Caffe dependencies

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

### Installing optional dependencies

```
# apt install \
    libatlas-base-dev \
# pip install \
    jupyter \
    pandas numpy scipy matplotlib \
    scikit-image scikit-learn \
    pyyaml
```

### Checking all dependencies

You can check all the dependencies on an Ubuntu system by running this
[notebook](https://github.com/dividiti/ck-caffe/blob/master/script/check-deps/check_deps.ipynb).
(View the output of this notebook on an [Odroid
XU3](http://odroid.com/dokuwiki/doku.php?id=en:odroid-xu3) board [here](
https://github.com/dividiti/ck-caffe/blob/master/script/check-deps/check_deps.xu3.20160808.ipynb).)

### Installing CK

Please proceed to <a href="#installing-ck">installing CK</a>.

<a name="installing-deps-gentoo"></a>
## Installing CK-Caffe dependencies on Gentoo

Installing the dependencies is recommended via `'emerge'` (for standard
Gentoo packages), or `'pip install'` (for standard Python packages, typically
of more recent versions than those available via `'emerge'`).  This can be
simply done by opening a Linux shell and copying-and-pasting commands from
cells below.

### Installing core CK dependencies

Collective Knowledge has only two dependencies: [Python](http://python.org)
(2.x and 3.x) and [Git](https://git-scm.com), which can be installed as
follows:

```
# emerge  \
    dev-lang/python \
    dev-vcs/git
```

### Installing common dependencies

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

### Installing Caffe dependencies

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

### Installing optional dependencies

```
# emerge \
    sci-libs/atlas
# pip install \
    jupyter \
    pandas numpy scipy matplotlib \
    scikit-image scikit-learn \
    pyyaml
```

### Installing CK

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
V1.7.4dev
$ python -c "import ck.kernel as ck; print (ck.__version__)"
V1.7.4dev
```

## Installing CK Caffe

We are now ready to install and run CK-Caffe:
```
$ ck pull repo:ck-caffe --url=https://github.com/dividiti/ck-caffe
$ ck run program:caffe
```

## Sample run

**TBD**


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
## Our publications related to this project and crowd-tuning

- [https://github.com/ctuning/ck/wiki/Publications Reference with BibTex]
