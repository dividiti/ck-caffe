#!/usr/bin/env python
#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

import os
import numpy as np
import utils

SRC_IMAGES_DIR = os.getenv('CK_ENV_DATASET_IMAGE_DIR')
SRC_LABELS_DIR = os.getenv('CK_ENV_DATASET_LABELS_DIR')
CAFFE_BIN_DIR = os.getenv('CK_ENV_LIB_CAFFE_BIN')
CAFFE_MODEL_DIR = os.getenv('CK_ENV_MODEL_CAFFE')

CUR_DIR = os.path.realpath('.')
TMP_LABELS_DIR = os.path.join(CUR_DIR, 'labels')
TRAIN_FILE_LIST = os.path.join(CUR_DIR, 'train.txt')
TEST_FILE_LIST = os.path.join(CUR_DIR, 'test.txt')
TRAIN_PERCENT = int(os.getenv('CK_TRAIN_IMAGES_PERCENT', 70))

# Should be more robust criterion, may be lib should proivde some env var
TARGET_IMG_W = 300 if '-300' in CAFFE_MODEL_DIR else 500
TARGET_IMG_H = TARGET_IMG_W

TRAIN_LMDB = os.path.join(CUR_DIR, 'train_lmdb')
TEST_LMDB = os.path.join(CUR_DIR, 'test_lmdb')
NAME_SIZE_FILE = os.path.join(CUR_DIR, 'test_name_size.txt')

LABEL_MAP = {}
LABEL_MAP_FILE = os.path.join(CUR_DIR, 'labelmap_kitti.prototxt')


def save_label_to_map(label):
  '''
  While KITTI annotation files contain text name for label,
  SSD treats label as integer id. 
  '''
  if label in LABEL_MAP:
    return LABEL_MAP[label]
  label_id = len(LABEL_MAP)
  LABEL_MAP[label] = label_id
  return label_id


def save_label_map_file():
  with open(LABEL_MAP_FILE, 'w') as f:
    for label in LABEL_MAP:
      s = 'item {{\n' \
          '  name: "{0}"\n' \
          '  label: {1}\n' \
          '  display_name: "{0}"\n' \
          '}}\n'\
          .format(label, LABEL_MAP[label])
      f.write(s)
    

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
  utils.mkdir(TMP_LABELS_DIR)
  
  for label_file in os.listdir(SRC_LABELS_DIR):
    src_label_path = os.path.join(SRC_LABELS_DIR, label_file)
    dst_label_path = os.path.join(TMP_LABELS_DIR, label_file)
    with open(src_label_path, 'r') as src_file:
      with open(dst_label_path, 'w') as dst_file:
        for line in src_file:
          cols = line.split(' ')
          label_id = save_label_to_map(cols[0])
          if label_id >= 0:
            dst_file.write('{} {} {} {} {}\n'.format(
              label_id, cols[4], cols[5], cols[6], cols[7]))

  save_label_map_file()
    

def write_file_list(img_files, file_name):
  '''
  Makes images list file. Each line of this list contains 
  full path to an image and path to corresponding label file.
  '''
  print('Writing {}...'.format(file_name))
  print('Images count: {}'.format(len(img_files)))
  with open(file_name, 'w') as f:
    for img_file in img_files:
      img_path = os.path.join(SRC_IMAGES_DIR, img_file)
      label_file = img_file[:-3] + 'txt'
      label_path = os.path.join(TMP_LABELS_DIR, label_file)
      assert os.path.isfile(label_path)
      f.write('{} {}\n'.format(img_path, label_path))


def make_train_test_file_lists():
  '''
  Splits all images into two random sets -
  one for train and another for test.
  '''
  all_images = os.listdir(SRC_IMAGES_DIR)
  all_images = np.random.permutation(all_images) 
  print('Total images count: {}'.format(len(all_images)))
  train_count = int(len(all_images) * TRAIN_PERCENT / 100.0)
  write_file_list(all_images[:train_count], TRAIN_FILE_LIST)
  write_file_list(all_images[train_count:], TEST_FILE_LIST)

  # Generate image name and size infomation.
  cmd = []
  cmd.append(os.path.join(CAFFE_BIN_DIR, 'get_image_size'))
  cmd.append('') # we can leave root path empty as our file list contains absolute pathes
  cmd.append(TEST_FILE_LIST)
  cmd.append(NAME_SIZE_FILE)
  utils.run_command(cmd)


def make_lmdb(list_file, out_dir):
  '''
  Use convert_annoset tool from caffe SSD branch.
  The tool takes a list file as parameter and writes
  all listed images and its labels into LBDM database.
  '''
  utils.rmdir(out_dir)
    
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
  utils.run_command(cmd)


if __name__ == '__main__':
  print('Converting labels into SSD format...')
  convert_labels()

  print('Making image list files...')
  make_train_test_file_lists()

  print('Making training lmdb...')
  make_lmdb(TRAIN_FILE_LIST, TRAIN_LMDB)

  print('Making testing lmdb...')
  make_lmdb(TEST_FILE_LIST, TEST_LMDB)

  # Save some info about prepared data to resue it in training script.
  utils.write_json('info.json', {
    'num_classes': len(LABEL_MAP),
    'img_width': TARGET_IMG_W,
    'img_height': TARGET_IMG_H
  })

  print('OK')
  print('Use "train" command key to start training session')
