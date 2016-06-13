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

echo ""
echo "Getting Caffe from '${CAFFE_URL}' ..."
rm -rf ${CAFFE_SRC_DIR}
git clone ${CAFFE_URL} --no-checkout ${CAFFE_SRC_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: Getting Caffe from '${CAFFE_URL}' failed!"
  exit 1
fi

echo ""
echo "Checking out the '${CAFFE_BRANCH}' branch of Caffe ..."
cd ${CAFFE_SRC_DIR}
git checkout ${CAFFE_BRANCH}
if [ "${?}" != "0" ] ; then
  echo "Error: Checking out the '${CAFFE_BRANCH}' branch of Caffe failed!"
  exit 1
fi

echo ""
echo "Building the '${CAFFE_BRANCH}' branch of Caffe ..."
echo "TODO"
#mkdir -p ${CAFFE_BUILD_DIR}
#cd ${CAFFE_BUILD_DIR}
#make -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
#if [ "${?}" != "0" ] ; then
#  echo "Error: Building the '${CAFFE_BRANCH}' branch of Caffe failed!"
#  exit 1
#fi
