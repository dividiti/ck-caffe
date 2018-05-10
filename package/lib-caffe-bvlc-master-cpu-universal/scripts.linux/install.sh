#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2015;
# - Anton Lokhmotov, 2016;
# - Leo Gordon, 2018.
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

    if [ -z "$CK_ENV_COMPILER_PYTHON_FILE" ]; then
        echo "CK_ENV_COMPILER_PYTHON_FILE is not defined -- make sure Python is set as a dependency"
        exit 1
    fi

    echo "To use it you need to set up CK env as follows (after installation)":
    echo ""
    echo "$ ck virtual env --tags=lib,caffe"
    echo "$ python -c 'import caffe' && echo 'Caffe for Python seems to be healthy'"
    echo ""
    read -p "Press enter to continue"
fi

    # on a Mac and compiling with LLVM:
if [ "$CK_DLL_EXT" == ".dylib" ] && [ -n "$CK_ENV_COMPILER_LLVM_SET" ]
then
    EXTRA_FLAGS="-flax-vector-conversions"
else
    EXTRA_FLAGS=""
fi

    # on a Mac and compiled with Python support:
if [ "$CK_DLL_EXT" == ".dylib" ] && [ "${CAFFE_BUILD_PYTHON}" == "ON" ]
then
    PYTHON_ROOT=`${CK_ENV_COMPILER_PYTHON_FILE} -c 'import sysconfig ; print(sysconfig.get_paths()["data"])'`

    if [ "${?}" != "0" ] ; then
        echo "Error: cannot detect Python paths, which likely means your Python is <2.7 and not supported by Caffe"
        exit 1
    fi

    SPECIFIC_PYTHON_PATHS=" -DPYTHON_LIBRARY=${PYTHON_ROOT}/Python -DPYTHON_INCLUDE_DIR=${PYTHON_ROOT}/Headers"
else
    SPECIFIC_PYTHON_PATHS=""
fi

cd ${INSTALL_DIR}/obj

cmake -DCMAKE_BUILD_TYPE=${CK_ENV_CMAKE_BUILD_TYPE:-Release} \
      -DCMAKE_C_COMPILER="${CK_CC_PATH_FOR_CMAKE}" \
      -DCMAKE_C_FLAGS="${CK_CC_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS}" \
      -DCMAKE_CXX_COMPILER="${CK_CXX_PATH_FOR_CMAKE}" \
      -DCMAKE_CXX_FLAGS="${CK_CXX_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS} -I${CK_ENV_LIB_OPENCV_INCLUDE} ${CK_CXX_COMPILER_STDLIB}" \
      -DCMAKE_AR="${CK_AR_PATH_FOR_CMAKE}" \
      -DCMAKE_RANLIB="${CK_RANLIB_PATH_FOR_CMAKE}" \
      -DCMAKE_LINKER="${CK_LD_PATH_FOR_CMAKE}" \
      -DCMAKE_SHARED_LINKER_FLAGS="${CK_OPENMP} ${CK_COMPILER_OWN_LIB_LOC}" \
      -DBUILD_python=${CAFFE_BUILD_PYTHON} \
      ${SPECIFIC_PYTHON_PATHS} \
      -DBUILD_docs=OFF \
      -DCPU_ONLY=ON \
      -DUSE_OPENMP:BOOL=${USE_OPENMP} \
      -DUSE_GREENTEA=OFF \
      -DUSE_LMDB=ON \
      -DUSE_LEVELDB=${USE_LEVELDB} \
      -DLEVELDB_ROOT=${CK_ENV_LIB_LEVELDB} \
      -DLevelDB_INCLUDE=${CK_ENV_LIB_LEVELDB_INCLUDE} \
      -DLevelDB_LIBRARY=${CK_ENV_LIB_LEVELDB_LIB}/${CK_ENV_LIB_LEVELDB_DYNAMIC_NAME} \
      -DUSE_HDF5=ON \
      -DBLAS=open \
      -DGFLAGS_INCLUDE_DIR="${CK_ENV_LIB_GFLAGS_INCLUDE}" \
      -DGLOG_INCLUDE_DIR="${CK_ENV_LIB_GLOG_INCLUDE}" \
      -DGFLAGS_LIBRARY="${CK_ENV_LIB_GFLAGS_LIB}/libgflags${CK_DLL_EXT}" \
      -DGLOG_LIBRARY="${CK_ENV_LIB_GLOG_LIB}/libglog${CK_DLL_EXT}" \
      -DBoost_ADDITIONAL_VERSIONS="1.62" \
      -DBOOST_ROOT=${CK_ENV_LIB_BOOST} \
      -DBOOST_INCLUDEDIR="${CK_ENV_LIB_BOOST_INCLUDE}" \
      -DBOOST_LIBRARYDIR="${CK_ENV_LIB_BOOST_LIB}" \
      -DBoost_INCLUDE_DIR="${CK_ENV_LIB_BOOST_INCLUDE}" \
      -DBoost_LIBRARY_DIR="${CK_ENV_LIB_BOOST_LIB}" \
      ${CK_ENV_COMPILER_PYTHON_FILE:+"-DPYTHON_EXECUTABLE=${CK_ENV_COMPILER_PYTHON_FILE}"} \
      ${CK_ENV_LIB_BOOST_PYTHON_LIBRARY:+"-DBoost_PYTHON_LIBRARY=${CK_ENV_LIB_BOOST_PYTHON_LIBRARY}"} \
      -DHDF5_DIR="${CK_ENV_LIB_HDF5}/share/cmake" \
      -DHDF5_ROOT_DIR="${CK_ENV_LIB_HDF5}/share/cmake" \
      -DHDF5_INCLUDE_DIRS="${CK_ENV_LIB_HDF5_INCLUDE}" \
      -DHDF5_LIBRARIES="${CK_ENV_LIB_HDF5_LIB}/libhdf5${CK_DLL_EXT}" \
      -DHDF5_HL_LIBRARIES="${CK_ENV_LIB_HDF5_LIB}/libhdf5_hl${CK_DLL_EXT}" \
      -DOpenBLAS_INCLUDE_DIR="${CK_ENV_LIB_OPENBLAS_INCLUDE}" \
      -DOpenBLAS_LIB="${CK_ENV_LIB_OPENBLAS_LIB}/libopenblas.a" \
      -DLMDB_INCLUDE_DIR="${CK_ENV_LIB_LMDB_INCLUDE}" \
      -DLMDB_LIBRARIES="${CK_ENV_LIB_LMDB_LIB}/liblmdb${CK_DLL_EXT}" \
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
