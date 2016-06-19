#! /bin/bash

#
# Installation script for OpenBLAS.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016.
#

# PACKAGE_DIR
# INSTALL_DIR

export OPENBLAS_SRC_DIR=${INSTALL_DIR}/src
export OPENBLAS_BLD_DIR=${OPENBLAS_SRC_DIR}

echo ""
echo "Cloning OpenBLAS from '${OPENBLAS_URL}' ..."
#rm -rf ${OPENBLAS_SRC_DIR}
#git clone ${OPENBLAS_URL} --no-checkout ${OPENBLAS_SRC_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: Cloning OpenBLAS from '${OPENBLAS_URL}' failed!"
  exit 1
fi

echo ""
echo "Checking out the '${OPENBLAS_TAG}' release of OpenBLAS ..."
cd ${OPENBLAS_SRC_DIR}
#git checkout tags/${OPENBLAS_TAG} -b ${OPENBLAS_TAG}
if [ "${?}" != "0" ] ; then
  echo "Error: Checking out the '${OPENBLAS_TAG}' release of OpenBLAS failed!"
  exit 1
fi

echo ""
echo "Building the '${OPENBLAS_TAG}' release of OpenBLAS ..."
mkdir -p ${OPENBLAS_BLD_DIR}
cd ${OPENBLAS_BLD_DIR}

# Check if ARM target
TARGET=""
if [ "${CK_ANDROID_NDK_ARCH}" == "arm" ] ; then
   export CC=${CK_CC}
   export FC=${CK_FC}
   export AR=${CK_AR}
   TARGET="OSNAME=Android TARGET=ARMV7"
elif [ "${CK_ANDROID_NDK_ARCH}" == "arm64" ] ; then
   export CC=${CK_CC}
   export FC=${CK_FC}
   export AR=${CK_AR}
   TARGET="OSNAME=Android TARGET=ARMV8"
fi

#make -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS} $TARGET
if [ "${?}" != "0" ] ; then
  echo "Error: Building the '${OPENBLAS_TAG}' release of OpenBLAS failed!"
  exit 1
fi

echo ""
echo "Installing the '${OPENBLAS_TAG}' release of OpenBLAS ..."
cd ${OPENBLAS_BLD_DIR}
make PREFIX=${INSTALL_DIR} install
if [ "${?}" != "0" ] ; then
  echo "Error: Installing the '${OPENBLAS_TAG}' release of OpenBLAS failed!"
  exit 1
fi
