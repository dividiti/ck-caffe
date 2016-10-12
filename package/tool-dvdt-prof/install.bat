@echo off

rem TODO: This Windows installation script should be updated with changes
rem similar to the Linux one. (Anton Lokhmotov, 09-Sep-2016.)

rem
rem Installation script for dividiti's OpenCL profiler.
rem
rem See CK LICENSE.txt for licensing details.
rem See CK COPYRIGHT.txt for copyright details.
rem
rem Developer(s): Grigori Fursin, 2015
rem

rem PACKAGE_DIR
rem INSTALL_DIR

set LIB_NAME=plugin-opencl-dvdt-profiler

echo.
echo Obtaining latest OpenCL dividiti profiler from Bitbucket ...
echo.

cd %INSTALL_DIR%

rem git clone https://bitbucket.org/dividiti/prof src

cd src
rem git pull

cmake %INSTALL_DIR%\src
rem  -DWALLCLOCK=timeofday
rem CC=%CK_CC% INCLUDES="%CK_ENV_LIB_OPENCL_INCLUDE%"

if %errorlevel% neq 0 (
 echo.
 echo Problem building CK package!
 goto err
)

msbuild.exe Prof.sln /m:1 /p:Configuration=Release /p:Platform=Win32

if %errorlevel% neq 0 (
 echo.
 echo Problem building CK package!
 goto err
)

exit /b 0

:err
exit /b 1
