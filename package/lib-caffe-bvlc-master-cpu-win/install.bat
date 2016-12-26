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

exit /b 0

cd %INSTALL_DIR%

echo **************************************************************
if "%VisualStudioVersion%" == "14.0" (
   set CMAKE_GENERATOR=Visual Studio 14 2015 Win64
) else (
   set CMAKE_GENERATOR=Visual Studio 12 2013 Win64
)

echo "CMAKE_GENERATOR=%CMAKE_GENERATOR%"

echo **************************************************************
echo Downloading extra libs ...
rem For now use fixed download - then should compile via CK
set EXTRA_URL=https://github.com/willyd/caffe-builder/releases/download/v1.0.1/libraries_v140_x64_py35_1.0.1.tar.bz2

rmdir /s /q libraries
rmdir libraries
mkdir libraries
cd libraries
wget --no-check-certificate %EXTRA_URL% -O libraries_v140_x64_py35_1.0.1.tar.bz2

bzip2 -d libraries_v140_x64_py35_1.0.1.tar.bz2
tar xvf libraries_v140_x64_py35_1.0.1.tar
del /S /Q libraries_v140_x64_py35_1.0.1.tar

echo **************************************************************
echo Obtaining latest Caffe from GitHub ...
echo.

cd %INSTALL_DIR%

rmdir /s /q src
rmdir src

git clone %CAFFE_URL% src

cd src
git checkout %CAFFE_BRANCH%

echo **************************************************************
echo Configuring Caffe for Windows

cd %INSTALL_DIR%

rmdir /s /q build
rmdir build
mkdir build
cd build

cmake -G"%CMAKE_GENERATOR%" ^
      -DBLAS=Open ^
      -DCMAKE_BUILD_TYPE:STRING=%CMAKE_CONFIG% ^
      -DBUILD_SHARED_LIBS:BOOL=%CMAKE_BUILD_SHARED_LIBS% ^
      -DBUILD_python:BOOL=%BUILD_PYTHON% ^
      -DBUILD_python_layer:BOOL=%BUILD_PYTHON_LAYER% ^
      -DBUILD_matlab:BOOL=%BUILD_MATLAB% ^
      -DCPU_ONLY:BOOL=%CPU_ONLY% ^
      -C "%INSTALL_DIR%\libraries\libraries\caffe-builder-config.cmake" ^
      "%INSTALL_DIR%\src"

if %errorlevel% neq 0 (
 echo.
 echo Problem building CK package!
 goto err
)

echo **************************************************************
echo.
echo Building using Visual Studio ...

cmake --build . --config %CMAKE_CONFIG%
if %errorlevel% neq 0 (
 echo.
 echo Problem building CK package!
 goto err
)

exit /b 0

:err
exit /b 1
