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

pwd
set > xyz-123.txt
exit 1

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
git checkout ${CAFFE_BRANCH}
if [ "${?}" != "0" ] ; then
  echo "Error: Checking out the '${CAFFE_BRANCH}' branch of Caffe failed!"
  exit 1
fi

#####################################################################
exit 1

${CAFFE_PKG_DIR}/3_config.py \
  ${CAFFE_PKG_DIR}/${CAFFE_CONFIG_TEMPLATE_FILE} \
  ${CAFFE_PKG_DIR}/${CAFFE_CONFIG_SETTINGS_IN_FILE} \
  ${CAFFE_PKG_DIR}/${CAFFE_CONFIG_SETTINGS_OUT_FILE} \
  ${CAFFE_BLD_DIR}/Makefile.config

${CAFFE_BUILD_SCRIPTS_DIR}/4_build.sh
