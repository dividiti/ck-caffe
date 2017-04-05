#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

# COCO_URL

COCO_NAME="COCO validation dataset"
#####################################################################
echo ""
echo "Downloading ${COCO_NAME} from '${COCO_URL}' ..."

wget -c ${COCO_URL} -O ${COCO_ARCHIVE}

if [ "${?}" != "0" ] ; then
  echo "Error: Downloading ${COCO_NAME} from '${COCO_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Calculating the MD5 hash of '${COCO_ARCHIVE}' ..."
COCO_MD5_CALC=($(md5sum ${COCO_ARCHIVE}))
if [ "${?}" != "0" ] ; then
  echo "Error: Calculating the MD5 hash of '${COCO_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Validating the MD5 hash of '${COCO_ARCHIVE}' ..."
echo "Calculated MD5 hash: ${COCO_MD5_CALC}"
echo "Reference MD5 hash: ${COCO_MD5}"
if [ "${COCO_MD5_CALC}" != "${COCO_MD5}" ] ; then
  echo "Error: Validating the MD5 hash of '${COCO_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Unpacking '${COCO_ARCHIVE}' ..."

cd ${INSTALL_DIR}
tar xvf ${COCO_ARCHIVE}
if [ "${?}" != "0" ] ; then
  echo "Error: Unpacking '${COCO_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Deleting '${COCO_ARCHIVE}' ..."

rm ${COCO_ARCHIVE}
if [ "${?}" != "0" ] ; then
  echo "Error: Deleting '${COCO_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Successfully installed ${COCO_NAME} ..."
exit 0


exit 0
