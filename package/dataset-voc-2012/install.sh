#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

# VOC_URL

VOC_TRAIN_NAME="VOC 2012 training dataset"

mkdir ${TRAIN_DIR}
cd ${INSTALL_DIR}/${TRAIN_DIR}
#####################################################################
echo ""
echo "Downloading ${VOC_TRAIN_NAME} from '${VOC_TRAIN_URL}' ..."

wget -c ${VOC_TRAIN_URL} -O ${VOC_TRAIN_ARCHIVE}

if [ "${?}" != "0" ] ; then
  echo "Error: Downloading ${VOC_TRAIN_NAME} from '${VOC_TRAIN_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Unpacking '${VOC_TRAIN_ARCHIVE}' ..."

tar xvf ${VOC_TRAIN_ARCHIVE}
if [ "${?}" != "0" ] ; then
  echo "Error: Unpacking '${VOC_TRAIN_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Deleting '${VOC_TRAIN_ARCHIVE}' ..."

rm ${VOC_TRAIN_ARCHIVE}
if [ "${?}" != "0" ] ; then
  echo "Error: Deleting '${VOC_TRAIN_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################

echo ""
echo "Successfully installed '${VOC_TRAIN_NAME}'"
exit 0
