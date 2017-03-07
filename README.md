# Collective Knowledge repository for collaboratively optimising Caffe-based designs

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

## Introduction

[CK-Caffe](https://github.com/dividiti/ck-caffe) is an open framework for
collaborative and reproducible optimisation of convolutional neural networks.
It's based on the [Caffe](http://caffe.berkeleyvision.org) framework from the
Berkeley Vision and Learning Center ([BVLC](http://bvlc.eecs.berkeley.edu)) and
the [Collective Knowledge](http://cknowledge.org) framework for customizable
cross-platform builds and experimental workflows with JSON API from the [cTuning
Foundation](http://ctuning.org) (see CK intro for more details: [1](https://arxiv.org/abs/1506.06256),
[2](https://www.researchgate.net/publication/304010295_Collective_Knowledge_Towards_RD_Sustainability) ). 
In essence, CK-Caffe is simply a suite of convenient wrappers with unified 
JSON API for customized building, evaluation and multi-objective optimisation of Caffe.

As outlined in our [vision](http://dx.doi.org/10.1145/2909437.2909449), we
invite the community to collaboratively design and optimize convolutional
neural networks to meet the performance, accuracy and cost requirements for
deployment on a range of form factors - from sensors to self-driving cars. To
this end, CK-Caffe leverages the key capabilities of CK to crowdsource
experimentation across diverse platforms, CNN designs, optimization
options, and so on; exchange experimental data in a flexible JSON-based format;
and apply leading-edge predictive analytics to extract valuable insights from
the experimental data.

See [cKnowledge.org/ai](http://cKnowledge.org/ai) for more details.

## Authors/contributors

* Anton Lokhmotov, [dividiti](http://dividiti.com)
* Grigori Fursin, [dividiti](http://dividiti.com) / [cTuning foundation](http://ctuning.org)
* Unmesh Bordoloi, [General Motors](http://gm.com)

## Quick installation on Ubuntu

Please refer to our [Installation Guide](https://github.com/dividiti/ck-caffe/wiki/Installation) for detailed instructions for Ubuntu, Gentoo, Yocto, Windows and Android.

### Installing general dependencies

```
$ sudo apt install coreutils \
                   build-essential \
                   make \
                   cmake \
                   wget \
                   git \
                   python \
                   python-pip
```

### Installing Caffe dependencies
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

### Installing CK

```
$ sudo pip install ck
$ ck version
```

### Installing CK-Caffe repository

```
$ ck pull repo:ck-caffe --url=https://github.com/dividiti/ck-caffe
```

### Building Caffe and all dependencies via CK

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

### Creating dataset subsets

The ILSVRC2012 validation dataset contains 50K images. For quick experiments,
you can create a subset of this dataset, as follows. Run:

```
$ ck install package:imagenet-2012-val-lmdb-256
```

When prompted, enter the number of images to convert to LMDB, say, `N` = 100.
The first `N` images will be taken.


### Customizing caffe benchmarking via CK command line

You can customize various Caffe parameters such as batch size and iterations via CK command line:

```
$ ck run program:caffe --env.CK_CAFFE_BATCH_SIZE=1 --env.CK_CAFFE_ITERATIONS=10
```

### Installing CK on Windows, Android and various flavours of Linux

You can find details about CK-Caffe installation for Windows, various flavours 
of Linux and Android [here](http://github.com/dividiti/ck-caffe/wiki/Installation).

## Preliminary results

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

## Next steps

CK-Caffe is part of an ambitious long-term and community-driven 
project to enable collaborative and systematic optimization 
of realistic workloads across diverse hardware 
in terms of performance, energy usage, accuracy, reliability,
hardware price and other costs
([ARM TechCon'16 talk](http://schedule.armtechcon.com/session/know-your-workloads-design-more-efficient-systems), 
[ARM TechCon'16 demo](https://github.com/ctuning/ck/wiki/Demo-ARM-TechCon'16), 
[DATE'16](http://tinyurl.com/zyupd5v), 
[CPC'15](http://arxiv.org/abs/1506.06256)).

We are working with the community to unify and crowdsource performance analysis 
and tuning of various DNN frameworks (or any realistic workload) 
using Collective Knowledge Technology:
* [CK-TensorFlow](https://github.com/dividiti/ck-tensorflow)
* [CK-TinyDNN](https://github.com/ctuning/ck-tiny-dnn)
* [Android app for DNN crowd-benchmarking and crowd-tuning](https://play.google.com/store/apps/details?id=openscience.crowdsource.video.experiments)
* [CK-powered ARM workload automation](https://github.com/ctuning/ck-wa)

We continue gradually exposing various design and optimization
choices including full parameterization of existing models.

## Open R&D challenges

We use crowd-benchmarking and crowd-tuning of such realistic workloads across diverse hardware for 
[open academic and industrial R&D challenges](https://github.com/ctuning/ck/wiki/Research-and-development-challenges.mediawiki) - 
join this community effort!

## Related Publications with long term vision

* <a href="https://github.com/ctuning/ck/wiki/Publications">All references with BibTex</a>

![logo](https://github.com/ctuning/ck-guide-images/blob/master/logo-validated-by-the-community-simple.png)
