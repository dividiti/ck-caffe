[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/ctuning/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](http://cTuning.org/ae)
[![workflow](https://github.com/ctuning/ck-guide-images/blob/master/ck-workflow.svg)](http://cKnowledge.org)

[![DOI](https://zenodo.org/badge/60531899.svg)](https://zenodo.org/badge/latestdoi/60531899)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

# News

* 20181205: It seems that Caffe for Android fails with the latest NDK. 
However, we checked that we can still automatically build Caffe 
for Android via CK with the NDK r13b and Boost 1.64 as described 
[here](https://github.com/dividiti/ck-caffe/issues/141).

# [cknowledge.org/ai](http://cknowledge.org/ai): Crowdsourcing benchmarking and optimisation of AI

A suite of open-source tools for [collecting knowledge on optimising AI](http://bit.ly/hipeac49-ckdl):
* [Android app](http://cKnowledge.org/android-apps.html)
* [Desktop app](https://github.com/dividiti/ck-crowdsource-dnn-optimization)
* [CK-Caffe](https://github.com/dividiti/ck-caffe)
* [CK-Caffe2](https://github.com/ctuning/ck-caffe2)
* [CK-TensorFlow](https://github.com/ctuning/ck-tensorflow)
* [CK-MXNet](https://github.com/ctuning/ck-mxnet)
* [CK-PyTorch](https://github.com/ctuning/ck-pytorch)
* [CK-CNTK](https://github.com/ctuning/ck-cntk)
* [CK-TinyDNN](https://github.com/ctuning/ck-tiny-dnn)
* [CK-MVNC (Movidius Neural Compute Stick)](https://github.com/ctuning/ck-mvnc)
* [CK-TensorRT](https://github.com/ctuning/ck-tensorrt)
* [CK-KaNN](https://github.com/ctuning/ck-kann)
* etc.

# Collective Knowledge repository for collaboratively optimising Caffe-based designs

## Introduction

[CK-Caffe](https://github.com/dividiti/ck-caffe) is an open framework for
collaborative and reproducible optimisation of convolutional neural networks.
It's based on the [Caffe](http://caffe.berkeleyvision.org) framework from the
Berkeley Vision and Learning Center ([BVLC](http://bvlc.eecs.berkeley.edu)) and
the [Collective Knowledge](http://cknowledge.org) framework for customizable
cross-platform builds and experimental workflows with JSON API from the
[cTuning Foundation](http://ctuning.org) (see CK intro for more details: [1](https://arxiv.org/abs/1506.06256),
[2](https://www.researchgate.net/publication/304010295_Collective_Knowledge_Towards_RD_Sustainability) ).
In essence, CK-Caffe is an open-source suite of convenient wrappers and workflows with unified
JSON API for simple and customized building, evaluation and multi-objective optimisation
of various Caffe implementations (CPU, CUDA, OpenCL) across diverse platforms
from mobile devices and IoT to supercomputers.

As outlined in our [vision](http://dx.doi.org/10.1145/2909437.2909449),
we invite the community to collaboratively design and optimize convolutional
neural networks to meet the performance, accuracy and cost requirements for
deployment on a range of form factors - from sensors to self-driving cars. To
this end, CK-Caffe leverages the key capabilities of CK to crowdsource
experimentation across diverse platforms, CNN designs, optimization
options, and so on; exchange experimental data in a flexible JSON-based format;
and apply leading-edge predictive analytics to extract valuable insights from
the experimental data.

See [cKnowledge.org/ai](http://cKnowledge.org/ai), 
[reproducible and CK-powered AI/SW/HW co-design competitions at ACM/IEEE conferences](http://cKnowledge.org/request),
[shared optimization statistics](http://cKnowledge.org/repo),
[reusable AI artifact in the CK format](http://cKnowledge.org/ai-artifacts)
and [online demo of CK AI API with self-optimizing DNN](http://cKnowledge.org/ai/ck-api-demo) for more details.

## Maintainers
* Linux/MacOS: [dividiti](http://dividiti.com) - not actively maintained
* Windows: currently no maintainer

## Authors/contributors

* Anton Lokhmotov, [dividiti](http://dividiti.com)
* Unmesh Bordoloi, [General Motors](http://gm.com)
* Grigori Fursin, [dividiti](http://dividiti.com) / [cTuning foundation](http://ctuning.org)
* Dmitry Savenko, [Xored](http://xored.com)
* Daniil Efremov, [Xored](http://xored.com)
* Flavio Vella, [dividiti](http://dividiti.com)

## Public benchmarking results

### Comparing the accuracy of 4 models

In this [Jupyter
notebook](https://github.com/dividiti/ck-caffe/blob/master/script/explore-accuracy/explore_accuracy.20160808.ipynb),
we compare the Top-1 and Top-5 accuracy of 4 models:

- [AlexNet](https://github.com/BVLC/caffe/tree/master/models/bvlc_alexnet)
- [SqueezeNet 1.0](https://github.com/DeepScale/SqueezeNet/tree/master/SqueezeNet_v1.0)
- [SqueezeNet 1.1](https://github.com/DeepScale/SqueezeNet/tree/master/SqueezeNet_v1.1)
- [GoogleNet](https://github.com/BVLC/caffe/tree/master/models/bvlc_googlenet)

The experimental data (stored in the main CK-Caffe repository under '[experiment](https://github.com/dividiti/ck-caffe/tree/master/experiment)') essentially confirms that [SqueezeNet](https://arxiv.org/abs/1602.07360) matches (and even slightly exceeds) the accuracy of [AlexNet](https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf) on the [ImageNet validation set](http://academictorrents.com/details/5d6d0df7ed81efd49ca99ea4737e0ae5e3a5f2e5) (50,000 images).

### Comparing the performance across models and configurations

We have performed several detailed performance analysis studies across a range of platforms using CK-Caffe. The following results are publicly available:

- [NVIDIA TX1](https://github.com/dividiti/ck-caffe-nvidia-tx1) ([view on github.com](https://github.com/dividiti/ck-caffe-nvidia-tx1/blob/master/script/caffe-tensorrt/ck-caffe-nvidia-tx1-with-tensorrt.20170429.ipynb); [view on nbviewer.jupyter.org](https://nbviewer.jupyter.org/github/dividiti/ck-caffe-nvidia-tx1/blob/master/script/caffe-tensorrt/ck-caffe-nvidia-tx1-with-tensorrt.20170429.ipynb?raw)): 4 models, 6 Caffe configs + 2 TensorRT 1.0 EA configs (also varying the batch size). **NB:** The Caffe results are released with approval from General Motors. The TensorRT 1.0 EA results are obtained with [CK-TensorRT](https://github.com/ctuning/ck-tensorrt) and released with approval from General Motors and NVIDIA.

- [NVIDIA GTX1080](https://github.com/dividiti/ck-caffe-nvidia-gtx1080) ([view on github.com](https://github.com/dividiti/ck-caffe-nvidia-gtx1080/blob/master/script/analysis/ck-caffe-nvidia-gtx1080.20170518.ipynb); [view on nbviewer.jupyter.org](https://nbviewer.jupyter.org/github/dividiti/ck-caffe-nvidia-gtx1080/blob/master/script/analysis/ck-caffe-nvidia-gtx1080.20170518.ipynb?raw)): 4 models, 14 configs (also varying the batch size). **NB:** The Caffe results are released with approval from General Motors.

- [Firefly RK3399](http://en.t-firefly.com/en/firenow/Firefly_RK3399) ([view on github.com](https://github.com/dividiti/ck-caffe-firefly-rk3399/blob/master/script/batch_size-libs-models/analysis.20170531.ipynb);
[view on nbviewer.jupyter.org](https://nbviewer.jupyter.org/github/dividiti/ck-caffe-firefly-rk3399/blob/master/script/batch_size-libs-models/analysis.20170531.ipynb)): 3 models, 9 configs (also varying the batch size).

- [Samsung Chromebook 2](http://www.samsung.com/us/computer/chrome-os-devices/XE503C12-K01US-specs) ([view on github.com](https://github.com/dividiti/ck-caffe-explore-batch-size-chromebook2/blob/master/script/compare-time-fw/compare_time_fw.20160809.ipynb); [view on nbviewer.jupyter.org](https://nbviewer.jupyter.org/github/dividiti/ck-caffe-explore-batch-size-chromebook2/blob/master/script/compare-time-fw/compare_time_fw.20160809.ipynb?raw)): 4 models, 4 configs (also varying the batch size).

- [Samsung Chromebook 2](http://www.samsung.com/us/computer/chrome-os-devices/XE503C12-K01US-specs) ([view on github.com](https://github.com/dividiti/ck-caffe-samsung-chromebook2/blob/master/script/batch_size-openblas_threads-models/analysis.20170520.ipynb); [view on nbviewer.jupyter.org](https://nbviewer.jupyter.org/github/dividiti/ck-caffe-samsung-chromebook2/blob/master/script/batch_size-openblas_threads-models/analysis.20170520.ipynb)): 3 models, OpenBLAS v0.2.19 (also varying the batch size and the number of threads).


## Quick installation on Ubuntu

Please refer to our [Installation Guide](https://github.com/dividiti/ck-caffe/wiki/Installation) for detailed instructions for Ubuntu, Gentoo, Yocto, RedHat, CentOS, Windows and Android.

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

### Installing essential Caffe dependencies
```
$ sudo apt install libleveldb-dev \
                   libsnappy-dev \
                   gfortran
```

### Installing optional Caffe dependencies
CK can automatically build the following dependencies from source using versions that should work well together. Installing via `apt`, however, is somewhat faster.

```
$ sudo apt install libboost-all-dev \
                   libgflags-dev \
                   libgoogle-glog-dev \
                   libhdf5-serial-dev \
                   liblmdb-dev \
                   libprotobuf-dev \
                   protobuf-compiler \
                   libopencv-dev
```

### Installing CK


```
$ sudo pip install ck
```

Skip "sudo" if installing on Windows.

Alternatively, you can install CK in a user space as follows:
```
$ git clone http://github.com/ctuning/ck ck-master
$ export PATH=$PWD/ck-master/bin:$PATH
$ export PYTHONPATH=$PWD/ck-master:$PYTHONPATH
```

### Testing CK

```
$ ck version
```

We suggest you to configure CK to install packages to the CK virtual environment entries (env):
```
$ ck set kernel var.install_to_env=yes
```

### Installing CK-Caffe repository

```
$ ck pull repo:ck-caffe --url=https://github.com/dividiti/ck-caffe
```

### Installing CK packages

Very often latest Caffe conflicts with the older protobuf version installed on a system.
That's why we suggest to install protobuf via CK before installing Caffe:
```
$ ck install package --tags=protobuf-host
```

### Building Caffe and all dependencies via CK

The first time you run caffe benchmark (on Linux or Windows), 
CK will build and install all missing dependencies for your machine,
download required data sets and will start benchmark:

```
$ ck run program:caffe
```

CK may ask you to select some detected software and packages to be used for installation (when multiple choices are available).
In such cases, we suggest you to either use a default value (just press Enter) or stable (recommended) versions.

### Testing installation via image classification

```
 $ ck compile program:caffe-classification --speed
 $ ck run program:caffe-classification
```

Note that you will be asked to select a JPEG image from available CK data sets.
We have added standard demo images (`cat.jpg`, `catgrey.jpg`, `fish-bike.jpg`, `computer_mouse.jpg`)
to the ['ctuning-datasets-min' repository](https://github.com/ctuning/ctuning-datasets-min).

You can list them via:
```
 $ ck pull repo:ctuning-datasets-min
 $ ck search dataset --tags=dnn
```

You can minimize interactive selection of multiple software dependencies by adding "--reuse_deps" flag during compilation, i.e.
```
 $ ck compile program:caffe-classification --speed --reuse_deps
 $ ck run program:caffe-classification
```

If you have Android SDK and NDK installed, you can compile and run the same classification example on your Android device 
connected to a host machine via ADB as follows:

```
 $ ck compile program:caffe-classification --speed --target_os=android21-arm64
 $ ck run program:caffe-classification --target_os=android21-arm64
```

### Participating in collaborative evaluation and optimization of various Caffe engines and models (on-going crowd-benchmarking)
You can participate in crowd-benchmarking of Caffe via:
```
$ ck crowdbench caffe --user={your email or ID to acknowledge contributions} --env.CK_CAFFE_BATCH_SIZE=5
```

During collaborative benchmarking, you can select various engines (which will be built on your machine)
and models for evaluation.

You can also manually install additional flavours of Caffe engines across diverse hardware
and OS (Linux/Windows/Android on Odroid, Raspberry Pi, ARM, Intel, AMD, NVIDIA, etc.)
as described [here](https://github.com/dividiti/ck-caffe/wiki/Installation).

You can also install extra models as follows:
```
 $ ck list package --tags=caffemodel
 $ ck install package:{name of above packages}
```

You can even evaluate DNN engines on Android mobile devices connected via `adb` to your host machine via:

```
$ ck crowdbench caffe --target_os=android21-arm64 --env.CK_CAFFE_BATCH_SIZE=1
```

Feel free to try different batch sizes by changing command line option `--env.CK_CAFFE_BATCH_SIZE`.

You can crowd-benchmark Caffe on Windows without re-compilation,
i.e. using Caffe CPU or OpenCL binaries pre-built by the CK.
You should install such binaries as follows:

```
 $ ck install package:lib-caffe-bvlc-master-cpu-bin-win
```
or
```
 $ ck install package:lib-caffe-bvlc-opencl-libdnn-viennacl-bin-win
```

You can also use this [Android app](http://cKnowledge.org/android-apps.html)
to crowdsource benchmarking of ARM-based Caffe libraries for image recognition.

You can see continuously aggregated results in the
[public Collective Knowledge repository](http://cknowledge.org/repo/web.php?native_action=show&native_module_uoa=program.optimization&scenario=1eb2f50d4620903e).

You can also open this website from the command line:
```
 $ ck browse experiment.bench.caffe
```

## Unifying multi-dimensional and multi-objective autotuning

It is also possible to take advantage of our [universal multi-objective CK autotuner](https://github.com/ctuning/ck/wiki/Autotuning)
to optimize Caffe. As a first simple example, we added batch size tuning via CK. You can invoke it as follows:

```
$ ck autotune caffe
```

All results will be recorded in the local CK repository and 
you will be given command lines to plot graphs or replay experiments such as:
```
$ ck plot graph:{experiment UID}
$ ck replay experiment:{experiment UID} --point={specific optimization point}
```

## Unifying AI API

CK allows us to unify AI interfaces while collaboratively optimizing underneath engines.
For example, we added similar support to install, use and evaluate 
[Caffe2](https://github.com/ctuning/ck-caffe2) and [TensorFlow](https://github.com/ctuning/ck-tensorflow) via CK:

```
$ ck pull repo:ck-caffe2
$ ck pull repo:ck-tensorflow

$ ck install package:lib-caffe2-master-eigen-cpu-universal --env.CAFFE_BUILD_PYTHON=ON
$ ck install package:lib-tensorflow-1.1.0-cpu
$ ck install package:lib-tensorflow-1.1.0-cuda

$ ck run program:caffe2 --cmd_key=classify
$ ck run program:tensorflow --cmd_key=classify

$ ck crowdbench caffe2 --env.BATCH_SIZE=5 --user=i_want_to_ack_my_contribution
$ ck crowdbench tensorflow --env.BATCH_SIZE=5 --user=i_want_to_ack_my_contribution

$ ck autotune caffe2
$ ck autotune tensorflow
```
### Creating dataset subsets

The ILSVRC2012 validation dataset contains 50K images. For quick experiments,
you can create a subset of this dataset, as follows. Run:

```
$ ck install package:imagenet-2012-val-lmdb-256
```

When prompted, enter the number of images to convert to LMDB, say, `N` = 100.
The first `N` images will be taken.

### Creating realistic/representative training sets

We provided an option in all our AI crowd-tuning tools to let the community report 
and share mispredictions (images, correct label and wrong misprediction) 
to gradually and collaboratively build realistic data/training sets:
* [Public repository (see "mispredictions and unexpected behavior)](http://cknowledge.org/repo/web.php?action=index&module_uoa=wfe&native_action=show&native_module_uoa=program.optimization)
* [Misclassified images via CK-based AI web-service](http://cknowledge.org/repo/web.php?action=index&module_uoa=wfe&native_action=show&native_module_uoa=program.optimization)

### Customizing caffe benchmarking via CK command line

You can customize various Caffe parameters such as batch size and iterations via CK command line:

```
$ ck run program:caffe --env.CK_CAFFE_BATCH_SIZE=1 --env.CK_CAFFE_ITERATIONS=10
```

### Installing CK on Windows, Android and various flavours of Linux

You can find details about CK-Caffe installation for Windows, various flavours
of Linux and Android [here](http://github.com/dividiti/ck-caffe/wiki/Installation).

## Online demo of a unified CK-AI API

* [Simple demo](http://cknowledge.org/repo/web.php?template=ck-ai-basic) to classify images with
continuous optimization of DNN engines underneath, sharing of mispredictions and creation of a community training set;
and to predict compiler optimizations based on program features.


## Next steps

CK-Caffe is part of an ambitious long-term and community-driven
project to enable collaborative and systematic optimization
of realistic workloads across diverse hardware
in terms of performance, energy usage, accuracy, reliability,
hardware price and other costs
([ARM TechCon'16 talk and demo](https://github.com/ctuning/ck/wiki/Demo-ARM-TechCon'16),
[DATE'16](http://tinyurl.com/zyupd5v),
[CPC'15](http://arxiv.org/abs/1506.06256)).

We are working with the community to unify and crowdsource performance analysis
and tuning of various DNN frameworks (or any representative workloads)
using Collective Knowledge Technology:
* [CK-TensorFlow](https://github.com/dividiti/ck-tensorflow)
* [CK-Caffe2](https://github.com/ctuning/ck-caffe2)
* [Android app for DNN crowd-benchmarking and crowd-tuning](http://cKnowledge.org/android-apps.html)
* [CK-powered ARM workload automation](https://github.com/ctuning/ck-wa)

We continue to gradually expose various design and optimization
choices including full parameterization of existing models.

## Open R&D challenges

We use crowd-benchmarking and crowd-tuning of such realistic workloads across diverse hardware for
[open academic and industrial R&D challenges](https://github.com/ctuning/ck/wiki/Research-and-development-challenges.mediawiki) -
join this community effort!

## Related publications with long-term vision

```
@inproceedings{Lokhmotov:2016:OCN:2909437.2909449,
 author = {Lokhmotov, Anton and Fursin, Grigori},
 title = {Optimizing Convolutional Neural Networks on Embedded Platforms with OpenCL},
 booktitle = {Proceedings of the 4th International Workshop on OpenCL},
 series = {IWOCL '16},
 year = {2016},
 location = {Vienna, Austria},
 url = {http://doi.acm.org/10.1145/2909437.2909449},
 acmid = {2909449},
 publisher = {ACM},
 address = {New York, NY, USA},
 keywords = {Convolutional neural networks, OpenCL, collaborative optimization, deep learning, optimization knowledge repository},
}

@inproceedings{ck-date16,
    title = {{Collective Knowledge}: towards {R\&D} sustainability},
    author = {Fursin, Grigori and Lokhmotov, Anton and Plowman, Ed},
    booktitle = {Proceedings of the Conference on Design, Automation and Test in Europe (DATE'16)},
    year = {2016},
    month = {March},
    url = {https://www.researchgate.net/publication/304010295_Collective_Knowledge_Towards_RD_Sustainability}
}
```

* <a href="https://github.com/ctuning/ck/wiki/Publications">All related references with BibTex</a>

## Testimonials and awards

* 2015: ARM and the cTuning foundation use CK to accelerate computer engineering: [HiPEAC Info'45 page 17](https://www.hipeac.net/assets/public/publications/newsletter/hipeacinfo45.pdf), [ARM TechCon'16 presentation and demo](https://github.com/ctuning/ck/wiki/Demo-ARM-TechCon'16), [public CK repo](https://github.com/ctuning/ck-wa)

## Troubleshooting

* When compiling OpenCL version of Caffe on Linux targeting NVidia GPU, select generic x86_64/libOpenCL.so rather than NVidia OpenCL driver when asked by the CK.

## Feedback

Feel free to engage with our community via this mailing list:
* http://groups.google.com/group/collective-knowledge
