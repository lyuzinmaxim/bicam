import cv2
import threading
import numpy as np
from math import sqrt
from tools import run_all_methods, run_sqdiff, run_ccoeff_normed, draw_blue_circle

TEMPLATE_SIZE = (50,50)
D = dict.fromkeys(['x', 'y'])
D['x'] = 500
D['y'] = 500


def coords_mouse_disp(event,x,y,flags,image):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        #cv2.circle(image, (100,100), 5, (255, 0, 0), 2)
        #cv2.imshow("",image)
        #cv2.waitKey(30)
        D['x'] = x 
        D['y'] = y 

       # print('Distance',x,y,image.shape)
	
class CSI_Camera:

    def __init__(self):
        # Initialize instance variables
        # OpenCV video capture element
        self.video_capture = None
        # The last captured image from the camera
        self.frame = None
        self.grabbed = False
        # The thread where the video capture runs
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

    def open(self, gstreamer_pipeline_string):
        try:
            self.video_capture = cv2.VideoCapture(
                gstreamer_pipeline_string, cv2.CAP_GSTREAMER
            )
            # Grab the first frame to start the video capturing
            self.grabbed, self.frame = self.video_capture.read()

        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("Pipeline: " + gstreamer_pipeline_string)


    def start(self):
        if self.running:
            print('Video capturing is already running')
            return None
        # create a thread to read the camera image
        if self.video_capture != None:
            self.running = True
            self.read_thread = threading.Thread(target=self.updateCamera)
            self.read_thread.start()
        return self

    def stop(self):
        self.running = False
        # Kill the thread
        self.read_thread.join()
        self.read_thread = None

    def updateCamera(self):
        # This is the thread to read images from the camera
        while self.running:
            try:
                grabbed, frame = self.video_capture.read()
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame
            except RuntimeError:
                print("Could not read image from camera")
        # FIX ME - stop and cleanup thread
        # Something bad happened

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def release(self):
        if self.video_capture != None:
            self.video_capture.release()
            self.video_capture = None
        # Now kill the thread
        if self.read_thread != None:
            self.read_thread.join()


""" 
gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
Flip the image by setting the flip_method (most common values: 0 and 2)
display_width and display_height determine the size of each camera pane in the window on the screen
Default 1920x1080
"""


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def run_cameras():
    window_title = "Dual CSI Cameras"

    #ROI = cv2.imread('/home/maxim/dual_cameras/experiment/left.jpg')[20:200, 620:770, :] 
    #ROI = cv2.imread('/home/maxim/dual_cameras/experiment/left1.jpg')[208:244, 548:586, :] 
    #ROI = cv2.imread('/home/maxim/dual_cameras/experiment/left1.jpg')[207:250, 580:617, :] 

    left_camera = CSI_Camera()
    left_camera.open(
        gstreamer_pipeline(
            sensor_id=0,
            capture_width=1920,
            capture_height=1080,
            flip_method=2,
            display_width=960,
            display_height=540,
        )
    )
    left_camera.start()

    right_camera = CSI_Camera()
    right_camera.open(
        gstreamer_pipeline(
            sensor_id=1,
            capture_width=1920,
            capture_height=1080,
            flip_method=2,
            display_width=960,
            display_height=540,
        )
    )
    right_camera.start()

    if left_camera.video_capture.isOpened() and right_camera.video_capture.isOpened():

        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

        try:
            while True:
                _, left_image = left_camera.read()
                _, right_image = right_camera.read()

                cv2.setMouseCallback(window_title,coords_mouse_disp,left_image)
                ROI = left_image[D['y']-50:D['y']+50,D['x']-50:D['x']+50,:]
   
                r1, r2 = run_ccoeff_normed(right_image, ROI, verbose=False)
   
                cv2.rectangle(right_image, r1, r2, 255, 2)

                l1, l2 = (D['x']-50,D['y']-50),(D['x']+50,D['y']+50) 
                cv2.rectangle(left_image, l1, l2, (240,240,240), 2)
		
                right_center = (r1[0] + 50, r1[1] + 50 )
                left_center = (D['x'], D['y'])
                #disparity = abs(right_center[0] - left_center[0])
                disparity = abs(r1[0] - l1[0])
                #distance = 163-(-2.6359 + 15651.6209/disparity)
                distance = (-2.6359 + 15651.6209/disparity)
                print("#########################\n{} => {}".format(disparity,distance))

                # Use numpy to place images next to each other
                camera_images = np.hstack((left_image, right_image)) 
                # Check to see if the user closed the window
                # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(window_title, camera_images)
                   
                else:
                    break

                # This also acts as

                
                keyCode = cv2.waitKey(30) & 0xFF
                # Stop the program on the ESC key
                if keyCode == 27:
                    break
        finally:

            left_camera.stop()
            left_camera.release()
            right_camera.stop()
            right_camera.release()
        cv2.destroyAllWindows()
    else:
        print("Error: Unable to open both cameras")
        left_camera.stop()
        left_camera.release()
        right_camera.stop()
        right_camera.release()



if __name__ == "__main__":
    run_cameras()