#
# CK Caffe checkout script.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s): Anton Lokhmotov, anton@dividiti.com
#
echo ""
echo "Checking out the '${CAFFE_BRANCH}' branch of Caffe ..."

cd ${CAFFE_SRC_DIR}
git checkout ${CAFFE_BRANCH}
if [ "${?}" != "0" ] ; then
  echo "Error: Checking out the '${CAFFE_BRANCH}' branch of Caffe failed!"
  exit 1
fi
