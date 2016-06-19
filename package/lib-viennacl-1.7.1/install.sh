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
#rm -rf ${VIENNACL_SRC_DIR}
#git clone ${VIENNACL_URL} --no-checkout ${VIENNACL_SRC_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: Cloning ViennaCL from '${VIENNACL_URL}' failed!"
  exit 1
fi

echo ""
echo "Checking out the '${VIENNACL_TAG}' release of ViennaCL ..."
cd ${VIENNACL_SRC_DIR}
#git checkout tags/${VIENNACL_TAG} -b ${VIENNACL_TAG}
if [ "${?}" != "0" ] ; then
  echo "Error: Checking out the '${VIENNACL_TAG}' release of ViennaCL failed!"
  exit 1
fi

echo ""
echo "Configuring ..."

#rm -rf $OBJ_DIR
#mkdir $OBJ_DIR
cd $OBJ_DIR

#-DBOOSTPATH=xyz
#cmake ../src -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}
if [ "$?" != "0" ]; then
 echo "Error: failed configuring ..."
 read -p "Press any key to continue!"
 exit $?
fi

echo ""
echo "Building ..."

#cmake --build .
#make
if [ "$?" != "0" ]; then
 echo "Error: failed making ..."
 read -p "Press any key to continue!"
 exit $?
fi

echo ""
echo "Installing ..."

#cmake -P cmake_install.cmake
#make install
if [ "$?" != "0" ]; then
 echo "Error: failed installing ..."
 read -p "Press any key to continue!"
 exit $?
fi

# Somehow library was not copied via above command
# Doing it manually for now
cp -f $OBJ_DIR/libviennacl/libviennacl.so $INSTALL_DIR/lib
if [ "$?" != "0" ]; then
 echo "Error: copying libviennacl.so failed ..."
 read -p "Press any key to continue!"
 exit $?
fi
