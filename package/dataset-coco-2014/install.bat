
echo Downloading COCO 2014 validation dataset
wget --no-check-certificate --continue "%IMAGE_URL%/%VAL_IMAGE_ARCHIVE%" -O "%VAL_IMAGE_ARCHIVE%"
python -m zipfile -e "%VAL_IMAGE_ARCHIVE%" .

echo Downloading COCO 2014 Train/Val object instances
wget --no-check-certificate --continue "%ANNOTATION_URL%/%TRAINVAL_OBJ_INSTANCES_ARCHIVE%" -O "%TRAINVAL_OBJ_INSTANCES_ARCHIVE%"
python -m zipfile -e  "%TRAINVAL_OBJ_INSTANCES_ARCHIVE%" .

exit /b 0
