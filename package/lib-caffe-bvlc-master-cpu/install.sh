#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016
# - Grigori Fursin, Grigori.Fursin@cTuning.org, 2016

# PACKAGE_DIR
# INSTALL_DIR

export CAFFE_PKG_DIR=${PACKAGE_DIR}
export CAFFE_SRC_DIR=${INSTALL_DIR}/src
export CAFFE_BLD_DIR=${CAFFE_SRC_DIR}

#####################################################################
echo ""
echo "Cloning Caffe from '${CAFFE_URL}' ..."

#rm -rf ${CAFFE_SRC_DIR}
#git clone ${CAFFE_URL} --no-checkout ${CAFFE_SRC_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: Cloning Caffe from '${CAFFE_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Checking out the '${CAFFE_BRANCH}' branch of Caffe ..."

cd ${CAFFE_SRC_DIR}
#git checkout ${CAFFE_BRANCH}
if [ "${?}" != "0" ] ; then
  echo "Error: Checking out the '${CAFFE_BRANCH}' branch of Caffe failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Copying automatically prepared Makefile.config to build directory ..."

cp -rf ${CAFFE_PKG_DIR}/Makefile.config ${CAFFE_SRC_DIR}

#####################################################################
echo ""
echo "Building Caffe in ${CAFFE_BLD_DIR} ..."

mkdir -p ${CAFFE_BLD_DIR}
cd ${CAFFE_BLD_DIR}

make -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
if [ "${?}" != "0" ] ; then
  echo "Error: Building Caffe in ${CAFFE_BLD_DIR} failed!"
  exit 1
fi

