#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2017;
# - Anton Lokhmotov, 2018.
#

# PACKAGE_DIR
# INSTALL_DIR

ln -s ${INSTALL_DIR}/src/external/mkldnn/install/lib/libmkldnn.so.0 ${INSTALL_DIR}/install/lib
ln -s ${INSTALL_DIR}/src/external/mkl/*/lib/libmklml_intel.so ${INSTALL_DIR}/install/lib
ln -s ${INSTALL_DIR}/src/external/mkl/*/lib/libiomp5.so ${INSTALL_DIR}/install/lib

return 0
