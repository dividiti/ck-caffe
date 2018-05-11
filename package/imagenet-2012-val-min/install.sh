#! /bin/bash

#
# Installation script for the 2012 ImageNet Large Scale Visual Recognition
# Challenge (ILSVRC'12) validation dataset.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016
# - Grigori Fursin, Grigori.Fursin@cTuning.org, 2016

# PACKAGE_DIR
# INSTALL_DIR

IMAGENET_VAL_TAR=${INSTALL_DIR}/ILSVRC2012_img_val.tar

#####################################################################
echo ""
echo "Checking whether '${IMAGENET_VAL_TAR}' already exists ..."
if [ -f "${IMAGENET_VAL_TAR}" ]
then
  echo "${IMAGENET_VAL_TAR} already exists ..."
  exit 1
fi

#####################################################################
echo ""
echo "Downloading ILSVRC'12 validation dataset from '${IMAGENET_VAL_URL}' ..."

wget -c ${IMAGENET_VAL_URL} -O ${IMAGENET_VAL_TAR}
if [ "${?}" != "0" ] ; then
  echo "Error: Downloading ILSVRC'12 validation set from '${IMAGENET_VAL_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Calculating the MD5 hash of '${IMAGENET_VAL_TAR}' ..."
IMAGENET_VAL_MD5_CALC=($(${CK_MD5SUM_CMD} ${IMAGENET_VAL_TAR}))
if [ "${?}" != "0" ] ; then
  echo "Error: Calculating the MD5 hash of '${IMAGENET_VAL_TAR}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Validating the MD5 hash of '${IMAGENET_VAL_TAR}' ..."
echo "Calculated MD5 hash: ${IMAGENET_VAL_MD5_CALC}"
echo "Reference MD5 hash: ${IMAGENET_VAL_MD5}"
if [ "${IMAGENET_VAL_MD5_CALC}" != "${IMAGENET_VAL_MD5}" ] ; then
  echo "Error: Validating the MD5 hash of '${IMAGENET_VAL_TAR}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Unpacking '${IMAGENET_VAL_TAR}' ..."

cd ${INSTALL_DIR}
tar xvf ${IMAGENET_VAL_TAR}
if [ "${?}" != "0" ] ; then
  echo "Error: Unpacking '${IMAGENET_VAL_TAR}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Removing '${IMAGENET_VAL_TAR}' ..."

cd ${INSTALL_DIR}
rm ${IMAGENET_VAL_TAR}
if [ "${?}" != "0" ] ; then
  echo "Error: Removing '${IMAGENET_VAL_TAR}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Successfully installed the ILSVRC'12 validation dataset ..."
exit 0
