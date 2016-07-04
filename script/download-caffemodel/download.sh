#! /bin/bash

#
# Download script for Caffe model weights.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016
# - Grigori Fursin, grigori@dividiti.com, 2016

# PACKAGE_DIR
# INSTALL_DIR

#####################################################################
echo ""
echo "Checking whether '${MODEL_PATH}' already exists ..."
if [ -f "${MODEL_PATH}" ]
then
  echo "Warning: '${MODEL_PATH}' already exists, skipping ..."
  exit 0
fi

#####################################################################
echo ""
echo "Downloading the weights from '${MODEL_URL}' ..."
wget -c ${MODEL_URL} -O ${MODEL_PATH}
if [ "${?}" != "0" ] ; then
  echo "Error: Downloading the weights from '${MODEL_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Calculating the hash of '${MODEL_PATH}' ..."
MODEL_HASH_CALC=($(${MODEL_HASH_CALCULATOR} ${MODEL_PATH}))
if [ "${?}" != "0" ] ; then
  echo "Warning: Calculating the hash of '${MODEL_PATH}' failed!"
fi
echo "Validating the hash of '${MODEL_PATH}' ..."
if [ "${MODEL_HASH_CALC}" != "${MODEL_HASH_REF}" ] ; then
  echo "Warning: ${MODEL_HASH_CALC} (calculated) not equal ${MODEL_HASH_REF} (reference)"
fi

#####################################################################
echo ""
echo "Installed ${MODEL_ENV}=${MODEL_PATH}"
exit 0
