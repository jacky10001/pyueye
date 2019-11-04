
""" 
uEye CCD GUI control with PyQt

@fcn_header:
    def get_qt_format(ueye_color_format):
    class PyuEyeQtView(QtGui.QWidget):
    class PyuEyeQtApp:

@refer: pyueye_example, source code from 
    https://en.ids-imaging.com/techtipps-detail/en_techtip-embedded-vision-kit.html

@create data: 2019.11.04
@update data: 2019.11.05
@author: Yang-Jie Gao
@e-mail: 60777001h@ntnu.edu.tw
"""

from PyQt4 import QtCore
from PyQt4 import QtGui
#from PyQt5.QtWidgets import QGraphicsScene, QApplication
#from PyQt5.QtWidgets import QGraphicsView
#from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSlider, QWidget

from pyueye import ueye


def get_qt_format(ueye_color_format):
    return { ueye.IS_CM_SENSOR_RAW8: QtGui.QImage.Format_Mono,
             ueye.IS_CM_MONO8: QtGui.QImage.Format_Mono,
             ueye.IS_CM_RGB8_PACKED: QtGui.QImage.Format_RGB888,
             ueye.IS_CM_BGR8_PACKED: QtGui.QImage.Format_RGB888,
             ueye.IS_CM_RGBA8_PACKED: QtGui.QImage.Format_RGB32,
             ueye.IS_CM_BGRA8_PACKED: QtGui.QImage.Format_RGB32
    } [ueye_color_format]


class PyuEyeQtView(QtGui.QWidget):
    
    update_signal = QtCore.pyqtSignal(QtGui.QImage, name="update_signal")

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.image = None
        self.save_btn = False
        
        ## Camera sensor view ##
        self.graphics_view = QtGui.QGraphicsView(self)
        self.hbox_main = QtGui.QHBoxLayout()
        self.vbox_btn  = QtGui.QVBoxLayout()
        
        self.scene = QtGui.QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.hbox_main.addWidget(self.graphics_view)

        self.scene.drawBackground = self.draw_background
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.update_signal.connect(self.update_image)

        self.processors = []
        self.resize(715, 512)
        
        ## Button ##        
        self.btn_open = QtGui.QPushButton('Save',self)
        self.btn_open.setToolTip('Save')
        self.btn_open.resize(self.btn_open.sizeHint())
        self.vbox_btn.addWidget(self.btn_open)
        
        self.btn_stop = QtGui.QPushButton('Stop',self)
        self.btn_stop.setToolTip('stop')
        self.btn_stop.resize(self.btn_stop.sizeHint())
        self.vbox_btn.addWidget(self.btn_stop)
        
        self.btn_open.clicked.connect(self.start_to_save_image)
        self.btn_stop.clicked.connect(self.stop_to_save_image)
        
        ## Layout ##
        self.hbox_main.addLayout(self.vbox_btn)
        self.setLayout(self.hbox_main)
    
    def start_to_save_image(self):
        self.save_btn = True
        print('Save image', self.save_btn)
    
    def stop_to_save_image(self):
        self.save_btn = False
        print('Save image', self.save_btn)
        
    def draw_background(self, painter, rect):
        if self.image:
            image = self.image.scaled(rect.width(), rect.height(), QtCore.Qt.KeepAspectRatio)
            painter.drawImage(rect.x(), rect.y(), image)

    def update_image(self, image):
        self.scene.update()

    def user_callback(self, image_data):
        return image_data.as_cv_image()

    def handle(self, image_data):
        self.image = self.user_callback(self, image_data, self.save_btn)
        
        self.update_signal.emit(self.image)

        # unlock the buffer so we can use it again
        image_data.unlock()

    def shutdown(self):
        self.close()

    def add_processor(self, callback):
        self.processors.append(callback)
    

class PyuEyeQtApp:
    def __init__(self, args=[]):        
        self.qt_app = QtGui.QApplication(args)
            
    def exec_(self):
        self.qt_app.exec_()

    def exit_connect(self, method):
        self.qt_app.aboutToQuit.connect(method)
