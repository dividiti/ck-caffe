# caffe-ssd-train-kitti

Demo program for fine-tuning of SSD caffemodels originaly trained on COCO and VOC datasets to detect objects of KITTI dataset.


## Requirements

Caffe library:
```
ck install package:lib-caffe-ssd-cpu
ck install package:lib-caffe-ssd-cuda
```

Caffe SSD model and pretrained weights:
```
ck install package:caffemodel-ssd-coco-300
ck install package:caffemodel-ssd-coco-512
ck install package:caffemodel-ssd-voc-300
ck install package:caffemodel-ssd-voc-512
```

KITTI dataset:
```
ck install package:dataset-kitti-full
```


## Run

There are two steps.

### Prepare

```
ck run program:caffe-ssd-train-kitti --cmd_key=prepare
```

Here training and testing datasets are prepared. Original KITTI dataset contains image files, while SSD training uses LMBD as a data source. KITTI images are scaled to a size supported by the selected caffemodel (300 or 512 px) and `CK_TRAIN_IMAGES_PERCENT` of them are included into the train database and the rest into the test database.

### Train
```
ck run program:caffe-ssd-train-kitti --cmd_key=train
```

Run training process using prepared data.

Essential anvironment variables:

#### `CK_BATCH_SIZE`
Specify the batch size.

#### `CK_DEVICE_ID`
The device that will be used in GPU mode. Run mode, CPU or GPU, is governed by the selected caffe library.

#### `CK_SNAPSHOT_INTERVAL`
The snapshot interval.

#### `CK_TEST_INTERVAL`
The number of iterations between two testing phases.


### Results

Trained weights are saved into `tmp/snapshots` directory.


### TODO

- Models `*-512` fail with message `Check failed: num_priors_ * num_classes_ == bottom[1]->channels()`, it is because of dimensions of final layers depend on the number of detection classes. Though that layers are modified in program but something is missed for `*-512` models (they have more layers than `*-300`s have).

- We could implement continued training by loading not the pretrained weights of the selected caffemodel but latest snapshot instead. 

- Implement one more command key `test` that will detect specified number of KITTI images using latest snapshot then will convert detection results and run original KITTI evaluation program (`$CK-TOOLS/demo-squeezedet-patched/squeezeDet/src/dataset/kitti-eval/cpp/evaluate_object.cpp`) to calculate metrics in the same way as SqueezeDet does.