#
# CK Caffe build script.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s): Anton Lokhmotov, anton@dividiti.com
#
echo ""
echo "Building Caffe in ${CAFFE_BLD_DIR} ..."

mkdir -p ${CAFFE_BLD_DIR}
cd ${CAFFE_BLD_DIR}

make -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
if [ "${?}" != "0" ] ; then
  echo "Error: Building Caffe in ${CAFFE_BLD_DIR} failed!"
  exit 1
fi
