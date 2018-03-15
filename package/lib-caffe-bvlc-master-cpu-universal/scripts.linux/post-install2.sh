#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2017
# - Leo Gordon, 2018
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

    # on a Mac and compiled with Python support:
if [ "$CK_DLL_EXT" = ".dylib" ] && [ "${CAFFE_BUILD_PYTHON}" == "ON" ]
then
    cd "${INSTALL_DIR}/install/python/caffe"
    ln -s _caffe.dylib _caffe.so
fi


return 0
