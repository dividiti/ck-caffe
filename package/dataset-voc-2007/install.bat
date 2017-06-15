

mkdir "%TRAIN_DIR%"
cd "%INSTALL_DIR%\%TRAIN_DIR%"

echo Downloading VOC 2007 training dataset from %VOC_TRAIN_URL%
wget --no-check-certificate --continue "%VOC_TRAIN_URL%" -O "%VOC_TRAIN_ARCHIVE%"
tar -xvf "%VOC_TRAIN_ARCHIVE%"

cd "%INSTALL_DIR%"
mkdir "%TEST_DIR%"
cd "%INSTALL_DIR%\%TEST_DIR%"

echo Downloading VOC 2007 test dataset from %VOC_TEST_URL%
wget --no-check-certificate --continue "%VOC_TEST_URL%" -O "%VOC_TEST_ARCHIVE%"
tar -xvf "%VOC_TEST_ARCHIVE%"

exit /b 0

