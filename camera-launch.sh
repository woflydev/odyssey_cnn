gst-launch-1.0 nvarguscamerasrc num-buffers=200 sensor-id=0 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=30/1, format=NV12' ! omxh264enc ! qtmux ! filesink location=nvargus.test.mp4

nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=30/1, format=NV12' ! appsink