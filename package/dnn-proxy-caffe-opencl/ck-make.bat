@echo off

rem
rem Make script for CK libraries
rem (depends on configured/installed compilers via CK)
rem
rem See CK LICENSE.txt for licensing details.
rem See CK Copyright.txt for copyright details.
rem
rem Developer(s): Grigori Fursin, 2015
rem

set CK_SOURCE_FILES=dnn_proxy.cpp
set CK_OBJ_FILES=dnn_proxy%CK_OBJ_EXT%
set CK_INCLUDE_FILE=dnn_proxy.h

set LIB_NAME=libdnnproxy

set CK_COMPILER_FLAGS_MISC=%CK_FLAG_PREFIX_INCLUDE%. %CK_COMPILER_FLAGS_MISC%




echo.
echo Building static library ...
echo.

set CK_TARGET_FILE=%LIB_NAME%%CK_LIB_EXT%
set CK_TARGET_FILE_S=%CK_TARGET_FILE%

set CK_CC_FLAGS=%CK_COMPILER_FLAGS_OBLIGATORY% %CK_COMPILER_FLAGS_MISC% %CK_COMPILER_FLAGS_CC_OPTS% %CK_COMPILER_FLAGS_ARCH% %CK_COMPILER_FLAGS_PAR%

echo Executing %CK_CC% %CK_OPT_SPEED% %CK_FLAGS_STATIC_LIB% %CK_FLAGS_CREATE_OBJ% %CK_CC_FLAGS% %CK_SOURCE_FILES% %CK_LD_FLAGS_MISC% %CK_LD_FLAGS_EXTRA%
%CK_CC% %CK_OPT_SPEED% %CK_FLAGS_STATIC_LIB% %CK_FLAGS_CREATE_OBJ% %CK_CC_FLAGS% %CK_SOURCE_FILES% %CK_LD_FLAGS_MISC% %CK_LD_FLAGS_EXTRA%
if %errorlevel% neq 0 (
 echo.
 echo Building failed!
 goto err
)

echo Executing %CK_LB% %CK_LB_OUTPUT%%CK_TARGET_FILE% %CK_OBJ_FILES%
%CK_LB% %CK_LB_OUTPUT%%CK_TARGET_FILE% %CK_OBJ_FILES%
if %errorlevel% neq 0 (
 echo.
 echo Building failed!
 goto err
)

echo.
echo Installing ...
echo.

mkdir %INSTALL_DIR%\lib
copy /B %CK_TARGET_FILE_S% %INSTALL_DIR%\lib



rem goto skip



echo.
echo Building dynamic library ...
echo.

set CK_TARGET_FILE=%LIB_NAME%%CK_DLL_EXT%
set CK_TARGET_FILE_D=%CK_TARGET_FILE%

set CK_CC_FLAGS=%CK_COMPILER_FLAGS_OBLIGATORY% %CK_COMPILER_FLAGS_MISC% %CK_COMPILER_FLAGS_CC_OPTS% %CK_COMPILER_FLAGS_ARCH% %CK_COMPILER_FLAGS_PAR%

echo Executing %CK_CC% %CK_OPT_SPEED% %CK_FLAGS_DLL% %CK_CC_FLAGS% %CK_SOURCE_FILES% %CK_FLAGS_OUTPUT%%CK_TARGET_FILE% %CK_FLAGS_DLL_EXTRA% %CK_LD_FLAGS_MISC% %CK_LD_FLAGS_EXTRA%
%CK_CC% %CK_OPT_SPEED% %CK_FLAGS_DLL% %CK_CC_FLAGS% %CK_SOURCE_FILES% %CK_FLAGS_OUTPUT%%CK_TARGET_FILE% %CK_FLAGS_DLL_EXTRA% %CK_LD_FLAGS_MISC% %CK_LD_FLAGS_EXTRA%
if %errorlevel% neq 0 (
 echo.
 echo Building failed!
 goto err
)

echo.
echo Installing ...
echo.

mkdir %INSTALL_DIR%\bin
copy /B %CK_TARGET_FILE_S% %INSTALL_DIR%\bin
copy /B %CK_TARGET_FILE_D% %INSTALL_DIR%\bin
copy /B %CK_TARGET_FILE_D% %INSTALL_DIR%\lib





:skip

mkdir %INSTALL_DIR%\include
copy /B %CK_INCLUDE_FILE% %INSTALL_DIR%\include

exit /b 0

:err
set /p x=Press any key to continue!
exit /b 1
