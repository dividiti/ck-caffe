#! /bin/bash

#
# Installation script for the 2012 ImageNet Large Scale Visual Recognition
# Challenge (ILSVRC'12) validation dataset.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016
# - Grigori Fursin, Grigori.Fursin@cTuning.org, 2016

# PACKAGE_DIR
# INSTALL_DIR

export CK_CAFFE_IMAGENET_VAL_LMDB=${INSTALL_DIR}/data

# Need to delete install dir otherwise CAFFE fails ...
rm -rf ${CK_CAFFE_IMAGENET_VAL_LMDB}

#####################################################################
echo ""
echo "Converting images ..."

GLOG_logtostderr=1 
    $CAFFE_INSTALL_DIR/bin/convert_imageset \
    -resize_height=$RESIZE_HEIGHT -resize_width=$RESIZE_WIDTH $SHUFFLE \
    $CK_CAFFE_IMAGENET_VAL \
    $CK_CAFFE_IMAGENET_VAL_TXT \
    $CK_CAFFE_IMAGENET_VAL_LMDB

if [ "${?}" != "0" ] ; then
  echo "Error: Converting failed in ${PWD}!"
  exit 1
fi

cd ${CK_CAFFE_IMAGENET_VAL_LMDB}

#####################################################################
echo ""
echo "Successfully converted images ..."
exit 0
