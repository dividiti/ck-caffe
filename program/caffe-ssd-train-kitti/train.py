#!/usr/bin/env python
#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

import os
import utils

caffe_pb2 = utils.import_caffe_pb2()

CAFFE_BIN_DIR = os.getenv('CK_ENV_LIB_CAFFE_BIN')
WEIGHTS_FILE = os.getenv('CK_ENV_MODEL_CAFFE_WEIGHTS')
CAFFE_MODEL_DIR = os.getenv('CK_ENV_MODEL_CAFFE')
SRC_SOLVER_PROTOTXT = os.path.join(CAFFE_MODEL_DIR, 'solver.prototxt')
SRC_TRAIN_PROTOTXT = os.path.join(CAFFE_MODEL_DIR, 'train.prototxt')
SRC_TEST_PROTOTXT = os.path.join(CAFFE_MODEL_DIR, 'test.prototxt')

# Should be more robust criterion, perhaps lib should provide some env var
RUN_MODE = 'CPU' if '-cpu' in CAFFE_BIN_DIR else 'GPU'
def is_cpu(): return RUN_MODE == 'CPU'
def is_gpu(): return RUN_MODE == 'GPU'

CUR_DIR = os.path.realpath('.')
BATCH_SIZE = int(os.getenv('CK_BATCH_SIZE', 8))
DEVICE_ID = int(os.getenv('CK_DEVICE_ID', 0))
SNAPSHOTS_DIR = 'snapshots'
SNAPSHOT_INTERVAL = int(os.getenv('CK_SNAPSHOT_INTERVAL', 1000))
TEST_INTERVAL = int(os.getenv('CK_TEST_INTERVAL', 250))
TEST_RESULTS_DIR = 'validations'
SOLVER_PROTOTXT = 'solver.prototxt'
TRAIN_PROTOTXT = 'train.prototxt'
TEST_PROTOTXT = 'test.prototxt'
TRAIN_LMDB = 'train_lmdb'
TEST_LMDB = 'test_lmdb'
LABEL_MAP_FILE = 'labelmap_kitti.prototxt'
NAME_SIZE_FILE = 'test_name_size.txt'

PREPARED_INFO = utils.read_json('info.json')
PREPARED_IMG_W = int(PREPARED_INFO['img_width'])
PREPARED_IMG_H = int(PREPARED_INFO['img_height'])
NUM_CLASSES = int(PREPARED_INFO['num_classes'])


def read_prototxt_net(file_name):
  net = caffe_pb2.NetParameter()
  utils.read_prototxt(file_name, net)
  layers = {}
  for layer in net.layer:
    layers[layer.name] = layer
  return net, layers


def prepare_solver_prototxt():
  params = caffe_pb2.SolverParameter()
  utils.read_prototxt(SRC_SOLVER_PROTOTXT, params)
  params.train_net = TRAIN_PROTOTXT
  params.test_net[0] = TEST_PROTOTXT
  params.snapshot = SNAPSHOT_INTERVAL
  params.snapshot_prefix = os.path.join(SNAPSHOTS_DIR, 'ssd_kitti')
  params.test_interval = TEST_INTERVAL
  params.solver_mode = params.CPU if is_cpu() else params.GPU
  params.device_id = DEVICE_ID
  utils.write_prototxt(SOLVER_PROTOTXT, params)


def change_layers_for_num_classes(layers):
  def change_layer(name, new_outs):
    new_name = name + '_kitti'
    layers[name].convolution_param.num_output = new_outs
    layers[name].name = new_name
    # correct layer references
    for layer in layers.values():
      for i in range(len(layer.bottom)):
        if layer.bottom[i] == name:
          layer.bottom[i] = new_name
      for i in range(len(layer.top)):
        if layer.top[i] == name:
          layer.top[i] = new_name

  change_layer('conv4_3_norm_mbox_conf', NUM_CLASSES * 4)
  change_layer('fc7_mbox_conf', NUM_CLASSES * 6)
  change_layer('conv6_2_mbox_conf', NUM_CLASSES * 6)
  change_layer('conv7_2_mbox_conf', NUM_CLASSES * 6)
  change_layer('conv8_2_mbox_conf', NUM_CLASSES * 4)
  change_layer('conv9_2_mbox_conf', NUM_CLASSES * 4)
  if PREPARED_IMG_W == 512:
    change_layer('conv10_2_mbox_conf', NUM_CLASSES * 4)


def prepare_train_prototxt():
  net, layers = read_prototxt_net(SRC_TRAIN_PROTOTXT)

  net.name = 'VGG_kitti_SSD_{}x{}_train'.format(PREPARED_IMG_W, PREPARED_IMG_H)

  layers['data'].data_param.source = TRAIN_LMDB
  layers['data'].data_param.batch_size = BATCH_SIZE
  layers['data'].annotated_data_param.label_map_file = LABEL_MAP_FILE

  layers['mbox_loss'].multibox_loss_param.num_classes = NUM_CLASSES

  change_layers_for_num_classes(layers)

  utils.write_prototxt(TRAIN_PROTOTXT, net)


def prepare_test_prototxt():
  net, layers = read_prototxt_net(SRC_TEST_PROTOTXT)

  net.name = 'VGG_kitti_SSD_{}x{}_test'.format(PREPARED_IMG_W, PREPARED_IMG_H)

  layers['data'].data_param.source = TEST_LMDB
  layers['data'].data_param.batch_size = BATCH_SIZE
  layers['data'].annotated_data_param.label_map_file = LABEL_MAP_FILE

  p = layers['detection_out'].detection_output_param
  p.num_classes = NUM_CLASSES
  p.save_output_param.label_map_file = LABEL_MAP_FILE
  p.save_output_param.output_directory = TEST_RESULTS_DIR
  p.save_output_param.output_name_prefix = 'ssd_kitti_'
  p.save_output_param.output_format = 'VOC'
  p.save_output_param.name_size_file = NAME_SIZE_FILE
  p.save_output_param.num_test_image = int(PREPARED_INFO['test_img_count'])

  p = layers['detection_eval'].detection_evaluate_param
  p.name_size_file = NAME_SIZE_FILE
  p.num_classes = NUM_CLASSES

  layers['mbox_conf_reshape'].reshape_param.shape.dim[2] = NUM_CLASSES
  
  change_layers_for_num_classes(layers)

  utils.write_prototxt(TEST_PROTOTXT, net)
    

def start_training():
  cmd = []
  cmd.append(os.path.join(CAFFE_BIN_DIR, 'caffe'))
  cmd.append('train')
  cmd.append('--solver=' + SOLVER_PROTOTXT)
  cmd.append('--weights=' + WEIGHTS_FILE)
  if is_gpu():
    cmd.append('--gpu=' + str(DEVICE_ID))
  utils.run_command(cmd)


if __name__ == '__main__':
  if utils.model_img_w(CAFFE_MODEL_DIR) != PREPARED_IMG_W or \
     utils.model_img_h(CAFFE_MODEL_DIR) != PREPARED_IMG_H:
    print('\nERROR:')
    print('Prepared data has different image size than caffemodel was designed for. ' +
          'Run "prepare" command to recreate train dataset respecting this model.')
    exit(-1)

  print('\nSome clean-up...')
  utils.mkdir(SNAPSHOTS_DIR)
  utils.mkdir(TEST_RESULTS_DIR)

  # Load default prototxt files from selected SSD caffemodel dir,
  # modify them using new parameter values corresponding to current
  # training session, and write as new files into current dir.
  print('\nPreparing prototxts...')
  prepare_train_prototxt()  
  prepare_test_prototxt()  
  prepare_solver_prototxt()
    
  print('\nTraining...')
  start_training()
      
