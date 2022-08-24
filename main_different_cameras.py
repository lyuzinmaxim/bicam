from tools import run_ccoeff_normed
from camera_tools import *
import cv2

TEMPLATE_SIZE = (100, 100)
COEF = 2.66 #f'_right/f'_left

D = dict.fromkeys(['x', 'y'])
D['x'] = 500
D['y'] = 500


def coords_mouse_disp(event, x, y, flags, image):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        D['x'] = x
        D['y'] = y


if __name__ == "__main__":

    window_title = "Dual CSI Cameras"

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
        prev_tick = cv2.getTickCount()

        try:
            while True:
                _, left_image = left_camera.read()
                _, right_image = right_camera.read()

                new = cv2.getTickCount()

                cv2.setMouseCallback(window_title, coords_mouse_disp, left_image)

                click_x, click_y = D['x'], D['y']


                ROI = left_image[click_y - TEMPLATE_SIZE[1]//2:click_y + TEMPLATE_SIZE[1]//2,
                                 click_x - TEMPLATE_SIZE[0]//2:click_x + TEMPLATE_SIZE[0]//2, :]

                #r1, r2 = run_ccoeff_normed(right_image, ROI, verbose=False)
                r1, r2 = run_ccoeff_normed(right_image, cv2.resize(ROI, (int(COEF*TEMPLATE_SIZE[0]), int(COEF*TEMPLATE_SIZE[1]))), verbose=False)
                cv2.rectangle(right_image, r1, r2, 255, 2)

                l1, l2 = (D['x'] - TEMPLATE_SIZE[0]//2, D['y'] - TEMPLATE_SIZE[0]//2),\
                         (D['x'] + TEMPLATE_SIZE[1]//2, D['y'] + TEMPLATE_SIZE[1]//2)
                cv2.rectangle(left_image, l1, l2, (240, 240, 240), 2)

                right_center = (r1[0] + COEF*TEMPLATE_SIZE[0]//2, r1[1] + COEF*TEMPLATE_SIZE[1]//2)
                left_center = (D['x'], D['y'])
                # disparity = abs(right_center[0] - left_center[0])


                x_l_, y_l_ = click_x - 960/2, 540/2 - click_y
                x_r_, y_r_ = right_center[0] - 960/2, 540/2 - right_center[1]

                #print(right_center, x_r_, x_l_)
                #disparity = abs(r1[0] - l1[0])
                disparity = abs(x_r_/ COEF - x_l_)
                # distance = 163-(-2.6359 + 15651.6209/disparity)
                # distance = (-5.4576 + 14422.4746 / (1e-10 + disparity))
                # distance = (-2.6359 + 15651.6209 / (1e-10 + disparity))
                # distance = (-18.990 + 15723.5 / disparity)
                distance = 15682.42/(disparity+18.46)
                print("#########################\n{} => {} sm".format(disparity, distance))

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
