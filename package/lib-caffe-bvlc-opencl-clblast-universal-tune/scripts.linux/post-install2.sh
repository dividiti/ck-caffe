#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2017
#

# PACKAGE_DIR
# INSTALL_DIR

CAFFE_LIB1=${INSTALL_DIR}/install/lib
CAFFE_LIB2=${INSTALL_DIR}/install/lib64

if [ ! -d "${CAFFE_LIB1}" ] && [ -d "${CAFFE_LIB2}" ] ; then
  echo ""
  echo "Renaming lib64 to lib "
  echo ""

  mv ${CAFFE_LIB2} ${CAFFE_LIB1}
fi

return 0
