#! /bin/bash

#
# Installation script for clBLAS.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2015;
# - Anton Lokhmotov, 2016.
#

# PACKAGE_DIR
# INSTALL_DIR

cd ${INSTALL_DIR}

############################################################
echo ""
echo "Cloning package from '${PACKAGE_URL}' ..."

rm -rf src

git clone ${PACKAGE_URL} src
if [ "${?}" != "0" ] ; then
  echo "Error: cloning package failed!"
  exit 1
fi

cd src
git checkout ${PACKAGE_BRANCH}

############################################################
echo ""
echo "Cleaning ..."

cd ${INSTALL_DIR}

rm -rf obj
mkdir obj
cd obj

############################################################
echo ""
echo "Executing cmake ..."

CK_TOOLCHAIN=android.toolchain.cmake
if [ "${CK_ENV_LIB_CRYSTAX_LIB}" != "" ] ; then
  CK_TOOLCHAIN=toolchain.cmake
fi

echo "-DVIENNACL_HOME=${CK_ENV_LIB_VIENNACL}"
echo "-DVIENNACL_DIR=${CK_ENV_LIB_VIENNACL_INCLUDE}"
echo "-DViennaCL_DIR=${CK_ENV_LIB_VIENNACL_INCLUDE}"
echo "-DViennaCL_INCLUDE_DIRS=${CK_ENV_LIB_VIENNACL_INCLUDE}"
echo "-DViennaCL_INCLUDE_DIR=${CK_ENV_LIB_VIENNACL_INCLUDE}"
echo "-DViennaCL_LIBRARIES=${CK_ENV_LIB_VIENNACL_LIB}"


export VIENNACL_HOME=${CK_ENV_LIB_VIENNACL}

cmake -DCMAKE_TOOLCHAIN_FILE="${PACKAGE_DIR}/misc/${CK_TOOLCHAIN}" \
      -DANDROID_NDK="${CK_ANDROID_NDK_ROOT_DIR}" \
      -DCMAKE_BUILD_TYPE=Release \
      -DANDROID_ABI="${CK_ANDROID_ABI}" \
      -DANDROID_NATIVE_API_LEVEL=${CK_ANDROID_API_LEVEL} \
      -DANDROID_USE_OPENMP=ON \
      -DBUILD_python=OFF \
      -DBUILD_docs=OFF \
      -DCPU_ONLY=OFF \
      -DUSE_CUDA=OFF \
      -DUSE_GREENTEA=ON \
      -DUSE_CLBLAST=ON \
      -DUSE_LMDB=ON \
      -DUSE_LEVELDB=OFF \
      -DUSE_HDF5=OFF \
      -DBLAS=open \
      -DBoost_ADDITIONAL_VERSIONS="1.62" \
      -DBoost_NO_SYSTEM_PATHS=ON \
      -DBOOST_ROOT=${CK_ENV_LIB_BOOST} \
      -DBOOST_INCLUDEDIR="${CK_ENV_LIB_BOOST_INCLUDE}" \
      -DBOOST_LIBRARYDIR="${CK_ENV_LIB_BOOST_LIB}" \
      -DBoost_INCLUDE_DIR="${CK_ENV_LIB_BOOST_INCLUDE}" \
      -DBoost_LIBRARY_DIR="${CK_ENV_LIB_BOOST_LIB}" \
      -DGFLAGS_INCLUDE_DIR="${CK_ENV_LIB_GFLAGS_INCLUDE}" \
      -DGFLAGS_LIBRARY="${CK_ENV_LIB_GFLAGS_LIB}/libgflags.a" \
      -DGLOG_INCLUDE_DIR="${CK_ENV_LIB_GLOG_INCLUDE}" \
      -DGLOG_LIBRARY="${CK_ENV_LIB_GLOG_LIB}/libglog.a" \
      -DVIENNACL_HOME="${CK_ENV_LIB_VIENNACL}" \
      -DVIENNACL_DIR="${CK_ENV_LIB_VIENNACL_INCLUDE}" \
      -DViennaCL_DIR="${CK_ENV_LIB_VIENNACL_INCLUDE}" \
      -DViennaCL_INCLUDE_DIRS="${CK_ENV_LIB_VIENNACL_INCLUDE}" \
      -DViennaCL_INCLUDE_DIR="${CK_ENV_LIB_VIENNACL_INCLUDE}" \
      -DViennaCL_LIBRARIES="${CK_ENV_LIB_VIENNACL_LIB}" \
      -DOpenBLAS_INCLUDE_DIR="${CK_ENV_LIB_OPENBLAS_INCLUDE}" \
      -DOpenBLAS_LIB="${CK_ENV_LIB_OPENBLAS_LIB}/libopenblas.a" \
      -DLMDB_INCLUDE_DIR="${CK_ENV_LIB_LMDB_INCLUDE}" \
      -DLMDB_LIBRARIES="${CK_ENV_LIB_LMDB_LIB}/liblmdb.a" \
      -DOpenCV_DIR="${CK_ENV_LIB_OPENCV_JNI}" \
      -DPROTOBUF_INCLUDE_DIR="${CK_ENV_LIB_PROTOBUF_INCLUDE}" \
      -DPROTOBUF_LIBRARY="${CK_ENV_LIB_PROTOBUF_LIB}/libprotobuf.a" \
      -DPROTOBUF_PROTOC_EXECUTABLE="${CK_ENV_LIB_PROTOBUF_HOST}/bin/protoc" \
      -DOpenCL_DIR="${CK_ENV_LIB_OPENCL}" \
      -DOPENCL_ROOT="${CK_ENV_LIB_OPENCL}" \
      -DOPENCL_LIBRARIES="${CK_ENV_LIB_OPENCL_LIB}/libOpenCL.so" \
      -DOPENCL_INCLUDE_DIRS="${CK_ENV_LIB_OPENCL_INCLUDE}" \
      -DCLBlast_DIR="${CK_ENV_LIB_CLBLAST}" \
      -DCLBLAST_LIB="${CK_ENV_LIB_CLBLAST_LIB}" \
      -DCLBLAST_INCLUDE="${CK_ENV_LIB_CLBLAST_INCLUDE}" \
      -DANDROID_STL=gnustl_static \
      -DBoost_USE_STATIC_LIBS=ON \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}/install" \
      -DCMAKE_PREFIX_PATH:PATH="${CK_ENV_LIB_CLBLAST}" \
      ../src

if [ "${?}" != "0" ] ; then
  echo "Error: cmake failed!"
  exit 1
fi

############################################################
echo ""
echo "Building package ..."

make VERBOSE=1 -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
if [ "${?}" != "0" ] ; then
  echo "Error: build failed!"
  exit 1
fi

############################################################
echo ""
echo "Installing package ..."

rm -rf install

make install/strip
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

exit 0
