#!/usr/bin/env python
#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

import json
import imp
import os
import shutil
import subprocess

from google.protobuf import text_format


# Should be more robust criterion, may be lib should proivde some env var
def model_img_w(model_path): return 300 if '-300' in model_path else 512
def model_img_h(model_path): return 300 if '-300' in model_path else 512


def run_command(args_list):
  print(' '.join(args_list))
  process = subprocess.Popen(args_list, stdout=subprocess.PIPE)
  output = process.communicate()[0]
  print(output)


# Despite of CK_ENV_LIB_CAFFE_PYTHON is in PYTHONPATH, we can't import caffe_pb2
# because of caffe.proto is not a package (at least in package:lib-caffe-ssd-cpu)
def import_caffe_pb2():
  caffe_python = os.getenv('CK_ENV_LIB_CAFFE_PYTHON')
  module_path = os.path.join(caffe_python, 'caffe', 'proto', 'caffe_pb2.py')
  return imp.load_source('caffe_pb2', module_path)  


def read_json(file_name):
  with open(file_name, 'r') as f:
    return json.load(f)

def write_json(file_name, obj):
  with open(file_name, 'w') as f:
    json.dump(obj, f, indent=2, sort_keys=True)


def read_text(file_name):
  with open(file_name, 'r') as f:
    return f.read()

def write_text(file_name, txt):
  with open(file_name, 'w') as f:
    f.write(txt)


def read_prototxt(file_name, proto):
  txt = read_text(file_name)  
  text_format.Merge(txt, proto)

def write_prototxt(file_name, proto):
  txt = text_format.MessageToString(proto)
  write_text(file_name, txt)


def rmdir(dir_name):
  if os.path.isdir(dir_name):
    shutil.rmtree(dir_name)

def mkdir(dir_name):
  if os.path.isdir(dir_name):
    shutil.rmtree(dir_name)
  os.mkdir(dir_name)
