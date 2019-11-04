#!/usr/bin/env python

#------------------------------------------------------------------------------
#                 PyuEye example - main modul
#
# Copyright (c) 2017 by IDS Imaging Development Systems GmbH.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#------------------------------------------------------------------------------

from ueye_camera import Camera
from ueye_utils import FrameThread
from ueye_gui import PyuEyeQtApp, PyuEyeQtView
from PyQt4 import QtGui

from pyueye import ueye

import cv2
import numpy as np

## global variable ##
global save_count
global loop_count
save_count = 0
loop_count = 0


def process_image(self, image_data, enable):
    global save_count
    global loop_count

    # reshape the image data as 1dimensional array
    image = image_data.as_1d_image()
    
    # save gray image
    if enable and loop_count%10==0:
        print('loop count:',loop_count,' save count:',save_count)
        cv2.imwrite('cap/%d.bmp'%save_count, image)
        save_count += 1
    
    # make a rgb image for show. (gray -> rgb, because QPainter can't use Format_Indexed8)
    image = image.reshape(1024,1280,1)
    image = np.concatenate([image,image,image], axis=-1)
    
    loop_count += 1
    # show the image with Qt
    return QtGui.QImage(image, 1280, 1024, QtGui.QImage.Format_RGB888)

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

