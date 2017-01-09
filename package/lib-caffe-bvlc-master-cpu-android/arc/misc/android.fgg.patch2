diff -ruN src/src/caffe/CMakeLists.txt src.new/src/caffe/CMakeLists.txt
--- src/src/caffe/CMakeLists.txt	2016-12-29 02:45:52.367053285 +0100
+++ src.new/src/caffe/CMakeLists.txt	2016-12-29 02:46:11.307052946 +0100
@@ -25,6 +25,8 @@
     SOVERSION ${CAFFE_TARGET_SOVERSION}
     )
 
+set(CMAKE_CXX_CREATE_SHARED_LIBRARY "${CMAKE_CXX_CREATE_SHARED_LIBRARY} ${CMAKE_EXE_LINKER_LIBS}")
+
 # ---[ Tests
  add_subdirectory(test)
 
