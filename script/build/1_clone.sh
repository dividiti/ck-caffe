#
# CK Caffe clone script.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s): Anton Lokhmotov, anton@dividiti.com
#
echo ""
echo "Cloning Caffe from '${CAFFE_URL}' ..."

rm -rf ${CAFFE_SRC_DIR}
git clone ${CAFFE_URL} --no-checkout ${CAFFE_SRC_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: Cloning Caffe from '${CAFFE_URL}' failed!"
  exit 1
fi
