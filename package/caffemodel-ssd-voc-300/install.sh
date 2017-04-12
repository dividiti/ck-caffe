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

# ORIGINAL_PACKAGE_DIR (path to original package even if scripts are used from some other package or script)
# PACKAGE_DIR (path where scripts are reused)
# INSTALL_DIR

export MODEL_PATH=${INSTALL_DIR}/${MODEL_FILE}

#####################################################################
echo ""
echo "Checking whether '${MODEL_PATH}' already exists ..."
if [ -f "${MODEL_PATH}" ]
then
  echo "Warning: '${MODEL_PATH}' already exists, skipping ..."
  exit 0
fi

#####################################################################
cd ${INSTALL_DIR}

echo ""
echo "Downloading the model files ..."

ggID=${PACKAGE_GOOGLE_DRIVE_ID}
ggURL='https://drive.google.com/uc?export=download'  
curl -sc /tmp/gcokie "${ggURL}&id=${ggID}" >/dev/null
getcode="$(awk '/_warning_/ {print $NF}' /tmp/gcokie)"  
curl -Lb /tmp/gcokie "${ggURL}&confirm=${getcode}&id=${ggID}" -o ${PACKAGE_NAME}

if [ "${?}" != "0" ] ; then
  echo "Error: Downloading the weights from '${PACKAGE_URL}' failed!"
  exit 1
fi

#####################################################################

echo ""
echo "Ungzipping archive ..."

if [ -f ${PACKAGE_NAME1} ] ; then
    rm -f ${PACKAGE_NAME1}
fi

gzip -d ${PACKAGE_NAME}
if [ "${?}" != "0" ] ; then
    echo "Error: ungzipping package failed!"
    exit 1
fi

#####################################################################

echo ""
echo "Untarring archive ..."

tar xvf ${PACKAGE_NAME1}
if [ "${?}" != "0" ] ; then
    echo "Error: untaring package failed!"
    exit 1
fi

#####################################################################
rm ${PACKAGE_NAME1}
cd ${INSTALL_DIR}/${SUBPACKAGE_NAME1}/${SUBPACKAGE_NAME2}/${SUBPACKAGE_NAME3}/${SUBPACKAGE_NAME4} && mv * ../../../..
rm -rf ${INSTALL_DIR}/models

#####################################################################
echo ""
echo "Copying net topology files to '${INSTALL_DIR}' ..."

cp -f ${ORIGINAL_PACKAGE_DIR}/*.prototxt ${INSTALL_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: copying net topology files failed!"
  exit 1
fi

exit 0
