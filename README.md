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

### Compare accuracy of four CNN architectures

In this [Jupyter
notebook](http://nbviewer.jupyter.org/github/dividiti/ck-caffe/blob/master/script/explore-accuracy/explore_accuracy.20160808.ipynb),
we compare the Top-1 and Top-5 accuracy of four CNN architectures:

- [AlexNet](https://github.com/BVLC/caffe/tree/master/models/bvlc_alexnet)
- [SqueezeNet 1.0](https://github.com/DeepScale/SqueezeNet/tree/master/SqueezeNet_v1.0)
- [SqueezeNet 1.1](https://github.com/DeepScale/SqueezeNet/tree/master/SqueezeNet_v1.1)
- [GoogleNet](https://github.com/BVLC/caffe/tree/master/models/bvlc_googlenet)

on the [Imagenet validation set](http://academictorrents.com/details/5d6d0df7ed81efd49ca99ea4737e0ae5e3a5f2e5) (50,000 images).

We have thus independently verified that on this data set [SqueezeNet](https://arxiv.org/abs/1602.07360) matches and slightly exceeds the accuracy of [AlexNet](https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf).

The experimental data is stored in the main CK-Caffe repository under '[experiment](https://github.com/dividiti/ck-caffe/tree/master/experiment)'.

### Compare performance of four CNN architectures on Chromebook 2

**TBD**

 
## Authors

* Anton Lokhmotov, [dividiti](http://dividiti.com) (UK)
* Grigori Fursin, [dividiti](http://dividiti.com) (UK)

## License
* [BSD](https://github.com/dividiti/ck-caffe/blob/master/LICENSE) (3 clause)

## Status
Under development.


# Installing CK-Caffe on Ubuntu

Before installing CK-Caffe on the target system, several libraries and programs
should be installed.  This can be simply done by opening a Linux shell and
copying-and-pasting commands from cells below.  Installing the dependencies is
recommended via `'apt install'` (for standard Ubuntu packages), or `'pip
install'` (for standard Python packages, typically of more recent versions than
those available via `'apt install'`).

## Conventions

In this guide, shell commands prefixed with `'$'` should be run as user,
whereas commands prefixed with `'#'` should be run as root (or as user with
`'sudo'`).

For example, to install the `'pip'` package manager and then
[Jupyter](http://jupyter.org), run as root:

```
# apt install pip-install
# pip install jupyter
```
or as user:
```
$ sudo apt install pip-install
$ sudo -H pip install jupyter
```

## Installing dependencies

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
    pip-install
```

### Installing Caffe dependencies

The BVLC Caffe framework has quite a few dependencies. If you've already run
Caffe on your machine, it's likely that you've already satisfied all of them.
If not, however, you can easily install them [in one
gollop](https://books.google.co.uk/books?isbn=0224046918) as follows:

```
# apt install \
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
    protobuf-compiler
# pip install \
    protobuf
```

### Installing optional dependencies

```
# pip install \
    jupyter   \
    pandas numpy scipy matplotlib \
    scikit-image scikit-learn     \
    pyyaml \
    protobuf
```

### Checking all dependencies

You can check all the dependencies on an Ubuntu system by running this [notebook](https://github.com/dividiti/ck-caffe/blob/master/script/check-deps/check_deps.ipynb). (View the output this notebook on an [Odroid XU3](http://odroid.com/dokuwiki/doku.php?id=en:odroid-xu3) board [here](http://nbviewer.jupyter.org/github/dividiti/ck-caffe/blob/master/script/check-deps/check_deps.xu3.20160808.ipynb).)


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
