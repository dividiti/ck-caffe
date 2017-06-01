#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

# VOC_URL

VOC_TRAIN_NAME="VOC 2007 training dataset"
VOC_TEST_NAME="VOC 2007 test dataset"

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
cd ${INSTALL_DIR} 
mkdir ${TEST_DIR}
cd ${INSTALL_DIR}/${TEST_DIR}
#####################################################################
echo ""
echo "Downloading ${VOC_TEST_NAME} from '${VOC_TEST_URL}' ..."

wget -c ${VOC_TEST_URL} -O ${VOC_TEST_ARCHIVE}

if [ "${?}" != "0" ] ; then
  echo "Error: Downloading ${VOC_TEST_NAME} from '${VOC_TEST_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Unpacking '${VOC_TEST_ARCHIVE}' ..."

tar xvf ${VOC_TEST_ARCHIVE}
if [ "${?}" != "0" ] ; then
  echo "Error: Unpacking '${VOC_TEST_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Deleting '${VOC_TEST_ARCHIVE}' ..."

rm ${VOC_TEST_ARCHIVE}
if [ "${?}" != "0" ] ; then
  echo "Error: Deleting '${VOC_TEST_ARCHIVE}' failed!"
  exit 1
fi

#####################################################################

echo ""
echo "Successfully installed 'VOC 2007 dataset'"
exit 0
