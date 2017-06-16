
mkdir "%TRAIN_DIR%"
cd "%INSTALL_DIR%\%TRAIN_DIR%"

echo Downloading VOC 2012 training dataset from %VOC_TRAIN_URL%
wget --no-check-certificate --continue "%VOC_TRAIN_URL%" -O "%VOC_TRAIN_ARCHIVE%"
tar -xvf "%VOC_TRAIN_ARCHIVE%"

exit /b 0
