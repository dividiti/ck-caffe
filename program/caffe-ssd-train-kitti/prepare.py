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

caffe_pb2 = utils.import_caffe_pb2()

SRC_IMAGES_DIR = os.getenv('CK_ENV_DATASET_IMAGE_DIR')
SRC_LABELS_DIR = os.getenv('CK_ENV_DATASET_LABELS_DIR')
CAFFE_BIN_DIR = os.getenv('CK_ENV_LIB_CAFFE_BIN')
CAFFE_MODEL_DIR = os.getenv('CK_ENV_MODEL_CAFFE')

CUR_DIR = os.path.realpath('.')
TMP_LABELS_DIR = os.path.join(CUR_DIR, 'labels')
TRAIN_FILE_LIST = os.path.join(CUR_DIR, 'train.txt')
TEST_FILE_LIST = os.path.join(CUR_DIR, 'test.txt')
TRAIN_PERCENT = int(os.getenv('CK_TRAIN_IMAGES_PERCENT', 70))
TRAIN_IMG_COUNT = 0 # to be assigned
TEST_IMG_COUNT = 0 # to be assigned

TARGET_IMG_W = utils.model_img_w(CAFFE_MODEL_DIR)
TARGET_IMG_H = utils.model_img_h(CAFFE_MODEL_DIR)

TRAIN_LMDB = os.path.join(CUR_DIR, 'train_lmdb')
TEST_LMDB = os.path.join(CUR_DIR, 'test_lmdb')
NAME_SIZE_FILE = os.path.join(CUR_DIR, 'test_name_size.txt')

LABEL_MAP = { 'background': 0 }
LABEL_MAP_FILE = os.path.join(CUR_DIR, 'labelmap_kitti.prototxt')


def save_label_to_map(label):
  '''
  While KITTI annotation files contain text name for label,
  SSD treats label as integer id. 
  '''
  # SqueezeDet demo (program:squeezedet) considers only a few labels.
  # It draw prediction boxes only for Car, Cyclist and Pedestrian.
  # So may be we should ignore rest of labels and treat them as DONTCARE_LABEL?
  if label in LABEL_MAP:
    return LABEL_MAP[label]
  label_id = len(LABEL_MAP)
  LABEL_MAP[label] = label_id
  return label_id


def save_label_map_file():
  proto = caffe_pb2.LabelMap()
  for label in LABEL_MAP:
    item = proto.item.add()
    item.name = label
    item.label = LABEL_MAP[label]
    item.display_name = label
  utils.write_prototxt(LABEL_MAP_FILE, proto)
    

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

  print('Labels found: {}'.format(len(LABEL_MAP)))
  print(';'.join(LABEL_MAP.keys()))
  save_label_map_file()
    

def write_file_list(img_files, file_name):
  '''
  Makes images list file. Each line of this list contains 
  full path to an image and path to corresponding label file.
  '''
  print('Writing {}...'.format(file_name))
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
  global TRAIN_IMG_COUNT
  global TEST_IMG_COUNT
  all_images = os.listdir(SRC_IMAGES_DIR)
  all_images = np.random.permutation(all_images) 
  TRAIN_IMG_COUNT = int(len(all_images) * TRAIN_PERCENT / 100.0)
  TEST_IMG_COUNT = len(all_images) - TRAIN_IMG_COUNT
  print('Total images count: {}'.format(len(all_images)))
  print('Train images count: {}'.format(TRAIN_IMG_COUNT))
  print('Test images count: {}'.format(TEST_IMG_COUNT))
  write_file_list(all_images[:TRAIN_IMG_COUNT], TRAIN_FILE_LIST)
  write_file_list(all_images[TRAIN_IMG_COUNT:], TEST_FILE_LIST)

  # Generate image name and size infomation.
  cmd = []
  cmd.append(os.path.join(CAFFE_BIN_DIR, 'get_image_size'))
  cmd.append('') # we can leave root path empty as our file list contains absolute paths
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
  print('\nConverting labels into SSD format...')
  convert_labels()

  print('\nMaking image list files...')
  make_train_test_file_lists()

  print('\nMaking training lmdb...')
  make_lmdb(TRAIN_FILE_LIST, TRAIN_LMDB)

  print('\nMaking testing lmdb...')
  make_lmdb(TEST_FILE_LIST, TEST_LMDB)

  # Save some info about prepared data to resue it in training script.
  utils.write_json('info.json', {
    'num_classes': len(LABEL_MAP),
    'img_width': TARGET_IMG_W,
    'img_height': TARGET_IMG_H,
    'train_img_count': TRAIN_IMG_COUNT,
    'test_img_count': TEST_IMG_COUNT
  })

  print('\nOK')
  print('Use "train" command key to start training session')
