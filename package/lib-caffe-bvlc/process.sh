#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016.
#

# PACKAGE_DIR
# INSTALL_DIR

export CAFFE_PKG_DIR=${PACKAGE_DIR}
export CAFFE_SRC_DIR=${INSTALL_DIR}/src
export CAFFE_BLD_DIR=${CAFFE_SRC_DIR}

#${CAFFE_BUILD_SCRIPTS_DIR}/1_clone.sh
#
#${CAFFE_BUILD_SCRIPTS_DIR}/2_checkout.sh

${CAFFE_BUILD_SCRIPTS_DIR}/3_config.py \
  ${CAFFE_PKG_DIR}/${CAFFE_CONFIG_TEMPLATE_FILE} \
  ${CAFFE_PKG_DIR}/${CAFFE_CONFIG_SETTINGS_IN_FILE} \
  ${CAFFE_PKG_DIR}/${CAFFE_CONFIG_SETTINGS_OUT_FILE} \
  ${CAFFE_BLD_DIR}/Makefile.config

${CAFFE_BUILD_SCRIPTS_DIR}/4_build.sh
