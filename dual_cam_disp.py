import numpy as np
import cv2
from sklearn.preprocessing import normalize
import os
import cv2
import threading
import numpy as np

DISP = 1

def coords_mouse_disp(event,x,y,flags,disp):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        #print x,y,disp[y,x],filteredImg[y,x]
        average=0
        for u in range (-1,2):
            for v in range (-1,2):
                average += disp[y+u,x+v]
        average=average/9
	
        print(average.shape)
        #Distance= -593.97*average**(3) + 1506.8*average**(2) - 1373.1*average + 522.06
        #Distance= np.around(Distance*0.01,decimals=2)
        Distance= np.around((145*6)/(average+0.00001)*0.001,decimals=2)
        print('Distance: '+ str(Distance)+' m')



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
    
    kernel= np.ones((3,3),np.uint8)

    window_size = 3
    min_disp = 2
    num_disp = 130-min_disp
    stereo = cv2.StereoSGBM_create(minDisparity = min_disp,
        numDisparities = num_disp,
        blockSize = window_size,
        uniquenessRatio = 10,
        speckleWindowSize = 100,
        speckleRange = 32,
        disp12MaxDiff = 5,
        P1 = 8*3*window_size**2,
        P2 = 32*3*window_size**2)
        
    # Used for the filtered image
    stereoR=cv2.ximgproc.createRightMatcher(stereo) # Create another stereo for right this time

    # WLS FILTER Parameters
    lmbda = 80000
    sigma = 1.8
    visual_multiplier = 1.0
     
    wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=stereo)
    wls_filter.setLambda(lmbda)
    wls_filter.setSigmaColor(sigma)
        
    left_camera = CSI_Camera()
    left_camera.open(
        gstreamer_pipeline(
            sensor_id=0,
            capture_width=500,
            capture_height=500,
            flip_method=2,
            display_width=500,
            display_height=500,
        )
    )
    left_camera.start()

    right_camera = CSI_Camera()
    right_camera.open(
        gstreamer_pipeline(
            sensor_id=1,
            capture_width=500,
            capture_height=500,
            flip_method=2,
            display_width=500,
            display_height=500,
        )
    )
    right_camera.start()

    if left_camera.video_capture.isOpened() and right_camera.video_capture.isOpened():

        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

        try:
            while True:
                _, left_image = left_camera.read()
                _, right_image = right_camera.read()
                #DISPARITY
                grayR= cv2.cvtColor(right_image,cv2.COLOR_BGR2GRAY)
                grayL= cv2.cvtColor(left_image,cv2.COLOR_BGR2GRAY)
                disp= stereo.compute(grayL,grayR)
                dispL= disp
                dispR= stereoR.compute(grayR,grayL)
                dispL= np.int16(dispL)
                dispR= np.int16(dispR)
                filteredImg= wls_filter.filter(dispL,grayL,None,dispR)
                filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX);
                filteredImg = np.uint8(filteredImg)
                disp= ((disp.astype(np.float32)/ 16)-min_disp)/num_disp
                
                closing= cv2.morphologyEx(disp,cv2.MORPH_CLOSE, kernel)
                dispc= (closing-closing.min())*255
                dispC= dispc.astype(np.uint8)                                   # Convert the type of the matrix from float32 to uint8, this way you can show the results with the function cv2.imshow()
                disp_Color= cv2.applyColorMap(dispC,cv2.COLORMAP_OCEAN)         # Change the Color of the Picture into an Ocean Color_Map
                filt_Color= cv2.applyColorMap(filteredImg,cv2.COLORMAP_OCEAN)
                
                if DISP:
                    cv2.imshow('Filtered Color Depth',filt_Color)
                    cv2.setMouseCallback("Filtered Color Depth",coords_mouse_disp,disp)

                
                
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
