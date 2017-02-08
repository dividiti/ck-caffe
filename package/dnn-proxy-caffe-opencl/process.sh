#! /bin/bash

#
# Installation script for CK packages.
#
# See CK LICENSE.txt for licensing details.
# See CK Copyright.txt for copyright details.
#
# Developer(s): Grigori Fursin, 2015
#

# PACKAGE_DIR
# INSTALL_DIR

export LIB_NAME=libdnnproxy

echo ""
echo "Copying dnn-proxy-caffe to src dir ..."
echo ""

mkdir ${INSTALL_DIR}/src

cp ${PACKAGE_DIR}/dnn_proxy.cpp ${INSTALL_DIR}/src
cp ${PACKAGE_DIR}/dnn_proxy.h ${INSTALL_DIR}/src
cp ${PACKAGE_DIR}/dnn_timer.h ${INSTALL_DIR}/src
cp ${PACKAGE_DIR}/classification.h ${INSTALL_DIR}/src
cp ${PACKAGE_DIR}/ck-make.sh ${INSTALL_DIR}/src

cd ${INSTALL_DIR}/src

. ./ck-make.sh
 if [ "${?}" != "0" ] ; then
  echo "Error: Compilation failed in $PWD!" 
  exit 1
 fi
