#! /bin/bash

# CK installation script for TensorFlow package from Makefiles
# http://cKnowledge.org/ai

CAFFE_SRC=${INSTALL_DIR}/src
cd ${CAFFE_SRC}

if [ "${CK_ENV_COMPILER_LLVM_BIN}" != "" ] ; then
  CK_FULL_CXX="${CK_ENV_COMPILER_LLVM_BIN}/${CK_CXX}"
  CK_FULL_AR="${CK_ENV_COMPILER_LLVM_BIN}/${CK_AR}"
  CK_FULL_LD="${CK_ENV_COMPILER_LLVM_BIN}/${CK_LD}"
elif [ "${CK_ENV_COMPILER_GCC_BIN}" != "" ] ; then
  CK_FULL_CXX="${CK_ENV_COMPILER_GCC_BIN}/${CK_CXX}"
  CK_FULL_AR="${CK_ENV_COMPILER_GCC_BIN}/${CK_AR}"
  CK_FULL_LD="${CK_ENV_COMPILER_GCC_BIN}/${CK_LD}"
else
  CK_FULL_CXX=${CK_CXX}
  CK_FULL_AR=${CK_AR}
  CK_FULL_LD=${CK_LD}
fi

CPU_ONLY=1
BLAS_INCLUDE=${CK_ENV_LIB_OPENBLAS_INCLUDE}
BLAS_LIB=${CK_ENV_LIB_OPENBLAS_LIB}

cp Makefile.config.example Makefile.config

make CUSTOM_CXX="${CK_FULL_CXX}" CPU_ONLY="${CPU_ONLY}" BLAS_INCLUDE="${BLAS_INCLUDE}" BLAS_LIB="${BLAS_LIB}" -j8

exit 0
#make py