#! /bin/bash

#
# Installation script for ViennaCL.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016.
#

# PACKAGE_DIR
# INSTALL_DIR

export VIENNACL_SRC_DIR=${INSTALL_DIR}/src
export OBJ_DIR=${INSTALL_DIR}/obj

echo ""
echo "Cloning ViennaCL from '${VIENNACL_URL}' ..."
rm -rf ${VIENNACL_SRC_DIR}
git clone ${VIENNACL_URL} --no-checkout ${VIENNACL_SRC_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: Cloning ViennaCL from '${VIENNACL_URL}' failed!"
  exit 1
fi

echo ""
echo "Checking out the '${VIENNACL_TAG}' release of ViennaCL ..."
cd ${VIENNACL_SRC_DIR}
git checkout tags/${VIENNACL_TAG} -b ${VIENNACL_TAG}
if [ "${?}" != "0" ] ; then
  echo "Error: Checking out the '${VIENNACL_TAG}' release of ViennaCL failed!"
  exit 1
fi

echo ""
echo "Configuring ..."

mkdir $OBJ_DIR
cd $OBJ_DIR

cmake ../src
if [ "$?" != "0" ]; then
 echo "Error: failed configuring ..."
 read -p "Press any key to continue!"
 exit $?
fi


echo ""
echo "Building ..."

cmake --build .
if [ "$?" != "0" ]; then
 echo "Error: failed making ..."
 read -p "Press any key to continue!"
 exit $?
fi

echo ""
echo "Installing ..."

cmake -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR} -P cmake_install.cmake
if [ "$?" != "0" ]; then
 echo "Error: failed installing ..."
 read -p "Press any key to continue!"
 exit $?
fi
