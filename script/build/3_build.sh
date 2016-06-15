#
# CK Caffe build script.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s): Anton Lokhmotov, anton@dividiti.com
#
echo ""
echo "Building the '${CAFFE_BRANCH}' branch of Caffe ..."

mkdir -p ${CAFFE_BUILD_DIR}
cd ${CAFFE_BUILD_DIR}

make -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
if [ "${?}" != "0" ] ; then
  echo "Error: Building the '${CAFFE_BRANCH}' branch of Caffe failed!"
  exit 1
fi
