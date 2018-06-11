@echo off

rem
rem Installation script for CK packages.
rem
rem See CK LICENSE.txt for licensing details.
rem See CK Copyright.txt for copyright details.
rem
rem Developer(s): Grigori Fursin, 2016-2017
rem

rem PACKAGE_DIR
rem INSTALL_DIR

if "%CAFFE_BUILD_PYTHON%" == "ON" (
  echo.
  echo You are compiling Caffe with Python support!
  echo To use it you need to set up CK env as following ^(after installation^)^:
  echo.
  echo $ ck virtual env --tags=lib,caffe
  echo $ ipython
  echo.
  set /p id="Press enter to continue"
)

echo **************************************************************
echo Preparing vars for Caffe ...

set CK_CXX_FLAGS_FOR_CMAKE=
set CK_CXX_FLAGS_ANDROID_TYPICAL=

set CUDNN_ROOT="%CK_ENV_LIB_CUDNN%"

set CK_CMAKE_EXTRA=%CK_CMAKE_EXTRA% -DCPU_ONLY:BOOL=%CPU_ONLY% ^
 -DBLAS=%BLAS_TYPE% ^
 -DUSE_LMDB=%USE_LMDB% ^
 -DUSE_LEVELDB=OFF ^
 -DUSE_CUDNN=ON ^
 -DUSE_LIBDNN=%USE_LIBDNN% ^
 -DUSE_PREBUILT_DEPENDENCIES=OFF ^
 -DBUILD_SHARED_LIBS:BOOL=%CMAKE_BUILD_SHARED_LIBS% ^
 -DBUILD_python=%CAFFE_BUILD_PYTHON% ^
 -DBUILD_matlab:BOOL=%BUILD_MATLAB% ^
 -DGFLAGS_INCLUDE_DIR="%CK_ENV_LIB_GFLAGS_INCLUDE%" ^
 -DGFLAGS_LIBRARY="%CK_ENV_LIB_GFLAGS_LIB%\gflags.lib" ^
 -DCUDA_TOOLKIT_ROOT_DIR="%CK_ENV_COMPILER_CUDA_WIN%" ^
 -DCUDNN_ROOT="%CK_ENV_LIB_CUDNN_WIN%" ^
 -DCUDA_ARCH_NAME="%CK_CUDA_ARCH_NAME%" ^
 -DCUDA_NVCC_FLAGS="-D_FORCE_INLINES -Wno-deprecated-gpu-targets" ^
 -DGLOG_INCLUDE_DIR="%CK_ENV_LIB_GLOG_INCLUDE%" ^
 -DGLOG_LIBRARY="%CK_ENV_LIB_GLOG_LIB%\glog.lib" ^
 -DLMDB_INCLUDE_DIR="%CK_ENV_LIB_LMDB_INCLUDE%" ^
 -DLMDB_LIBRARIES="%CK_ENV_LIB_LMDB_LIB%\lmdb.lib" ^
 -DCMAKE_BUILD_TYPE:STRING=%CMAKE_CONFIG% ^
 -DPROTOBUF_DIR="%CK_ENV_LIB_PROTOBUF_HOST%\cmake" ^
 -DHDF5_ROOT_DIR="%CK_ENV_LIB_HDF5%\cmake" ^
 -DHDF5_INCLUDE_DIRS="%CK_ENV_LIB_HDF5_INCLUDE%" ^
 -DHDF5_LIBRARIES="%CK_ENV_LIB_HDF5_LIB%\hdf5.lib" ^
 -DHDF5_HL_LIBRARIES="%CK_ENV_LIB_HDF5_LIB%\hdf5_hl.lib" ^
 -DOpenBLAS_INCLUDE_DIR="%CK_ENV_LIB_OPENBLAS_INCLUDE%" ^
 -DOpenBLAS_LIB="%CK_ENV_LIB_OPENBLAS_LIB%\%CK_ENV_LIB_OPENBLAS_STATIC_NAME%" ^
 -DBoost_ADDITIONAL_VERSIONS="1.62;1.64;1.65;1.66" ^
 -DBoost_NO_SYSTEM_PATHS=ON ^
 -DBOOST_ROOT=%CK_ENV_LIB_BOOST% ^
 -DBOOST_LIBRARYDIR="%CK_ENV_LIB_BOOST_LIB%" ^
 -DBoost_LIBRARY_DIR="%CK_ENV_LIB_BOOST_LIB%" ^
 %CK_CMAKE_EXTRA_BOOST_PYTHON% ^
 -DOpenCV_DIR="%CK_ENV_LIB_OPENCV%" ^
 -DOpenCV_LIB_PATH="%CK_ENV_LIB_OPENCV_LIB%"

rem  -DHDF5_DIR="%CK_ENV_LIB_HDF5%\cmake" ^
rem -DCUDNN_INCLUDE="%CK_ENV_LIB_CUDNN_INCLUDE%" ^
rem -DCUDNN_LIBRARY="%CK_ENV_LIB_CUDNN_LIB%\%CK_ENV_LIB_CUDNN_STATIC_NAME%" ^
rem -DBOOST_INCLUDEDIR="%CK_ENV_LIB_BOOST_INCLUDE%" ^
rem -DBoost_INCLUDE_DIR="%CK_ENV_LIB_BOOST_INCLUDE%" ^

exit /b 0
