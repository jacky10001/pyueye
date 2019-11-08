
""" 
uEye CCD main program

@fcn_header:
    def process_image(self, image_data, enable):
        --> custom function (can do save or some process)
    
    def main():

@refer: pyueye_example, source code from 
    https://en.ids-imaging.com/techtipps-detail/en_techtip-embedded-vision-kit.html

    Copyright (c) 2017 by IDS Imaging Development Systems GmbH.
    All rights reserved.

@create data: 2019.11.04
@update data: 2019.11.05
@author: Yang-Jie Gao
@e-mail: 60777001h@ntnu.edu.tw
"""

from ueye_camera import Camera
from ueye_utils import FrameThread
from ueye_gui import PyuEyeQtApp, PyuEyeQtView
from PyQt4 import QtGui

from pyueye import ueye

import glob
import cv2
import numpy as np
from numpy.fft import fft2, fftshift

import os
os.makedirs('cap', exist_ok='True')

## global variable ##
global save_count, loop_count, keep_save

try:
    tmp = sorted(glob.glob('cap/*.bmp'))[-1]
    tmp = tmp[tmp.rfind('\\')+1:-4]
    print('Start number: ', tmp)
except:
    tmp = '00000'
    print('Start number: ', tmp)

save_count = int(tmp) + 1
loop_count = 0
keep_save = False


def process_image(self, image_data, enable):
    global save_count, loop_count, keep_save

    # reshape the image data as 1dimensional array
    image = image_data.as_1d_image()
    
    # save gray image
    if enable == 'STOP':
        keep_save = 'STOP'
    elif enable == 'SAVE':
        keep_save = 'STOP'
        print('loop count:',loop_count,' save count:',save_count)
        cv2.imwrite('cap/%05d.bmp'%save_count, image)
        save_count += 1
    elif enable == 'AUTO':
        keep_save = 'AUTO'
        if loop_count%10==0:
            print('loop count:',loop_count,' save count:',save_count)
            cv2.imwrite('cap/%05d.bmp'%save_count, image)
            save_count += 1
    
    # make a rgb image for show. (gray -> rgb, because QPainter can't use Format_Indexed8)
    image = image.reshape(1024,1280,1)
    image = np.concatenate([image,image,image], axis=-1)
    
    loop_count += 1
    # show the image with Qt
    return QtGui.QImage(image, 1280, 1024, QtGui.QImage.Format_RGB888), keep_save

# def RecFrame(self, image_data):

def main():

    # we need a QApplication, that runs our QT Gui Framework    
    app = PyuEyeQtApp()

    # a basic qt window
    view = PyuEyeQtView()
    view.show()
    view.user_callback = process_image

    # camera class to simplify uEye API access
    cam = Camera()
    cam.init()
    cam.set_colormode(ueye.IS_CM_SENSOR_RAW8)
    cam.set_aoi(0,0, 1280, 1024)
    # cam.set_full_auto()
    cam.set_FrameRate(15)
    cam.set_Exposure(66)
    cam.alloc()
    cam.capture_video()

    # a thread that waits for new images and processes all connected views
    thread = FrameThread(cam, view)
    thread.start()

    # cleanup
    app.exit_connect(thread.stop)
    app.exec_()

    thread.stop()
    thread.join()

    cam.stop_video()
    cam.exit()

if __name__ == "__main__":
    main()

