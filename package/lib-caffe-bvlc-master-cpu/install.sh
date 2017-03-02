#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016
# - Grigori Fursin, grigori@dividiti.com, 2016

# PACKAGE_DIR
# INSTALL_DIR

export CAFFE_PKG_DIR=${PACKAGE_DIR}
export CAFFE_SRC_DIR=${INSTALL_DIR}/src
export CAFFE_BLD_DIR=${CAFFE_SRC_DIR}

################################################################################
echo ""
echo "Cloning Caffe from '${CAFFE_URL}' ..."

rm -rf ${CAFFE_SRC_DIR}
git clone ${CAFFE_URL} --no-checkout ${CAFFE_SRC_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: Cloning Caffe from '${CAFFE_URL}' failed!"
  exit 1
fi

################################################################################
echo ""
echo "Checking out the '${CAFFE_BRANCH}' branch of Caffe ..."

cd ${CAFFE_SRC_DIR}
git checkout ${CAFFE_BRANCH}
if [ "${?}" != "0" ] ; then
  echo "Error: Checking out the '${CAFFE_BRANCH}' branch of Caffe failed!"
  exit 1
fi

################################################################################
echo ""
echo "Copying automatically generated 'Makefile.config' to '${CAFFE_BLD_DIR}' ..."

cp ${CAFFE_PKG_DIR}/Makefile.config ${CAFFE_BLD_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: Copying automatically generated 'Makefile.config' to '${CAFFE_BLD_DIR}' failed!"
  exit 1
fi

################################################################################
if [ "${CK_ENV_LIB_CLBLAST_DYNAMIC_NAME}" == "libclblast_mali.so" ] ; then
  echo ""
  echo "Editing 'Makefile' in '${CAFFE_BLD_DIR}' to link against Mali-optimized CLBlast overlay ..."
  sed -re 's/clblast/clblast_mali clblast/' --in-place=.bak ${CAFFE_SRC_DIR}/Makefile
  if [ "${?}" != "0" ] ; then
    echo "Error: Editing 'Makefile' in '${CAFFE_BLD_DIR}' failed!"
    exit 1
  fi
fi

################################################################################
echo ""
echo "Building Caffe in '${CAFFE_BLD_DIR}' ..."

mkdir -p ${CAFFE_BLD_DIR}
cd ${CAFFE_BLD_DIR}

# When using protobuf and many processors, build fails
if [ "$CK_JOBS" != "" ] ; then
  JOBS=$CK_JOBS
else
  JOBS=${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
  if [ "$JOBS" -gt "4" ] ; then
    JOBS=4
  fi
fi

# Get used compiler - useful for NVCC, but will work with other packages too ...
CK_COMPILER=`which $CK_CXX`

# Have various problems with parallel compilation ...
make VERBOSE=1 CXX=$CK_COMPILER
# -j $JOBS
if [ "${?}" != "0" ] ; then
  echo "Error: Building Caffe in '${CAFFE_BLD_DIR}' failed!"
  exit 1
fi

