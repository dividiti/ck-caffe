@echo off

rem
rem Installation script for CK packages.
rem
rem See CK LICENSE.txt for licensing details.
rem See CK Copyright.txt for copyright details.
rem
rem Developer(s):
rem - Anton Lokhmotov, anton@dividiti.com, 2016
rem - Grigori Fursin, grigori@dividiti.com, 2016
rem

rem ORIGINAL_PACKAGE_DIR (path to original package even if scripts are used from some other package or script)
rem PACKAGE_DIR (path where scripts are reused)
rem INSTALL_DIR

set MODEL_PATH=%INSTALL_DIR%\%MODEL_FILE%

echo.
echo Copying net topology files to %INSTALL_DIR% ...

copy %ORIGINAL_PACKAGE_DIR%\* %INSTALL_DIR%

echo.
echo Downloading the weights from %MODEL_URL% ...
del /S /Q %MODEL_PATH%
wget -c %MODEL_URL% -O %MODEL_PATH% --no-check-certificate

exit /b 0
