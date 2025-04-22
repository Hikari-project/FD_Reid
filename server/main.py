# coding: utf-8
# @Author    : LittleAnt
# @Time      :
# @Descrip   : Please contact [wechat:cv_littleant] on WeChat for any questions.

import os
import sys

import onnxruntime as ort
from GUI.subpage.UiPageRegister import PageRegister
from GUI.subpage.UiPageManager import PageManager
from GUI.subpage.UiPageProcess import PageProcess
from GUI.subpage.UiFunctions import UIFuncitons
from GUI.ui.home import Ui_MainWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMenu
from PySide6.QtGui import QImage, QPixmap, QColor, QIcon
from PySide6.QtCore import QTimer, QThread, Signal, QObject, QPoint, Qt
os.environ['KMP_DUPLICATE_LIB_OK']='True'

class MainWindow(QMainWindow, Ui_MainWindow, PageRegister, PageManager, PageProcess, UIFuncitons):
    main_process_thread = Signal()
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.reid_pipeline = None
        PageManager.set_mag_page(self)
        PageProcess.set_proc_page(self)
        PageRegister.set_reg_page(self)
        UIFuncitons.uiDefinitions(self)

        # multi_page connect
        self.model_box.currentTextChanged.connect(self.change_model)
        self.device_box.currentTextChanged.connect(self.change_device)
        self.sample_ft_spinbox.valueChanged.connect(lambda x:self.change_val(x, 'sample_ft_spinbox')) 
        self.sample_ft_slider.valueChanged.connect(lambda x:self.change_val(x, 'sample_ft_slider')) 
        self.thresh_spinbox.valueChanged.connect(lambda x:self.change_val(x, 'thresh_spinbox')) 
        self.thresh_slider.valueChanged.connect(lambda x:self.change_val(x, 'thresh_slider')) 

        # stack weiget change
        self.btn_reg.clicked.connect(self.buttonClick)
        self.btn_proc.clicked.connect(self.buttonClick)
        self.btn_mag.clicked.connect(self.buttonClick)
        self.btn_exit.clicked.connect(self.buttonClick)

        self.ToggleBotton.clicked.connect(lambda: UIFuncitons.toggleMenu(self, True)) 
        self.settings_button.clicked.connect(lambda: UIFuncitons.settingBox(self, True)) 

    def change_model(self):
        select_track_model = self.model_box.currentText()
        if "botsort" == select_track_model.lower():
            self.reid_pipeline.track_method = "botsort.yaml"
        else:   
            self.reid_pipeline.track_method = "bytetrack.yaml"
    
    
    def mousePressEvent(self, event):
        p = event.globalPosition()
        globalPos = p.toPoint()
        self.dragPos = globalPos

    def change_device(self):
        select_device = self.device_box.currentText()
        if "gpu" in select_device.lower():
            if ort.get_device() == 'GPU':
                device = "gpu"
            else:
                device = "cpu"
                print("GPU environment is not configured!!!")
                self.device_box.setCurrentText("CPU")
        else:
            device = "cpu"
        self.reid_pipeline.reload_reid_model(device=device)

    def change_val(self, x, flag):
        if flag == 'sample_ft_spinbox':
            self.sample_ft_slider.setValue(int(x))    # The box value changes, changing the slider
            print("The video sample ft is set to {}".format(x))
            self.proc_class.skip_frames = int(x)
        elif flag == 'sample_ft_slider':
            self.sample_ft_spinbox.setValue(x)        # The slider value changes, changing the box
            print("The video sample ft is set to {}".format(x))
            self.proc_class.skip_frames = int(x)
        elif flag == 'thresh_spinbox':
            self.thresh_slider.setValue(int(x*100))
            print("The match threshold is set to {}".format(x))
            self.proc_class.match_thresh = float(x)
        elif flag == 'thresh_slider':
            self.thresh_spinbox.setValue(x/100)
            print("The match threshold is set to {}".format(x/100))
            self.proc_class.match_thresh = float(x/100)


    def buttonClick(self):
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == 'btn_reg':
            self.stackedWidget.setCurrentWidget(self.reg)
        
        if btnName == 'btn_proc':
            self.stackedWidget.setCurrentWidget(self.proc)
        
        if btnName == 'btn_mag':
            self.stackedWidget.setCurrentWidget(self.manager)
        
        if btnName == 'btn_exit':
            self.stackedWidget.setCurrentWidget(self.proc)
        print(f'Button "{btnName}" pressed!')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = QIcon("./ui/images/icons_v2/our_id.jpg")
    app.setWindowIcon(icon)
    home = MainWindow()
    home.show()
    sys.exit(app.exec())