#!/usr/bin/env python
#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

import os
import shutil
import subprocess
import numpy as np  

SRC_IMAGES_DIR = os.getenv('CK_ENV_DATASET_IMAGE_DIR')
SRC_LABELS_DIR = os.getenv('CK_ENV_DATASET_LABELS_DIR')
TRAIN_PERCENT = int(os.getenv('CK_TRAIN_IMAGES_PERCENT', 70))
CAFFE_BIN_DIR = os.getenv('CK_ENV_LIB_CAFFE_BIN')

CUR_DIR = os.path.realpath('.')
TMP_LABELS_DIR = os.path.join(CUR_DIR, 'labels')
TRAIN_FILE_LIST = os.path.join(CUR_DIR, 'train.txt')
VAL_FILE_LIST = os.path.join(CUR_DIR, 'val.txt')

TARGET_IMG_W = 300 # TODO depend on SSD model: ssd-300 or ssd-500
TARGET_IMG_H = 300 # TODO depend on SSD model: ssd-300 or ssd-500
TARGET_TRAIN_LMDB = os.path.join(CUR_DIR, 'train_lmdb')
TARGET_VAL_LMDB = os.path.join(CUR_DIR, 'val_lmdb')

LABEL_MAP_FILE = os.path.join(os.path.realpath('..'), 'labelmap_kitti.prototxt')

# These ids should be the same as in LABEL_MAP_FILE
LABEL_MAP = {
  'Car': 0,
  'Cyclist': 1,
  'Pedestrian': 2
}


def get_label_id(label):
  '''
  While KITTI annotation files contain text name for label,
  SSD treats label as integer id. We keep label ids as static data
  here for simplisity and because of KITTI has only a few of them,
  but they could be read from LABEL_MAP_FILE
  '''
  return LABEL_MAP[label] if label in LABEL_MAP else -1


def convert_labels():
  '''
  Converts labels into SSD format.
  When convert_annoset tool reads a text label file, it splits 
  each line into only 5 values: label, xmin, ymin, xmax, ymax.
  While KITTI label files contain much more fields, e.g:
    0) Car     - label
    1) 0.00    - truncation
    2) 0       - occlusion
    3) 1.96    - ?
    4) 280.38  - xmin
    5) 185.10  - ymin
    6) 344.90  - xmax
    7) 215.59  - ymax
    8) 1.49    - ?
    9) 1.76    - ?
   10) 4.01    - ?
   11) -15.71  - ?
   12) 2.16    - ?
   13) 38.26   - ?
   14) 1.57    - ?
  '''
  if os.path.isdir(TMP_LABELS_DIR):
    shutil.rmtree(TMP_LABELS_DIR)
  os.mkdir(TMP_LABELS_DIR)
  
  for label_file in os.listdir(SRC_LABELS_DIR):
    src_label_path = os.path.join(SRC_LABELS_DIR, label_file)
    dst_label_path = os.path.join(TMP_LABELS_DIR, label_file)
    with open(src_label_path, 'r') as src_file:
      with open(dst_label_path, 'w') as dst_file:
        for line in src_file:
          cols = line.split(' ')
          label_id = get_label_id(cols[0])
          if label_id >= 0:
            dst_file.write('{} {} {} {} {}\n'.format(
              label_id, cols[4], cols[5], cols[6], cols[7]))
    

def write_file_list(img_files, file_name):
  print('Writing {}...'.format(file_name))
  print('Images count: {}'.format(len(img_files)))
  with open(file_name, 'w') as f:
    for img_file in img_files:
      img_path = os.path.join(SRC_IMAGES_DIR, img_file)
      label_file = img_file[:-3] + 'txt'
      label_path = os.path.join(TMP_LABELS_DIR, label_file)
      assert os.path.isfile(label_path)
      f.write('{} {}\n'.format(img_path, label_path))


def make_train_val_file_lists():
  '''
  Splits all images into two random sets -
  one for train and another for validation.
  '''
  all_images = os.listdir(SRC_IMAGES_DIR)
  all_images = np.random.permutation(all_images) 
  print('Total images count: {}'.format(len(all_images)))
  train_count = int(len(all_images) * TRAIN_PERCENT / 100.0)
  write_file_list(all_images[:train_count], TRAIN_FILE_LIST)
  write_file_list(all_images[train_count:], VAL_FILE_LIST)


def make_lmdb(list_file, out_dir):
  if os.path.isdir(out_dir):
    shutil.rmtree(out_dir)
    
  cmd = []
  cmd.append(os.path.join(CAFFE_BIN_DIR, 'convert_annoset'))
  cmd.append('--anno_type=detection')
  cmd.append('--label_type=txt')
  cmd.append('--label_map_file=' + LABEL_MAP_FILE)
  cmd.append('--resize_height=' + str(TARGET_IMG_H))
  cmd.append('--resize_width=' + str(TARGET_IMG_W))
  cmd.append('--backend=lmdb')
  cmd.append('--encoded')
  cmd.append('--encode_type=jpg')
  cmd.append('') # we can leave root path empty as our file list contains absolute pathes
  cmd.append(list_file)
  cmd.append(out_dir)
  print(' '.join(cmd))
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  output = process.communicate()[0]
  print(output)


if __name__ == '__main__':
  print('Converting labels into SSD format...')
  convert_labels()

  print('Making image list files...')
  make_train_val_file_lists()

  print('Making training lmdb...')
  make_lmdb(TRAIN_FILE_LIST, TARGET_TRAIN_LMDB)

  print('Making validation lmdb...')
  make_lmdb(VAL_FILE_LIST, TARGET_VAL_LMDB)
