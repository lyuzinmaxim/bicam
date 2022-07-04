# bicam



install dependencies

<details>
  <summary>Click to expand!</summary>
  
  Install gstreamer libs
  ```
  sudo apt install \
  libssl1.1 \
  libgstreamer1.0-0 \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav \
  libgstrtspserver-1.0-0
  ```

  OpenCV compilation command:
  ```
  mkdir build
  cd build
  cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D INSTALL_PYTHON_EXAMPLES=OFF \
  -D BUILD_EXAMPLES=OFF \
  -D BUILD_SHARED_LIBS=OFF \
  -D INSTALL_C_EXAMPLES=OFF \
  -D PYTHON_EXECUTABLE=/usr/bin/python3 \
  -D BUILD_opencv_python2=OFF \
  -D CMAKE_INSTALL_PREFIX=/usr \
  -D PYTHON3_EXECUTABLE=/usr/bin/python3 \
  -D PYTHON3_INCLUDE_DIR=/usr/include/python3.8 \
  -D PYTHON3_PACKAGES_PATH=/usr/lib/python3/dist-packages \
  -D CUDAARITHM=OFF \
  -D BUILD_opencv_cudabgsegm=OFF \
  -D CUDAFILTERS=OFF \
  -D CUDAIMGPROC=OFF \
  -D CUDAFEATURES2D=OFF \
  -D CUDALEGACY=OFF \
  -D CUDAOBJDETECT=OFF \
  -D CUDAOPTFLOW=OFF \
  -D CUDACODEC=OFF \
  -D BUILD_OPENCV_DNN=OFF \
  -D OPENCV_EXTRA_MODULES_PATH=/home/maxim/experiment/opencv_contrib/modules \
  -D BUILD_DNN_OPENCL=OFF \
  -D BUILD_OPENCV_XIMGPROC=ON \
  -D WITH_GSTREAMER=ON ..
  ```
    ## Heading

</details>

# Usage
