#!/usr/bin/env python
#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

import os
import re
import utils

CAFFE_BIN_DIR = os.getenv('CK_ENV_LIB_CAFFE_BIN')
WEIGHTS_FILE = os.getenv('CK_ENV_MODEL_CAFFE_WEIGHTS_FILE')
CAFFE_MODEL_DIR = os.getenv('CK_ENV_MODEL_CAFFE')
SRC_SOLVER_PROTOTXT = os.path.join(CAFFE_MODEL_DIR, 'solver.prototxt')
SRC_TRAIN_PROTOTXT = os.path.join(CAFFE_MODEL_DIR, 'train.prototxt')
SRC_TEST_PROTOTXT = os.path.join(CAFFE_MODEL_DIR, 'test.prototxt')

RUN_MODE_CPU = 'CPU'
RUN_MODE_GPU = 'GPU'
# Should be more robust criterion, may be lib should proivde some env var
RUN_MODE = RUN_MODE_CPU if '-cpu' in CAFFE_BIN_DIR else RUN_MODE_GPU

BATCH_SIZE = os.getenv('CK_BATCH_SIZE', 8)
DEVICE_ID = os.getenv('CK_DEVICE_ID', 0)
SNAPSHOTS_DIR = 'snapshots'
SOLVER_PROTOTXT = 'solver.prototxt'
TRAIN_PROTOTXT = 'train.prototxt'
TEST_PROTOTXT = 'test.prototxt'
TRAIN_LMDB = 'train_lmdb'
TEST_LMDB = 'val_lmdb'
LABEL_MAP_FILE = 'labelmap_kitti.prototxt'
NAME_SIZE_FILE = 'test_name_size.txt'

PREPARED_INFO = utils.read_json('info.json')
NUM_CLASSES = PREPARED_INFO['num_classes']


def set_param(txt, key, value, as_str = False):
  key_marker = '^(\\s*{})\\:\\s+(.+)$'.format(key)
  if as_str:
    new_param = '\\1: "{}"'.format(value)
  else:
    new_param = '\\1: {}'.format(value)
  return re.sub(key_marker, new_param, txt, 0, re.MULTILINE)


def prepare_solver_file():
  params = utils.read_text(SRC_SOLVER_PROTOTXT)
  params = set_param(params, 'train_net', TRAIN_PROTOTXT, True)
  params = set_param(params, 'test_net', TEST_PROTOTXT, True)
  params = set_param(params, 'snapshot_prefix', SNAPSHOTS_DIR, True)
  params = set_param(params, 'solver_mode', RUN_MODE)
  params = set_param(params, 'device_id', DEVICE_ID)
  # Another parameters could be taken from environment in the future
  utils.write_text(SOLVER_PROTOTXT, params)


def make_model_name(phase):
  return 'VGG_kitti_SSD_{}x{}_{}'.format(
    PREPARED_INFO['img_width'], PREPARED_INFO['img_height'], phase)


def prepare_train_prototxt():
  txt = utils.read_text(SRC_TRAIN_PROTOTXT)
  #txt = set_param(txt, 'name', make_model_name('train'), True)
  txt = set_param(txt, 'batch_size', BATCH_SIZE)
  txt = set_param(txt, 'source', TRAIN_LMDB, True)
  txt = set_param(txt, 'num_classes', NUM_CLASSES)
  txt = set_param(txt, 'label_map_file', LABEL_MAP_FILE, True)
  utils.write_text(TRAIN_PROTOTXT, txt)


def prepare_test_prototxt():
  txt = utils.read_text(SRC_TEST_PROTOTXT)
  #txt = set_param(txt, 'name', make_model_name('test'), True)
  txt = set_param(txt, 'batch_size', BATCH_SIZE)
  txt = set_param(txt, 'source', TEST_LMDB)
  txt = set_param(txt, 'num_classes', NUM_CLASSES)
  txt = set_param(txt, 'label_map_file', LABEL_MAP_FILE, True)
  txt = set_param(txt, 'name_size_file', NAME_SIZE_FILE, True)

  reshape_layer = r'^(\s*reshape_param \{' \
                      r'\s*shape \{' \
                        r'\s*dim: 0' \
                        r'\s*dim: -1' \
                        r'\s*dim:) (\d+)$'
  num_classes = r'\1 ' + str(NUM_CLASSES)
  txt = re.sub(reshape_layer, num_classes, txt, 1, re.MULTILINE)
  
  utils.write_text(TEST_PROTOTXT, txt)
    

def start_training():
  cmd = []
  cmd.append(os.path.join(CAFFE_BIN_DIR, 'caffe'))
  cmd.append('train')
  cmd.append('--solver=' + SOLVER_PROTOTXT)
  cmd.append('--weights=' + WEIGHTS_FILE)
  if RUN_MODE == RUN_MODE_GPU:
    cmd.append('--gpu=' + str(DEVICE_ID))
  utils.run_command(cmd)


if __name__ == '__main__':
  utils.rmdir(SNAPSHOTS_DIR)

  # Load default prototxt files from selected SSD caffemodel dir,
  # modify them using new parameter values corresponding to current
  # training session, and write as new files into current dir.
  print('Preparing prototxts...')
  prepare_train_prototxt()  
  prepare_test_prototxt()  
  prepare_solver_file()
    
  print('Training...')
  start_training()
      
