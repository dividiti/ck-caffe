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

cd ${INSTALL_DIR}/src

cp Makefile.config.acl Makefile.config

export ACL_ROOT=${CK_ENV_LIB_ARMCL}

make all distribute -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS} V=1 \
          ACL_INCS="${CK_ENV_LIB_ARMCL_INCLUDE} ${CK_ENV_LIB_ARMCL_SRC} ${CK_ENV_LIB_ARMCL_SRC}/include ${CK_ENV_LIB_OPENBLAS_LIB} ${CK_ENV_LIB_PROTOBUF_HOST_INCLUDE} ${INSTALL_DIR}/src/.build_release/src" \
          ACL_LIBS_DIR="${CK_ENV_LIB_ARMCL_LIB}" \
          ACL_LIBS="arm_compute OpenCL" \
          BLAS_INCLUDE="${CK_ENV_LIB_OPENBLAS_INCLUDE}" \
          BLAS_LIB="${CK_ENV_LIB_OPENBLAS_LIB}"

if [ "${?}" != "0" ] ; then
  echo "Error: make failed!"
  exit 1
fi

mkdir ../install
mkdir ../install/lib
mkdir ../install/include
mkdir ../install/include/caffe
mkdir ../install/include/caffe/proto

cp -rf .build_release/lib/* ../install/lib
cp -rf include ../install
cp -rf .build_release/src/caffe/proto/*.h ../install/include/caffe/proto

return 0

cmake -DCMAKE_BUILD_TYPE=${CK_ENV_CMAKE_BUILD_TYPE:-Release} \
      -DCMAKE_C_COMPILER="${CK_CC_PATH_FOR_CMAKE}" \
      -DCMAKE_C_FLAGS="${CK_CC_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS}" \
      -DCMAKE_CXX_COMPILER="${CK_CXX_PATH_FOR_CMAKE}" \
      -DCMAKE_CXX_FLAGS="${CK_CXX_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS} -I${CK_ENV_LIB_OPENCV_INCLUDE}" \
      -DCMAKE_AR="${CK_AR_PATH_FOR_CMAKE}" \
      -DCMAKE_LINKER="${CK_LD_PATH_FOR_CMAKE}" \
      -DCMAKE_SHARED_LINKER_FLAGS="$CK_OPENMP" \
      -DBUILD_python=${CAFFE_BUILD_PYTHON} \
      -DBUILD_docs=OFF \
      -DCPU_ONLY=ON \
      -DUSE_OPENMP:BOOL=${USE_OPENMP} \
      -DUSE_GREENTEA=OFF \
      -DUSE_LMDB=ON \
      -DUSE_LEVELDB=${USE_LEVELDB} \
      -DUSE_HDF5=ON \
      -DBLAS=open \
      -DGFLAGS_INCLUDE_DIR="${CK_ENV_LIB_GFLAGS_INCLUDE}" \
      -DGLOG_INCLUDE_DIR="${CK_ENV_LIB_GLOG_INCLUDE}" \
      -DGFLAGS_LIBRARY="${CK_ENV_LIB_GFLAGS_LIB}/libgflags.so" \
      -DGLOG_LIBRARY="${CK_ENV_LIB_GLOG_LIB}/libglog.so" \
      -DBoost_ADDITIONAL_VERSIONS="1.62" \
      -DBOOST_ROOT=${CK_ENV_LIB_BOOST} \
      -DBOOST_INCLUDEDIR="${CK_ENV_LIB_BOOST_INCLUDE}" \
      -DBOOST_LIBRARYDIR="${CK_ENV_LIB_BOOST_LIB}" \
      -DBoost_INCLUDE_DIR="${CK_ENV_LIB_BOOST_INCLUDE}" \
      -DBoost_LIBRARY_DIR="${CK_ENV_LIB_BOOST_LIB}" \
      -DHDF5_DIR="${CK_ENV_LIB_HDF5}/share/cmake" \
      -DHDF5_ROOT_DIR="${CK_ENV_LIB_HDF5}/share/cmake" \
      -DHDF5_INCLUDE_DIRS="${CK_ENV_LIB_HDF5_INCLUDE}" \
      -DHDF5_LIBRARIES="${CK_ENV_LIB_HDF5_LIB}/libhdf5.so" \
      -DHDF5_HL_LIBRARIES="${CK_ENV_LIB_HDF5_LIB}/libhdf5_hl.so" \
      -DOpenBLAS_INCLUDE_DIR="${CK_ENV_LIB_OPENBLAS_INCLUDE}" \
      -DOpenBLAS_LIB="${CK_ENV_LIB_OPENBLAS_LIB}/libopenblas.a" \
      -DLMDB_INCLUDE_DIR="${CK_ENV_LIB_LMDB_INCLUDE}" \
      -DLMDB_LIBRARIES="${CK_ENV_LIB_LMDB_LIB}/liblmdb.so" \
      -DOpenCV_DIR="${OPENCV_DIR}" \
      -DPROTOBUF_INCLUDE_DIR="${CK_ENV_LIB_PROTOBUF_HOST_INCLUDE}" \
      -DPROTOBUF_PROTOC_EXECUTABLE="${CK_ENV_LIB_PROTOBUF_HOST}/bin/protoc" \
      -DPROTOBUF_LIBRARY="${CK_ENV_LIB_PROTOBUF_HOST_LIB}/libprotobuf.a" \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}/install" \
      -DCMAKE_VERBOSE_MAKEFILE=ON \
      ../src

#      -DOpenCV_INSTALL_PATH="${CK_ENV_LIB_OPENCV}" \
#      -DOpenCV_INCLUDE_DIRS="${CK_ENV_LIB_OPENCV_INCLUDE}" \
#      -DOpenCV_LIB_DIR_OPT="${CK_ENV_LIB_OPENCV_LIB}" \

#      -DBoost_USE_STATIC_LIBS=ON \
#      -DBoost_NO_SYSTEM_PATHS=ON \

if [ "${?}" != "0" ] ; then
  echo "Error: cmake failed!"
  exit 1
fi

#export CK_MAKE_EXTRA="VERBOSE=1"

export PACKAGE_BUILD_TYPE=skip

return 0
