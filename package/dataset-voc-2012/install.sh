#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

# VOC_URL

VOC_NAME="VOC validation dataset"
#####################################################################
echo ""
echo "Downloading ${VOC_NAME} from '${VOC_URL}' ..."

wget -c ${VOC_URL} -O ${VOC_ARCHIVE}

if [ "${?}" != "0" ] ; then
  echo "Error: Downloading ${VOC_NAME} from '${VOC_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Calculating the MD5 hash of '${VOC_ARCHIVE}' ..."
VOC_MD5_CALC=($(md5sum ${VOC_ARCHIVE}))
if [ "${?}" != "0" ] ; then
  echo "Error: Calculating the MD5 hash of '${VOC_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Validating the MD5 hash of '${VOC_ARCHIVE}' ..."
echo "Calculated MD5 hash: ${VOC_MD5_CALC}"
echo "Reference MD5 hash: ${VOC_MD5}"
if [ "${VOC_MD5_CALC}" != "${VOC_MD5}" ] ; then
  echo "Error: Validating the MD5 hash of '${VOC_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Unpacking '${VOC_ARCHIVE}' ..."

cd ${INSTALL_DIR}
tar xvf ${VOC_ARCHIVE}
if [ "${?}" != "0" ] ; then
  echo "Error: Unpacking '${VOC_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Deleting '${VOC_ARCHIVE}' ..."

rm ${VOC_ARCHIVE}
if [ "${?}" != "0" ] ; then
  echo "Error: Deleting '${VOC_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Successfully installed ${VOC_NAME} ..."
exit 0


exit 0
