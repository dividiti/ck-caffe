#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2015;
# - Anton Lokhmotov, 2016-2017.
#

# PACKAGE_DIR
# INSTALL_DIR

echo "**************************************************************"
echo "Preparing vars for Caffe ..."

CK_OPENMP="-fopenmp"
if [ "${CK_HAS_OPENMP}" = "0"  ]; then
  CK_OPENMP=""
fi

OPENCV_DIR=${CK_ENV_LIB_OPENCV_JNI}
if [ "${OPENCV_DIR}" == "" ]; then
  OPENCV_DIR=${CK_ENV_LIB_OPENCV}/share/OpenCV
fi

# Print about python
if [ "${CAFFE_BUILD_PYTHON}" == "ON" ] ; then
  echo ""
  echo "You are compiling Caffe with Python support!"
  echo "To use it you need to set up CK env after installation as follows:"
  echo ""
  echo "$ ck virtual env --tags=lib,caffe"
  echo "$ ipython"
  echo ""
  read -p "Press enter to continue"
fi

# For a non-standard CUDA installation path, CUDA_BIN_PATH must be set BEFORE
# running CMake (see https://cmake.org/cmake/help/v3.5/module/FindCUDA.html).
export CUDA_BIN_PATH=${CK_ENV_COMPILER_CUDA}

# Check extra stuff
EXTRA_FLAGS=""


cd ${INSTALL_DIR}/obj

cmake -DCMAKE_BUILD_TYPE=${CK_ENV_CMAKE_BUILD_TYPE:-Release} \
      -DCMAKE_C_COMPILER="${CK_CC_PATH_FOR_CMAKE}" \
      -DCMAKE_C_FLAGS="${CK_CC_FLAGS_FOR_CMAKE} ${CK_CC_FLAGS_ANDROID_TYPICAL} ${EXTRA_FLAGS}" \
      -DCMAKE_CXX_COMPILER="${CK_CXX_PATH_FOR_CMAKE}" \
      -DCMAKE_CXX_FLAGS="${CK_CXX_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS} -I${CK_ENV_LIB_OPENCV_INCLUDE}" \
      -DCMAKE_AR="${CK_AR_PATH_FOR_CMAKE}" \
      -DCMAKE_LINKER="${CK_LD_PATH_FOR_CMAKE}" \
      -DCMAKE_EXE_LINKER_FLAGS="${CK_LINKER_FLAGS_ANDROID_TYPICAL}" \
      -DCMAKE_EXE_LINKER_LIBS="${CK_LINKER_LIBS_ANDROID_TYPICAL}" \
      -DCMAKE_SHARED_LINKER_FLAGS="$CK_OPENMP" \
      -DUSE_OPENMP:BOOL=${USE_OPENMP} \
      -DBLAS=${BLAS_TYPE} \
      -DBUILD_python=${CAFFE_BUILD_PYTHON} \
      -DBUILD_docs=OFF \
      -DCPU_ONLY=OFF \
      -DUSE_CUDA=${USE_CUDA} \
      -DCUDA_USE_STATIC_CUDA_RUNTIME=OFF \
      -DCUDA_NVCC_FLAGS="-D_FORCE_INLINES -Wno-deprecated-gpu-targets" \
      -DUSE_LIBDNN:BOOL=${USE_LIBDNN} \
      -DUSE_CLBLAS:BOOL=${USE_CLBLAS} \
      -DUSE_CLBLAST:BOOL=${USE_CLBLAST} \
      -DUSE_ISAAC:BOOL=${USE_ISAAC} \
      -DUSE_GREENTEA=OFF \
      -DUSE_LMDB=ON \
      -DUSE_LEVELDB=${USE_LEVELDB} \
      -DUSE_HDF5=ON \
      -DDISABLE_DEVICE_HOST_UNIFIED_MEMORY=${DISABLE_DEVICE_HOST_UNIFIED_MEMORY} \
      -DDISABLE_DOUBLE_SUPPORT=${DISABLE_DOUBLE_SUPPORT} \
      -DBoost_ADDITIONAL_VERSIONS="1.62" \
      -DBoost_NO_SYSTEM_PATHS=ON \
      -DBOOST_ROOT=${CK_ENV_LIB_BOOST} \
      -DBOOST_INCLUDEDIR="${CK_ENV_LIB_BOOST_INCLUDE}" \
      -DBOOST_LIBRARYDIR="${CK_ENV_LIB_BOOST_LIB}" \
      -DBoost_INCLUDE_DIR="${CK_ENV_LIB_BOOST_INCLUDE}" \
      -DBoost_LIBRARY_DIR="${CK_ENV_LIB_BOOST_LIB}" \
      -DGFLAGS_INCLUDE_DIR="${CK_ENV_LIB_GFLAGS_INCLUDE}" \
      -DGLOG_INCLUDE_DIR="${CK_ENV_LIB_GLOG_INCLUDE}" \
      -DGFLAGS_LIBRARY="${CK_ENV_LIB_GFLAGS_LIB}/libgflags.so" \
      -DGLOG_LIBRARY="${CK_ENV_LIB_GLOG_LIB}/libglog.so" \
      -DOpenBLAS_INCLUDE_DIR="${CK_ENV_LIB_OPENBLAS_INCLUDE}" \
      -DOpenBLAS_LIB="${CK_ENV_LIB_OPENBLAS_LIB}/libopenblas.a" \
      -DLMDB_INCLUDE_DIR="${CK_ENV_LIB_LMDB_INCLUDE}" \
      -DLMDB_LIBRARIES="${CK_ENV_LIB_LMDB_LIB}/liblmdb.so" \
      -DOpenCV_DIR="${OPENCV_DIR}" \
      -DHDF5_DIR="${CK_ENV_LIB_HDF5}/share/cmake" \
      -DHDF5_ROOT_DIR="${CK_ENV_LIB_HDF5}/share/cmake" \
      -DHDF5_INCLUDE_DIRS="${CK_ENV_LIB_HDF5_INCLUDE}" \
      -DHDF5_LIBRARIES="${CK_ENV_LIB_HDF5_LIB}/libhdf5.so" \
      -DHDF5_HL_LIBRARIES="${CK_ENV_LIB_HDF5_LIB}/libhdf5_hl.so" \
      -DPROTOBUF_INCLUDE_DIR="${CK_ENV_LIB_PROTOBUF_HOST_INCLUDE}" \
      -DPROTOBUF_LIBRARY="${CK_ENV_LIB_PROTOBUF_HOST_LIB}/libprotobuf.a" \
      -DPROTOBUF_PROTOC_EXECUTABLE="${CK_ENV_LIB_PROTOBUF_HOST}/bin/protoc" \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}/install" \
      ${CK_CMAKE_EXTRA} \
      ../src

if [ "${?}" != "0" ] ; then
  echo "Error: cmake failed!"
  exit 1
fi

#export CK_MAKE_EXTRA="VERBOSE=1"

export PACKAGE_BUILD_TYPE=skip

return 0
