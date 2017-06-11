#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2017
# - Anton Lokhmotov, 2017
#

# PACKAGE_DIR
# INSTALL_DIR

CAFFE_LIB=${INSTALL_DIR}/install/lib
CAFFE_LIB64=${INSTALL_DIR}/install/lib64

if [ ! -d "${CAFFE_LIB}" ] && [ -d "${CAFFE_LIB64}" ] ; then
  echo ""
  echo "Renaming lib64 to lib ..."
  echo ""
  mv ${CAFFE_LIB264} ${CAFFE_LIB}
fi

return 0
