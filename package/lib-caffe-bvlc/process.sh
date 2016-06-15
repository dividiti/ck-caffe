#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, 2016.
#

# PACKAGE_DIR
# INSTALL_DIR

export CAFFE_SRC_DIR=${INSTALL_DIR}/src
export CAFFE_BUILD_DIR=${CAFFE_SRC_DIR}

${CAFFE_BUILD_SCRIPTS_DIR}/1_clone.sh
${CAFFE_BUILD_SCRIPTS_DIR}/2_checkout.sh
${CAFFE_BUILD_SCRIPTS_DIR}/3_build.sh
