#! /bin/bash

function download {
  NAME=${1}
  URL=${2}
  ARCH=${3}
  FULL_URL=${URL}/${ARCH}
  echo ""
  echo "Downloading ${NAME} from '${FULL_URL}' ..."

  wget -c ${FULL_URL} -O ${ARCH}

  if [ "${?}" != "0" ] ; then
    echo "Error: Downloading ${NAME} from '${FULL_URL}' failed!"
    exit 1
  fi
}

function uncompress {
  ARCH=${1}
  echo ""
  echo "Unzipping archive ..."

  unzip ${ARCH}
  if [ "${?}" != "0" ] ; then
    echo "Error: unzipping package failed!"
    exit 1
  fi
  rm ${ARCH}
}

# #####################################################################

# TRAIN_IMG_NAME="COCO 2014 train dataset"
# download "${TRAIN_IMG_NAME}" ${IMAGE_URL} "${TRAIN_IMAGE_ARCHIVE}"
# uncompress "${TRAIN_IMAGE_ARCHIVE}"

# #####################################################################

# VAL_IMG_NAME="COCO 2014 validation dataset"
# download "${VAL_IMG_NAME}" ${IMAGE_URL} "${VAL_IMAGE_ARCHIVE}"
# uncompress "${VAL_IMAGE_ARCHIVE}"

# #####################################################################

# TEST_IMG_NAME="COCO 2014 test dataset"
# download "${TEST_IMG_NAME}" ${IMAGE_URL} "${TEST_IMAGE_ARCHIVE}"
# uncompress "${TEST_IMAGE_ARCHIVE}"

# #####################################################################

TRAINVAL_OBJ_INSTANCES_NAME="COCO 2014 Train/Val object instances"
download "${TRAINVAL_OBJ_INSTANCES_NAME}" ${ANNOTATION_URL} "${TRAINVAL_OBJ_INSTANCES_ARCHIVE}"
uncompress "${TRAINVAL_OBJ_INSTANCES_ARCHIVE}"

#####################################################################

TRAINVAL_PERSON_KEYPOINTS_NAME="COCO 2014 Train/Val person keypoints"
download "${TRAINVAL_PERSON_KEYPOINTS_NAME}" ${ANNOTATION_URL} "${TRAINVAL_PERSON_KEYPOINTS_ARCHIVE}"
uncompress "${TRAINVAL_PERSON_KEYPOINTS_ARCHIVE}"

#####################################################################

TRAINVAL_IMG_CAPTIONS_NAME="COCO 2014 Train/Val image captions"
download "${TRAINVAL_IMG_CAPTIONS_NAME}" ${ANNOTATION_URL} "${TRAINVAL_IMG_CAPTIONS_ARCHIVE}"
uncompress "${TRAINVAL_IMG_CAPTIONS_ARCHIVE}"

exit 0
