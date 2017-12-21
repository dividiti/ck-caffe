#!/bin/bash
echo copy files from ${ORIGINAL_PACKAGE_DIR}/patch.${CK_TARGET_OS_ID}/  to ${INSTALL_DIR} 
cp ${ORIGINAL_PACKAGE_DIR}/patch.${CK_TARGET_OS_ID}/* ${INSTALL_DIR}

