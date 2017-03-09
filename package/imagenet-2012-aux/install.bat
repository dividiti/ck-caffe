@echo off

rem  Installation script for the 2012 ImageNet Large Scale Visual Recognition
rem Challenge (ILSVRC'12) auxiliary dataset.
rem
rem See CK LICENSE.txt for licensing details.
rem See CK COPYRIGHT.txt for copyright details.
rem
rem Developer(s):
rem - Anton Lokhmotov, anton@dividiti.com, 2016
rem - Grigori Fursin, Grigori.Fursin@cTuning.org, 2016

rem PACKAGE_DIR
rem INSTALL_DIR

set FULL_PATH=%INSTALL_DIR%/%DOWNLOAD_FILE%
set FULL_URL=%DOWNLOAD_URL%/%DOWNLOAD_FILE%

rem #####################################################################
echo.
echo Downloading %DOWNLOAD_NAME% from %FULL_URL% ...

wget --no-check-certificate -c "%FULL_URL%" -O "%FULL_PATH%"

if %errorlevel% neq 0 (
 echo.
 echo Error: Failed downloading %DOWNLOAD_NAME% ...
 goto err
)

rem #####################################################################

echo.
echo Unpacking %DOWNLOAD_NAME% ...

cd /D %INSTALL_DIR%

if EXIST "%DOWNLOAD_FILE1%" (
  del /Q /S %PACKAGE_FILE1%
)

gzip -d %DOWNLOAD_FILE%

tar xvf %DOWNLOAD_FILE1%

if EXIST "%DOWNLOAD_FILE1%" (
  del /Q /S %PACKAGE_FILE1%
)

rem Delete weird MacOS X files.
del /Q /S %INSTALL_DIR%\._*

rem #####################################################################
echo.
echo Successfully installed the %DOWNLOAD_NAME% validation dataset ...

exit /b 0

:err
exit /b 1
