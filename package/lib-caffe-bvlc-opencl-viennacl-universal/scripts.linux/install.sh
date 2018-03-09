#! /bin/bash

#
# Installation script for Caffe.
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
  echo "To use it you need to set up CK env as following (after installation)":
  echo ""
  echo "$ ck virtual env --tags=lib,caffe"
  echo "$ ipython"
  echo ""
  read -p "Press enter to continue"
fi

# Check extra stuff
EXTRA_FLAGS=""

if [ "${CK_VIENNACL_DEBUG}" == "ON" ] ; then
  EXTRA_FLAGS="$EXTRA_FLAGS -DVIENNACL_DEBUG_ALL"
fi

export CLBlast_DIR=${CK_ENV_LIB_CLBLAST}

cd ${INSTALL_DIR}/obj

cmake -DCMAKE_BUILD_TYPE=${CK_ENV_CMAKE_BUILD_TYPE:-Release} \
      -DCMAKE_C_COMPILER="${CK_CC_PATH_FOR_CMAKE}" \
      -DCMAKE_C_FLAGS="${CK_CC_FLAGS_FOR_CMAKE} ${CK_CC_FLAGS_ANDROID_TYPICAL} ${EXTRA_FLAGS}" \
      -DCMAKE_CXX_COMPILER="${CK_CXX_PATH_FOR_CMAKE}" \
      -DCMAKE_CXX_FLAGS="${CK_CXX_FLAGS_FOR_CMAKE} ${CK_CXX_FLAGS_ANDROID_TYPICAL} ${EXTRA_FLAGS} -I${CK_ENV_LIB_OPENCV_INCLUDE}" \
      -DCMAKE_AR="${CK_AR_PATH_FOR_CMAKE}" \
      -DCMAKE_LINKER="${CK_LD_PATH_FOR_CMAKE}" \
      -DCMAKE_EXE_LINKER_FLAGS="${CK_LINKER_FLAGS_ANDROID_TYPICAL}" \
      -DCMAKE_EXE_LINKER_LIBS="${CK_LINKER_LIBS_ANDROID_TYPICAL}" \
      -DCMAKE_SHARED_LINKER_FLAGS="$CK_OPENMP" \
      -DBUILD_python=${CAFFE_BUILD_PYTHON} \
      -DBUILD_docs=OFF \
      -DBLAS=${BLAS_TYPE} \
      -DCPU_ONLY:BOOL=${CPU_ONLY} \
      -DUSE_OPENMP:BOOL=${USE_OPENMP} \
      -DUSE_FFT:BOOL=${USE_FFT} \
      -DUSE_GREENTEA:BOOL=${USE_GREENTEA} \
      -DUSE_CUDA:BOOL=${USE_CUDA} \
      -DUSE_CUDNN:BOOL=${USE_CUDNN} \
      -DUSE_LIBDNN:BOOL=${USE_LIBDNN} \
      -DUSE_CLBLAS:BOOL=${USE_CLBLAS} \
      -DUSE_CLBLAST:BOOL=${USE_CLBLAST} \
      -DUSE_NCCL:BOOL=${USE_NCCL} \
      -DUSE_ISAAC:BOOL=${USE_ISAAC} \
      -DUSE_INTEL_SPATIAL=${USE_INTEL_SPATIAL} \
      -DUSE_INDEX64:BOOL=${USE_INDEX64} \
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
      -DVIENNACL_HOME="${CK_ENV_LIB_VIENNACL}" \
      -DVIENNACL_DIR="${CK_ENV_LIB_VIENNACL_INCLUDE}" \
      -DViennaCL_DIR="${CK_ENV_LIB_VIENNACL_INCLUDE}" \
      -DViennaCL_INCLUDE_DIRS="${CK_ENV_LIB_VIENNACL_INCLUDE}" \
      -DViennaCL_INCLUDE_DIR="${CK_ENV_LIB_VIENNACL_INCLUDE}" \
      -DViennaCL_LIBRARIES="${CK_ENV_LIB_VIENNACL_LIB}" \
      -DOpenCL_DIR="${CK_ENV_LIB_OPENCL}" \
      -DOPENCL_ROOT="${CK_ENV_LIB_OPENCL}" \
      -DOPENCL_LIBRARIES="${CK_ENV_LIB_OPENCL_LIB}/libOpenCL.so" \
      -DOPENCL_INCLUDE_DIRS="${CK_ENV_LIB_OPENCL_INCLUDE}" \
      -DCLBlast_DIR="${CK_ENV_LIB_CLBLAST}" \
      -DCLBLAST_LIB="${CK_ENV_LIB_CLBLAST_LIB}" \
      -DCLBLAST_INCLUDE="${CK_ENV_LIB_CLBLAST_INCLUDE}" \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}/install" \
      ../src

if [ "${?}" != "0" ] ; then
  echo "Error: cmake failed!"
  exit 1
fi

#export CK_MAKE_EXTRA="VERBOSE=1"

export PACKAGE_BUILD_TYPE=skip

return 0
