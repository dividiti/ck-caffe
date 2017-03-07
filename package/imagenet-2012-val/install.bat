@echo off

rem Installation script for the 2012 ImageNet Large Scale Visual Recognition
rem Challenge (ILSVRC'12) validation dataset.
rem
rem See CK LICENSE.txt for licensing details.
rem See CK COPYRIGHT.txt for copyright details.
rem
rem Developer(s):
rem - Anton Lokhmotov, anton@dividiti.com, 2016
rem - Grigori Fursin, Grigori.Fursin@cTuning.org, 2016

rem PACKAGE_DIR
rem INSTALL_DIR

set IMAGENET_VAL_TAR=%INSTALL_DIR%\ILSVRC2012_img_val.tar

rem #####################################################################
echo.
echo Downloading archive ...

wget --no-check-certificate -c "%IMAGENET_VAL_URL%" -O "%IMAGENET_VAL_TAR%"

if %errorlevel% neq 0 (
 echo.
 echo Error: Failed downloading archive ...
 goto err
)

rem #####################################################################

echo.
echo Unpacking %DOWNLOAD_NAME% ...

cd /D %INSTALL_DIR%

tar xvf %IMAGENET_VAL_TAR%

if EXIST "%IMAGENET_VAL_TAR%" (
  del /Q /S %IMAGENET_VAL_TAR%
)

rem #####################################################################
echo.
echo Successfully installed the ILSVRC'12 validation dataset ...

exit /b 0

:err
exit /b 1
