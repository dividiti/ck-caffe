#! /bin/bash

#
# Installation script for the 2012 ImageNet Large Scale Visual Recognition
# Challenge (ILSVRC'12) auxiliary dataset.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016
# - Grigori Fursin, Grigori.Fursin@cTuning.org, 2016

# PACKAGE_DIR
# INSTALL_DIR

FULL_PATH=${INSTALL_DIR}/${DOWNLOAD_FILE}
FULL_URL=${DOWNLOAD_URL}/${DOWNLOAD_FILE}

#####################################################################
echo ""
echo "Checking whether '${FULL_PATH}' already exists ..."
if [ -f "${FULL_PATH}" ]
then
  echo "  ${DOWNLOAD_FILE} already exists ..."
  exit 1
fi

#####################################################################
echo ""
echo "Downloading ${DOWNLOAD_NAME} from '${FULL_URL}' ..."

wget -c ${FULL_URL} -O ${FULL_PATH}
if [ "${?}" != "0" ] ; then
  echo "Error: Downloading ${DOWNLOAD_NAME} from '${FULL_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Calculating the MD5 hash of '${DOWNLOAD_FILE}' ..."
DOWNLOAD_FILE_MD5_CALC=($(${CK_MD5SUM_CMD} ${FULL_PATH}))
if [ "${?}" != "0" ] ; then
  echo "Error: Calculating the MD5 hash of '${DOWNLOAD_FILE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Validating the MD5 hash of '${DOWNLOAD_FILE}' ..."
echo "Calculated MD5 hash: ${DOWNLOAD_FILE_MD5_CALC}"
echo "Reference MD5 hash: ${DOWNLOAD_FILE_MD5}"
if [ "${DOWNLOAD_FILE_MD5_CALC}" != "${DOWNLOAD_FILE_MD5}" ] ; then
  echo "Error: Validating the MD5 hash of '${DOWNLOAD_FILE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Unpacking '${DOWNLOAD_FILE}' ..."

cd ${INSTALL_DIR}
tar -xf ${DOWNLOAD_FILE} && rm -f ${DOWNLOAD_FILE}
if [ "${?}" != "0" ] ; then
  echo "Error: Unpacking '${DOWNLOAD_FILE}' failed!"
  exit 1
fi

# Delete weird MacOS X files.
rm -rf ${INSTALL_DIR}/._*
# Set as executable.
chmod 755 ${INSTALL_DIR}/imagenet*

#####################################################################
echo ""
echo "Successfully installed the ${DOWNLOAD_NAME} validation dataset ..."
exit 0
