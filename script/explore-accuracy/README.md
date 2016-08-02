Instructions
============

- For each Caffe network of interest, run:

```
$ ./_clean_program_pipeline.sh
$ ./_setup_program_pipeline.sh
Initializing universal program pipeline ...

***************************************************************************************

<...>

***************************************************************************************
Current directory: /home/anton/CK_REPOS/ck-caffe/program/caffe/tmp
***************************************************************************************

Resolving software dependencies ...

*** Dependency 1 = dataset-imagenet-aux (ImageNet dataset (aux)):

    Resolved. CK environment UID = ca493d0ecd624c48

*** Dependency 2 = dataset-imagenet-lmdb (ImageNet dataset (lmdb)):

    Resolved. CK environment UID = 84834443bb5839ea

*** Dependency 3 = lib-caffe (Caffe framework):

    Resolved. CK environment UID = e07c0c6968e8490b

*** Dependency 4 = caffemodel (Caffe model (net and weights)):

    Resolved. CK environment UID = 0f975ebfa4e6385a

***************************************************************************************
Writing state to file /home/anton/CK_REPOS/ck-caffe/script/explore-accuracy/_setup_program_pipeline_tmp.json ...
***************************************************************************************
Pipeline is ready!
```

- Select the Caffe installation, the dataset and the network to use.
  (If only one entity is available, no question will be asked.)
- For example, to measure the accuracy of GoogleNet, run:
```
$ ./explore_accuracy_googlenet.sh
^**************************************************************************************
Pipeline iteration: 1 of 1

  Vector of flattened and updated choices:

      ------------------- Statistical repetition: 1 of 1 -------------------

Initializing universal program pipeline ...

***************************************************************************************

<...>

{
  "loss1/loss1": 1.86667, 
  "loss1/top-1": 0.55522, 
  "loss1/top-5": 0.804981, 
  "loss2/loss1": 1.50183, 
  "loss2/top-1": 0.629759, 
  "loss2/top-5": 0.856821, 
  "loss3/loss3": 1.25635, 
  "loss3/top-1": 0.689299, 
  "loss3/top-5": 0.891441, 
  "post_processed": "yes"
}

Execution time: 0.000 sec.
***************************************************************************************
Pipeline executed successfully!
***************************************************************************************
```

When done, check the experiment entry:
```
$ ck search experiment:* --tags=accuracy,googlenet
local:experiment:caffe-explore-accuracy-googlenet
```
