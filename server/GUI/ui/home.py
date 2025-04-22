# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QCursor,
                           QFont, QIcon)
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox,
                               QFrame, QGridLayout, QHBoxLayout, QLCDNumber, QLabel, QLayout, QLineEdit,
                               QProgressBar, QPushButton, QSizePolicy,
                               QSlider, QSpacerItem, QSpinBox, QStackedWidget,
                               QTableView, QVBoxLayout, QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(940, 643)
        MainWindow.setMinimumSize(QSize(940, 560))
        self.LittleAntP2 = QWidget(MainWindow)
        self.LittleAntP2.setObjectName(u"LittleAntP2")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.LittleAntP2.setFont(font)
        self.LittleAntP2.setStyleSheet(u"")
        self.gridLayout_5 = QGridLayout(self.LittleAntP2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.Main_QF = QFrame(self.LittleAntP2)
        self.Main_QF.setObjectName(u"Main_QF")
        self.Main_QF.setStyleSheet(u"QFrame#Main_QF{\n"
"	background-color: qlineargradient(x0:0, y0:1, x1:1, y1:1,stop:0.4  rgb(107, 128, 210), stop:1 rgb(180, 140, 255));\n"
"border:0px solid red;\n"
"border-radius:0px\n"
"}")
        self.Main_QF.setFrameShape(QFrame.NoFrame)
        self.Main_QF.setFrameShadow(QFrame.Raised)
        self.appLayout = QHBoxLayout(self.Main_QF)
        self.appLayout.setSpacing(0)
        self.appLayout.setObjectName(u"appLayout")
        self.appLayout.setContentsMargins(0, 0, 0, 0)
        self.LeftMenuBg = QFrame(self.Main_QF)
        self.LeftMenuBg.setObjectName(u"LeftMenuBg")
        self.LeftMenuBg.setMinimumSize(QSize(40, 0))
        self.LeftMenuBg.setMaximumSize(QSize(40, 16777215))
        self.LeftMenuBg.setStyleSheet(u"QFrame#LeftMenuBg{\n"
"	background-color: rgba(255, 255, 255,0);\n"
"border:0px solid red;\n"
"border-radius:30px\n"
"}")
        self.LeftMenuBg.setFrameShape(QFrame.NoFrame)
        self.LeftMenuBg.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.LeftMenuBg)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.LeftMenu = QFrame(self.LeftMenuBg)
        self.LeftMenu.setObjectName(u"LeftMenu")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        self.LeftMenu.setFont(font1)
        self.LeftMenu.setFrameShape(QFrame.NoFrame)
        self.LeftMenu.setFrameShadow(QFrame.Raised)
        self.verticalMenuLayout = QVBoxLayout(self.LeftMenu)
        self.verticalMenuLayout.setSpacing(0)
        self.verticalMenuLayout.setObjectName(u"verticalMenuLayout")
        self.verticalMenuLayout.setContentsMargins(0, 0, 0, 0)
        self.toggleBox = QFrame(self.LeftMenu)
        self.toggleBox.setObjectName(u"toggleBox")
        self.toggleBox.setMaximumSize(QSize(16777215, 45))
        self.toggleBox.setFrameShape(QFrame.NoFrame)
        self.toggleBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.toggleBox)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.ToggleBotton = QPushButton(self.toggleBox)
        self.ToggleBotton.setObjectName(u"ToggleBotton")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ToggleBotton.sizePolicy().hasHeightForWidth())
        self.ToggleBotton.setSizePolicy(sizePolicy)
        self.ToggleBotton.setMinimumSize(QSize(0, 45))
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(13)
        font2.setBold(True)
        font2.setItalic(False)
        self.ToggleBotton.setFont(font2)
        self.ToggleBotton.setCursor(QCursor(Qt.PointingHandCursor))
        self.ToggleBotton.setLayoutDirection(Qt.LeftToRight)
        self.ToggleBotton.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 8px solid transparent;\n"
"\n"
"text-align: left;\n"
"padding-left: 0px;\n"
"color: rgba(255, 255, 255, 199);\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}")
        icon = QIcon()
        icon.addFile(u":/icons_v2/images/icons_v2/menu.png", QSize(), QIcon.Normal, QIcon.Off)
        self.ToggleBotton.setIcon(icon)
        self.ToggleBotton.setIconSize(QSize(20, 20))
        self.ToggleBotton.setCheckable(True)
        self.ToggleBotton.setAutoDefault(False)

        self.verticalLayout_4.addWidget(self.ToggleBotton)


        self.verticalMenuLayout.addWidget(self.toggleBox)

        self.topMenu = QFrame(self.LeftMenu)
        self.topMenu.setObjectName(u"topMenu")
        self.topMenu.setStyleSheet(u"QFrame#LeftMenuBg{\n"
"	background-color: rgba(255, 255, 255,0);\n"
"border:0px solid red;\n"
"border-radius:30px\n"
"}")
        self.topMenu.setFrameShape(QFrame.NoFrame)
        self.topMenu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.topMenu)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.btn_proc = QPushButton(self.topMenu)
        self.btn_proc.setObjectName(u"btn_proc")
        sizePolicy.setHeightForWidth(self.btn_proc.sizePolicy().hasHeightForWidth())
        self.btn_proc.setSizePolicy(sizePolicy)
        self.btn_proc.setMinimumSize(QSize(0, 45))
        self.btn_proc.setFont(font2)
        self.btn_proc.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_proc.setLayoutDirection(Qt.LeftToRight)
        self.btn_proc.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 8px solid transparent;\n"
"\n"
"text-align: left;\n"
"padding-left: 0px;\n"
"color: rgba(255, 255, 255, 199);\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/icons_v2/images/icons_v2/ai.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_proc.setIcon(icon1)
        self.btn_proc.setIconSize(QSize(20, 20))

        self.verticalLayout_8.addWidget(self.btn_proc)

        self.btn_reg = QPushButton(self.topMenu)
        self.btn_reg.setObjectName(u"btn_reg")
        sizePolicy.setHeightForWidth(self.btn_reg.sizePolicy().hasHeightForWidth())
        self.btn_reg.setSizePolicy(sizePolicy)
        self.btn_reg.setMinimumSize(QSize(0, 45))
        self.btn_reg.setFont(font2)
        self.btn_reg.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_reg.setLayoutDirection(Qt.LeftToRight)
        self.btn_reg.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 8px solid transparent;\n"
"\n"
"text-align: left;\n"
"padding-left: 0px;\n"
"color: rgba(255, 255, 255, 199);\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/icons_v2/images/icons_v2/register.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_reg.setIcon(icon2)
        self.btn_reg.setIconSize(QSize(22, 22))

        self.verticalLayout_8.addWidget(self.btn_reg)

        self.btn_mag = QPushButton(self.topMenu)
        self.btn_mag.setObjectName(u"btn_mag")
        sizePolicy.setHeightForWidth(self.btn_mag.sizePolicy().hasHeightForWidth())
        self.btn_mag.setSizePolicy(sizePolicy)
        self.btn_mag.setMinimumSize(QSize(0, 45))
        self.btn_mag.setFont(font2)
        self.btn_mag.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_mag.setLayoutDirection(Qt.LeftToRight)
        self.btn_mag.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 10px solid transparent;\n"
"\n"
"text-align: left;\n"
"padding-left: 0px;\n"
"color: rgba(255, 255, 255, 199);\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/icons_v2/images/icons_v2/database.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_mag.setIcon(icon3)
        self.btn_mag.setIconSize(QSize(18, 18))

        self.verticalLayout_8.addWidget(self.btn_mag)

        self.btn_exit = QPushButton(self.topMenu)
        self.btn_exit.setObjectName(u"btn_exit")
        sizePolicy.setHeightForWidth(self.btn_exit.sizePolicy().hasHeightForWidth())
        self.btn_exit.setSizePolicy(sizePolicy)
        self.btn_exit.setMinimumSize(QSize(0, 45))
        self.btn_exit.setFont(font2)
        self.btn_exit.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_exit.setLayoutDirection(Qt.LeftToRight)
        self.btn_exit.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 1px solid transparent;\n"
"\n"
"text-align: left center;\n"
"padding-left: 9px;\n"
"color: rgba(255, 255, 255, 199);\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}\n"
"")
        icon4 = QIcon()
        icon4.addFile(u":/icons_v2/images/icons_v2/close.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_exit.setIcon(icon4)

        self.verticalLayout_8.addWidget(self.btn_exit)


        self.verticalMenuLayout.addWidget(self.topMenu, 0, Qt.AlignTop)

        self.bottomMenu = QFrame(self.LeftMenu)
        self.bottomMenu.setObjectName(u"bottomMenu")
        self.bottomMenu.setFrameShape(QFrame.NoFrame)
        self.bottomMenu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.bottomMenu)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)

        self.verticalMenuLayout.addWidget(self.bottomMenu, 0, Qt.AlignBottom)


        self.verticalLayout_3.addWidget(self.LeftMenu)


        self.appLayout.addWidget(self.LeftMenuBg)

        self.contentBox = QFrame(self.Main_QF)
        self.contentBox.setObjectName(u"contentBox")
        self.contentBox.setFrameShape(QFrame.NoFrame)
        self.contentBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.contentBox)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.top = QFrame(self.contentBox)
        self.top.setObjectName(u"top")
        self.top.setMinimumSize(QSize(0, 45))
        self.top.setMaximumSize(QSize(16777215, 45))
        self.top.setFrameShape(QFrame.NoFrame)
        self.top.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.top)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.leftBox = QFrame(self.top)
        self.leftBox.setObjectName(u"leftBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.leftBox.sizePolicy().hasHeightForWidth())
        self.leftBox.setSizePolicy(sizePolicy1)
        self.leftBox.setMinimumSize(QSize(0, 45))
        self.leftBox.setMaximumSize(QSize(16777215, 45))
        self.leftBox.setFrameShape(QFrame.NoFrame)
        self.leftBox.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.leftBox)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout.addWidget(self.leftBox)

        self.rightButtons = QFrame(self.top)
        self.rightButtons.setObjectName(u"rightButtons")
        self.rightButtons.setMinimumSize(QSize(0, 28))
        self.rightButtons.setFrameShape(QFrame.NoFrame)
        self.rightButtons.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.rightButtons)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.settings_button = QPushButton(self.rightButtons)
        self.settings_button.setObjectName(u"settings_button")
        self.settings_button.setMinimumSize(QSize(28, 28))
        self.settings_button.setMaximumSize(QSize(28, 28))
        self.settings_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.settings_button.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"border: none;\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(232, 59, 35);\n"
"}\n"
"\n"
"")
        icon5 = QIcon()
        icon5.addFile(u":/icons_v2/images/icons_v2/gear.png", QSize(), QIcon.Normal, QIcon.Off)
        self.settings_button.setIcon(icon5)
        self.settings_button.setIconSize(QSize(16, 16))

        self.horizontalLayout_2.addWidget(self.settings_button)

        self.min_sf = QPushButton(self.rightButtons)
        self.min_sf.setObjectName(u"min_sf")
        self.min_sf.setMinimumSize(QSize(28, 28))
        self.min_sf.setMaximumSize(QSize(28, 28))
        self.min_sf.setCursor(QCursor(Qt.PointingHandCursor))
        self.min_sf.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"border: none;\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(232, 59, 35);\n"
"}\n"
"\n"
"")
        icon6 = QIcon()
        icon6.addFile(u":/icons_v2/images/icons_v2/minimize-sign.png", QSize(), QIcon.Normal, QIcon.Off)
        self.min_sf.setIcon(icon6)
        self.min_sf.setIconSize(QSize(16, 16))

        self.horizontalLayout_2.addWidget(self.min_sf)

        self.max_sf = QPushButton(self.rightButtons)
        self.max_sf.setObjectName(u"max_sf")
        self.max_sf.setMinimumSize(QSize(28, 28))
        self.max_sf.setMaximumSize(QSize(28, 28))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(10)
        font3.setBold(False)
        font3.setItalic(False)
        font3.setStyleStrategy(QFont.PreferDefault)
        self.max_sf.setFont(font3)
        self.max_sf.setCursor(QCursor(Qt.PointingHandCursor))
        self.max_sf.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"border: none;\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(232, 59, 35);\n"
"}\n"
"\n"
"")
        icon7 = QIcon()
        icon7.addFile(u":/icons_v2/images/icons_v2/maximize.png", QSize(), QIcon.Normal, QIcon.Off)
        self.max_sf.setIcon(icon7)
        self.max_sf.setIconSize(QSize(16, 16))

        self.horizontalLayout_2.addWidget(self.max_sf)

        self.close_button = QPushButton(self.rightButtons)
        self.close_button.setObjectName(u"close_button")
        self.close_button.setMinimumSize(QSize(28, 28))
        self.close_button.setMaximumSize(QSize(28, 28))
        self.close_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_button.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"border: none;\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgba(114, 129, 214, 59);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(232, 59, 35);\n"
"}\n"
"\n"
"")
        self.close_button.setIcon(icon4)
        self.close_button.setIconSize(QSize(16, 16))

        self.horizontalLayout_2.addWidget(self.close_button)


        self.horizontalLayout.addWidget(self.rightButtons, 0, Qt.AlignRight)


        self.verticalLayout_2.addWidget(self.top)

        self.contentBottom = QFrame(self.contentBox)
        self.contentBottom.setObjectName(u"contentBottom")
        self.contentBottom.setFrameShape(QFrame.NoFrame)
        self.contentBottom.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.contentBottom)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.content = QFrame(self.contentBottom)
        self.content.setObjectName(u"content")
        self.content.setFrameShape(QFrame.NoFrame)
        self.content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.content)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.pagesContainer = QFrame(self.content)
        self.pagesContainer.setObjectName(u"pagesContainer")
        self.pagesContainer.setStyleSheet(u"")
        self.pagesContainer.setFrameShape(QFrame.NoFrame)
        self.pagesContainer.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.pagesContainer)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(10, 10, 10, 10)
        self.stackedWidget = QStackedWidget(self.pagesContainer)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"background: transparent;")
        self.manager = QWidget()
        self.manager.setObjectName(u"manager")
        self.manager.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.manager)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.mg_main = QFrame(self.manager)
        self.mg_main.setObjectName(u"mg_main")
        self.mg_main.setFrameShape(QFrame.StyledPanel)
        self.mg_main.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.mg_main)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.mg_left = QFrame(self.mg_main)
        self.mg_left.setObjectName(u"mg_left")
        self.mg_left.setFrameShape(QFrame.StyledPanel)
        self.mg_left.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.mg_left)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.mg_left_1 = QFrame(self.mg_left)
        self.mg_left_1.setObjectName(u"mg_left_1")
        self.mg_left_1.setFont(font1)
        self.mg_left_1.setStyleSheet(u"\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:12px;\n"
"")
        self.mg_left_1.setFrameShape(QFrame.StyledPanel)
        self.mg_left_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.mg_left_1)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.mag_id_nameEdit = QLineEdit(self.mg_left_1)
        self.mag_id_nameEdit.setObjectName(u"mag_id_nameEdit")
        font4 = QFont()
        font4.setFamilies([u"Arial"])
        font4.setPointSize(15)
        self.mag_id_nameEdit.setFont(font4)
        self.mag_id_nameEdit.setStyleSheet(u"")

        self.horizontalLayout_7.addWidget(self.mag_id_nameEdit)

        self.mag_nameedit_button = QPushButton(self.mg_left_1)
        self.mag_nameedit_button.setObjectName(u"mag_nameedit_button")
        self.mag_nameedit_button.setFont(font4)
        self.mag_nameedit_button.setStyleSheet(u"/*\u6309\u94ae\u666e\u901a\u6001*/\n"
"QPushButton\n"
"{\n"
"\n"
"    /*background-color:rgb(14 , 150 , 254);*/\n"
"    /*\u8fb9\u6846\u5706\u89d2\u534a\u5f84\u4e3a8\u50cf\u7d20*/ \n"
"    border-radius:8px;\n"
"    background-color:rgba(255,255,255,90);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u505c\u7559\u6001*/\n"
"QPushButton:hover\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(44 , 137 , 255);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u6309\u4e0b\u6001*/\n"
"QPushButton:pressed\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(14 , 135 , 228);\n"
"    /*\u5de6\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u53f3\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-left:3px;\n"
"    /*\u4e0a\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u4e0b\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-top:3px;\n"
"}")

        self.horizontalLayout_7.addWidget(self.mag_nameedit_button)


        self.gridLayout.addWidget(self.mg_left_1, 1, 0, 1, 1)

        self.mg_left_2 = QFrame(self.mg_left)
        self.mg_left_2.setObjectName(u"mg_left_2")
        self.mg_left_2.setFont(font1)
        self.mg_left_2.setStyleSheet(u"\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:12px;\n"
"")
        self.mg_left_2.setFrameShape(QFrame.StyledPanel)
        self.mg_left_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.mg_left_2)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.mag_del_edit = QLineEdit(self.mg_left_2)
        self.mag_del_edit.setObjectName(u"mag_del_edit")
        self.mag_del_edit.setFont(font4)

        self.horizontalLayout_8.addWidget(self.mag_del_edit)

        self.mag_delete_button = QPushButton(self.mg_left_2)
        self.mag_delete_button.setObjectName(u"mag_delete_button")
        self.mag_delete_button.setFont(font4)
        self.mag_delete_button.setStyleSheet(u"/*\u6309\u94ae\u666e\u901a\u6001*/\n"
"QPushButton\n"
"{\n"
"    /*background-color:rgb(14 , 150 , 254);*/\n"
"    /*\u8fb9\u6846\u5706\u89d2\u534a\u5f84\u4e3a8\u50cf\u7d20*/ \n"
"    border-radius:8px;\n"
"    background-color:rgba(255,255,255,90);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u505c\u7559\u6001*/\n"
"QPushButton:hover\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(44 , 137 , 255);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u6309\u4e0b\u6001*/\n"
"QPushButton:pressed\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(14 , 135 , 228);\n"
"    /*\u5de6\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u53f3\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-left:3px;\n"
"    /*\u4e0a\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u4e0b\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-top:3px;\n"
"}")

        self.horizontalLayout_8.addWidget(self.mag_delete_button)


        self.gridLayout.addWidget(self.mg_left_2, 1, 1, 1, 1)

        self.all_db_showTb = QTableView(self.mg_left)
        self.all_db_showTb.setObjectName(u"all_db_showTb")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.all_db_showTb.sizePolicy().hasHeightForWidth())
        self.all_db_showTb.setSizePolicy(sizePolicy2)
        font5 = QFont()
        font5.setFamilies([u"Arial"])
        font5.setPointSize(15)
        font5.setBold(True)
        self.all_db_showTb.setFont(font5)
        self.all_db_showTb.setStyleSheet(u"background-color:rgba(167, 170, 170,196)")

        self.gridLayout.addWidget(self.all_db_showTb, 0, 0, 1, 2)

        self.gridLayout.setRowStretch(0, 5)

        self.horizontalLayout_6.addWidget(self.mg_left)

        self.frame_5 = QFrame(self.mg_main)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_5)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.mag_grly_img_show = QLabel(self.frame_5)
        self.mag_grly_img_show.setObjectName(u"mag_grly_img_show")
        sizePolicy3 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.mag_grly_img_show.sizePolicy().hasHeightForWidth())
        self.mag_grly_img_show.setSizePolicy(sizePolicy3)
        self.mag_grly_img_show.setMinimumSize(QSize(256, 256))
        self.mag_grly_img_show.setFont(font1)
        self.mag_grly_img_show.setStyleSheet(u"background-color: rgb(238, 242, 255);\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:15px")
        self.mag_grly_img_show.setAlignment(Qt.AlignCenter)

        self.verticalLayout_7.addWidget(self.mag_grly_img_show)

        self.label_7 = QLabel(self.frame_5)
        self.label_7.setObjectName(u"label_7")
        font6 = QFont()
        font6.setFamilies([u"Arial"])
        font6.setPointSize(18)
        font6.setBold(True)
        font6.setItalic(True)
        self.label_7.setFont(font6)

        self.verticalLayout_7.addWidget(self.label_7)

        self.mag_total_reg_num = QLCDNumber(self.frame_5)
        self.mag_total_reg_num.setObjectName(u"mag_total_reg_num")
        self.mag_total_reg_num.setFont(font1)

        self.verticalLayout_7.addWidget(self.mag_total_reg_num)

        self.verticalLayout_7.setStretch(0, 3)
        self.verticalLayout_7.setStretch(1, 2)
        self.verticalLayout_7.setStretch(2, 1)

        self.horizontalLayout_6.addWidget(self.frame_5)

        self.horizontalLayout_6.setStretch(0, 2)
        self.horizontalLayout_6.setStretch(1, 1)

        self.verticalLayout.addWidget(self.mg_main)

        self.stackedWidget.addWidget(self.manager)
        self.reg = QWidget()
        self.reg.setObjectName(u"reg")
        self.horizontalLayout_10 = QHBoxLayout(self.reg)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.reg_main = QFrame(self.reg)
        self.reg_main.setObjectName(u"reg_main")
        self.reg_main.setFrameShape(QFrame.StyledPanel)
        self.reg_main.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.reg_main)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.reg_show_main_img = QLabel(self.reg_main)
        self.reg_show_main_img.setObjectName(u"reg_show_main_img")
        self.reg_show_main_img.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.reg_show_main_img.sizePolicy().hasHeightForWidth())
        self.reg_show_main_img.setSizePolicy(sizePolicy3)
        self.reg_show_main_img.setFont(font1)
        self.reg_show_main_img.setStyleSheet(u"background-color: rgb(238, 242, 255);\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:15px")
        self.reg_show_main_img.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_12.addWidget(self.reg_show_main_img)

        self.frame_7 = QFrame(self.reg_main)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.frame_7)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(-1, 0, -1, 0)
        self.reg_show_crop_img = QLabel(self.frame_7)
        self.reg_show_crop_img.setObjectName(u"reg_show_crop_img")
        sizePolicy3.setHeightForWidth(self.reg_show_crop_img.sizePolicy().hasHeightForWidth())
        self.reg_show_crop_img.setSizePolicy(sizePolicy3)
        self.reg_show_crop_img.setFont(font1)
        self.reg_show_crop_img.setStyleSheet(u"background-color: rgb(238, 242, 255);\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:15px")
        self.reg_show_crop_img.setAlignment(Qt.AlignCenter)

        self.verticalLayout_13.addWidget(self.reg_show_crop_img)

        self.frame_8 = QFrame(self.frame_7)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.gridLayout_6 = QGridLayout(self.frame_8)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(-1, 50, -1, -1)
        self.reg_id_lineEdit = QLineEdit(self.frame_8)
        self.reg_id_lineEdit.setObjectName(u"reg_id_lineEdit")
        self.reg_id_lineEdit.setMinimumSize(QSize(0, 30))
        self.reg_id_lineEdit.setMaximumSize(QSize(16777215, 50))
        font7 = QFont()
        font7.setFamilies([u"Arial"])
        font7.setPointSize(14)
        font7.setBold(True)
        self.reg_id_lineEdit.setFont(font7)
        self.reg_id_lineEdit.setStyleSheet(u"border-radius:8px;\n"
"background-color:rgba(255,255,255,90);")

        self.gridLayout_6.addWidget(self.reg_id_lineEdit, 3, 1, 1, 2)

        self.reg_processd_box = QComboBox(self.frame_8)
        self.reg_processd_box.addItem("")
        self.reg_processd_box.setObjectName(u"reg_processd_box")
        self.reg_processd_box.setMinimumSize(QSize(0, 30))
        self.reg_processd_box.setMaximumSize(QSize(16777215, 50))
        self.reg_processd_box.setFont(font2)
        self.reg_processd_box.setStyleSheet(u"\n"
"QComboBox {\n"
"            background-color: rgba(255,255,255,90);\n"
"			color: rgba(0, 0, 0, 200);\n"
"            border: 1px solid lightgray;\n"
"            border-radius: 10px;\n"
"            padding-left: 15px;\n"
"        }\n"
"        \n"
"        QComboBox:on {\n"
"            border: 1px solid #63acfb;\n"
"        }\n"
"\n"
"        QComboBox::drop-down {\n"
"            width: 22px;\n"
"            border-left: 1px solid lightgray;\n"
"            border-top-right-radius: 15px;\n"
"            border-bottom-right-radius: 15px;\n"
"        }\n"
"        \n"
"        QComboBox::drop-down:on {\n"
"            border-left: 1px solid #63acfb;\n"
"        }\n"
"\n"
"        QComboBox::down-arrow {\n"
"            width: 16px;\n"
"            height: 16px;\n"
"            image: url(:/icons_v2/images/icons_v2/box_down.png);\n"
"        }\n"
"\n"
"        QComboBox::down-arrow:on {\n"
"            image: url(:/icons_v2/images/icons_v2/box_up.png)\n"
"        }\n"
"\n"
"        QComboBox QAbstractIte"
                        "mView {\n"
"            border: none;\n"
"            outline: none;\n"
"			padding: 10px;\n"
"            background-color: rgb(223, 188, 220);\n"
"        }\n"
"\n"
"\n"
"        QComboBox QScrollBar:vertical {\n"
"            width: 2px;\n"
"           background-color: rgba(255,255,255,150);\n"
"        }\n"
"\n"
"        QComboBox QScrollBar::handle:vertical {\n"
"            background-color: rgba(255,255,255,90);\n"
"        }")

        self.gridLayout_6.addWidget(self.reg_processd_box, 2, 0, 1, 3)

        self.reg_to_makesure_reg = QPushButton(self.frame_8)
        self.reg_to_makesure_reg.setObjectName(u"reg_to_makesure_reg")
        self.reg_to_makesure_reg.setMinimumSize(QSize(0, 40))
        self.reg_to_makesure_reg.setMaximumSize(QSize(16777215, 60))
        self.reg_to_makesure_reg.setFont(font5)
        self.reg_to_makesure_reg.setStyleSheet(u"/*\u6309\u94ae\u666e\u901a\u6001*/\n"
"QPushButton\n"
"{  \n"
"    border-radius:8px;\n"
"    background-color:rgba(255,255,255,90);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u505c\u7559\u6001*/\n"
"QPushButton:hover\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(44 , 137 , 255);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u6309\u4e0b\u6001*/\n"
"QPushButton:pressed\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(14 , 135 , 228);\n"
"    /*\u5de6\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u53f3\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-left:3px;\n"
"    /*\u4e0a\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u4e0b\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-top:3px;\n"
"}")

        self.gridLayout_6.addWidget(self.reg_to_makesure_reg, 4, 0, 1, 3)

        self.reg_file_process = QPushButton(self.frame_8)
        self.reg_file_process.setObjectName(u"reg_file_process")
        self.reg_file_process.setMinimumSize(QSize(0, 30))
        self.reg_file_process.setMaximumSize(QSize(16777215, 50))
        self.reg_file_process.setFont(font7)
        self.reg_file_process.setStyleSheet(u"/*\u6309\u94ae\u666e\u901a\u6001*/\n"
"QPushButton\n"
"{\n"
"    border-radius:8px;\n"
"    background-color:rgba(255,255,255,90);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u505c\u7559\u6001*/\n"
"QPushButton:hover\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(44 , 137 , 255);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u6309\u4e0b\u6001*/\n"
"QPushButton:pressed\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(14 , 135 , 228);\n"
"    /*\u5de6\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u53f3\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-left:3px;\n"
"    /*\u4e0a\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u4e0b\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-top:3px;\n"
"}")

        self.gridLayout_6.addWidget(self.reg_file_process, 1, 0, 1, 3)

        self.pushButton_2 = QPushButton(self.frame_8)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMinimumSize(QSize(0, 30))
        self.pushButton_2.setMaximumSize(QSize(16777215, 50))
        self.pushButton_2.setFont(font1)
        self.pushButton_2.setStyleSheet(u"")
        icon8 = QIcon()
        icon8.addFile(u":/icons_v2/images/icons_v2/id-card.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_2.setIcon(icon8)
        self.pushButton_2.setIconSize(QSize(25, 25))

        self.gridLayout_6.addWidget(self.pushButton_2, 3, 0, 1, 1)

        self.reg_file_open = QPushButton(self.frame_8)
        self.reg_file_open.setObjectName(u"reg_file_open")
        self.reg_file_open.setMinimumSize(QSize(30, 30))
        self.reg_file_open.setMaximumSize(QSize(16777215, 50))
        self.reg_file_open.setFont(font1)
        self.reg_file_open.setStyleSheet(u"/*\u6309\u94ae\u505c\u7559\u6001*/\n"
"QPushButton:hover\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(44 , 137 , 255);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u6309\u4e0b\u6001*/\n"
"QPushButton:pressed\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(14 , 135 , 228);\n"
"    /*\u5de6\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u53f3\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-left:3px;\n"
"    /*\u4e0a\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u4e0b\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-top:3px;\n"
"}")
        icon9 = QIcon()
        icon9.addFile(u":/icons_v2/images/icons_v2/image-gallery.png", QSize(), QIcon.Normal, QIcon.Off)
        self.reg_file_open.setIcon(icon9)
        self.reg_file_open.setIconSize(QSize(25, 25))
        self.reg_file_open.setCheckable(True)

        self.gridLayout_6.addWidget(self.reg_file_open, 0, 0, 1, 1)

        self.reg_file_lineEdit = QLineEdit(self.frame_8)
        self.reg_file_lineEdit.setObjectName(u"reg_file_lineEdit")
        self.reg_file_lineEdit.setMinimumSize(QSize(0, 30))
        self.reg_file_lineEdit.setMaximumSize(QSize(16777215, 50))
        font8 = QFont()
        font8.setFamilies([u"Arial"])
        font8.setPointSize(14)
        font8.setBold(False)
        self.reg_file_lineEdit.setFont(font8)
        self.reg_file_lineEdit.setCursor(QCursor(Qt.ArrowCursor))
        self.reg_file_lineEdit.setStyleSheet(u"border-radius:8px;\n"
"background-color:rgba(255,255,255,90);")
        self.reg_file_lineEdit.setInputMethodHints(Qt.ImhNone)
        self.reg_file_lineEdit.setText(u"  \u8bf7\u6253\u5f00\u6ce8\u518c\u56fe\u50cf")
        self.reg_file_lineEdit.setFrame(True)
        self.reg_file_lineEdit.setEchoMode(QLineEdit.Normal)
        self.reg_file_lineEdit.setCursorPosition(9)
        self.reg_file_lineEdit.setAlignment(Qt.AlignJustify|Qt.AlignVCenter)
        self.reg_file_lineEdit.setDragEnabled(False)
        self.reg_file_lineEdit.setReadOnly(True)

        self.gridLayout_6.addWidget(self.reg_file_lineEdit, 0, 1, 1, 2)


        self.verticalLayout_13.addWidget(self.frame_8)


        self.horizontalLayout_12.addWidget(self.frame_7)

        self.horizontalLayout_12.setStretch(0, 2)
        self.horizontalLayout_12.setStretch(1, 1)

        self.horizontalLayout_10.addWidget(self.reg_main)

        self.stackedWidget.addWidget(self.reg)
        self.proc = QWidget()
        self.proc.setObjectName(u"proc")
        self.verticalLayout_20 = QVBoxLayout(self.proc)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.proc_main = QFrame(self.proc)
        self.proc_main.setObjectName(u"proc_main")
        self.proc_main.setFrameShape(QFrame.StyledPanel)
        self.proc_main.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.proc_main)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.proc_mian_top_left = QFrame(self.proc_main)
        self.proc_mian_top_left.setObjectName(u"proc_mian_top_left")
        self.proc_mian_top_left.setFrameShape(QFrame.StyledPanel)
        self.proc_mian_top_left.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.proc_mian_top_left)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.det_pano_img = QLabel(self.proc_mian_top_left)
        self.det_pano_img.setObjectName(u"det_pano_img")
        sizePolicy3.setHeightForWidth(self.det_pano_img.sizePolicy().hasHeightForWidth())
        self.det_pano_img.setSizePolicy(sizePolicy3)
        self.det_pano_img.setFont(font1)
        self.det_pano_img.setStyleSheet(u"background-color: rgb(238, 242, 255);\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:15px")
        self.det_pano_img.setAlignment(Qt.AlignCenter)

        self.verticalLayout_11.addWidget(self.det_pano_img)

        self.proc_bar_qf = QFrame(self.proc_mian_top_left)
        self.proc_bar_qf.setObjectName(u"proc_bar_qf")
        self.proc_bar_qf.setFrameShape(QFrame.StyledPanel)
        self.proc_bar_qf.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.proc_bar_qf)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.proc_run_button = QPushButton(self.proc_bar_qf)
        self.proc_run_button.setObjectName(u"proc_run_button")
        self.proc_run_button.setFont(font1)
        self.proc_run_button.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: center;\n"
"border: none;\n"
"}\n"
"QPushButton:hover{\n"
"\n"
"}")
        icon10 = QIcon()
        icon10.addFile(u":/icons_v2/images/icons_v2/begin.png", QSize(), QIcon.Normal, QIcon.Off)
        icon10.addFile(u":/icons_v2/images/icons_v2/pause.png", QSize(), QIcon.Normal, QIcon.On)
        self.proc_run_button.setIcon(icon10)
        self.proc_run_button.setIconSize(QSize(20, 20))
        self.proc_run_button.setCheckable(True)

        self.horizontalLayout_9.addWidget(self.proc_run_button)

        self.progress_bar = QProgressBar(self.proc_bar_qf)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setMaximumSize(QSize(16777215, 20))
        font9 = QFont()
        font9.setFamilies([u"Microsoft YaHei UI"])
        font9.setPointSize(10)
        font9.setBold(True)
        font9.setItalic(False)
        self.progress_bar.setFont(font9)
        self.progress_bar.setStyleSheet(u"QProgressBar{ \n"
"font: 700 10pt \"Microsoft YaHei UI\";\n"
"color: rgb(253, 143, 134); \n"
"text-align:center; \n"
"border:3px solid rgb(255, 255, 255);\n"
"border-radius: 10px; \n"
"background-color: rgba(215, 215, 215,100);\n"
"} \n"
"\n"
"QProgressBar:chunk{ \n"
"border-radius:0px; \n"
"background: rgba(119, 111, 252, 200);\n"
"border-radius: 7px;\n"
"}")
        self.progress_bar.setMaximum(1000)
        self.progress_bar.setValue(0)

        self.horizontalLayout_9.addWidget(self.progress_bar)

        self.proc_stop_button = QPushButton(self.proc_bar_qf)
        self.proc_stop_button.setObjectName(u"proc_stop_button")
        self.proc_stop_button.setFont(font1)
        self.proc_stop_button.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: center;\n"
"border: none;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"\n"
"}")
        icon11 = QIcon()
        icon11.addFile(u":/icons_v2/images/icons_v2/stop.png", QSize(), QIcon.Normal, QIcon.Off)
        self.proc_stop_button.setIcon(icon11)
        self.proc_stop_button.setIconSize(QSize(20, 20))

        self.horizontalLayout_9.addWidget(self.proc_stop_button)

        self.horizontalLayout_9.setStretch(0, 1)
        self.horizontalLayout_9.setStretch(1, 10)
        self.horizontalLayout_9.setStretch(2, 1)

        self.verticalLayout_11.addWidget(self.proc_bar_qf)

        self.verticalLayout_11.setStretch(0, 10)
        self.verticalLayout_11.setStretch(1, 1)

        self.gridLayout_4.addWidget(self.proc_mian_top_left, 0, 0, 1, 1)

        self.proc_main_top_right = QFrame(self.proc_main)
        self.proc_main_top_right.setObjectName(u"proc_main_top_right")
        self.proc_main_top_right.setFrameShape(QFrame.StyledPanel)
        self.proc_main_top_right.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.proc_main_top_right)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(12, 0, 0, 30)
        self.process_table_show = QTableView(self.proc_main_top_right)
        self.process_table_show.setObjectName(u"process_table_show")
        sizePolicy2.setHeightForWidth(self.process_table_show.sizePolicy().hasHeightForWidth())
        self.process_table_show.setSizePolicy(sizePolicy2)
        self.process_table_show.setFont(font7)
        self.process_table_show.setStyleSheet(u"background-color:rgba(167, 170, 170,196)")

        self.verticalLayout_10.addWidget(self.process_table_show)


        self.gridLayout_4.addWidget(self.proc_main_top_right, 0, 1, 1, 1)

        self.label_11 = QLabel(self.proc_main)
        self.label_11.setObjectName(u"label_11")
        font10 = QFont()
        font10.setFamilies([u"Segoe UI"])
        font10.setPointSize(16)
        font10.setBold(True)
        font10.setItalic(True)
        self.label_11.setFont(font10)
        self.label_11.setStyleSheet(u"font: 700 italic 16pt \"Segoe UI\";")

        self.gridLayout_4.addWidget(self.label_11, 1, 0, 1, 1)

        self.label_4 = QLabel(self.proc_main)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"font: 700 italic 16pt \"Segoe UI\";")

        self.gridLayout_4.addWidget(self.label_4, 1, 1, 1, 1)

        self.proc_main_bottom_left = QFrame(self.proc_main)
        self.proc_main_bottom_left.setObjectName(u"proc_main_bottom_left")
        self.proc_main_bottom_left.setFrameShape(QFrame.StyledPanel)
        self.proc_main_bottom_left.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.proc_main_bottom_left)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.save_csv_checkbox = QCheckBox(self.proc_main_bottom_left)
        self.save_csv_checkbox.setObjectName(u"save_csv_checkbox")
        self.save_csv_checkbox.setMinimumSize(QSize(0, 25))
        self.save_csv_checkbox.setFont(font2)
        self.save_csv_checkbox.setStyleSheet(u"\n"
"        QCheckBox::indicator {\n"
"            padding-top: 1px;\n"
"   padding-left: 10px;\n"
"            width: 60px;\n"
"            height: 40px;\n"
"            border: none;\n"
"        }\n"
"\n"
"        QCheckBox::indicator:unchecked {\n"
"            image: url(:/icons_v2/images/icons_v2/check_no.png);\n"
"        }\n"
"\n"
"        QCheckBox::indicator:checked {\n"
"            image: url(:/icons_v2/images/icons_v2/check_yes.png);\n"
"        }")

        self.gridLayout_3.addWidget(self.save_csv_checkbox, 0, 3, 1, 1)

        self.process_file_button = QPushButton(self.proc_main_bottom_left)
        self.process_file_button.setObjectName(u"process_file_button")
        self.process_file_button.setMinimumSize(QSize(30, 30))
        self.process_file_button.setFont(font1)
        self.process_file_button.setStyleSheet(u"/*\u6309\u94ae\u505c\u7559\u6001*/\n"
"QPushButton:hover\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(44 , 137 , 255);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u6309\u4e0b\u6001*/\n"
"QPushButton:pressed\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(14 , 135 , 228);\n"
"    /*\u5de6\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u53f3\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-left:3px;\n"
"    /*\u4e0a\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u4e0b\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-top:3px;\n"
"}")
        icon12 = QIcon()
        icon12.addFile(u":/icons_v2/images/icons_v2/film-reel.png", QSize(), QIcon.Normal, QIcon.Off)
        self.process_file_button.setIcon(icon12)
        self.process_file_button.setIconSize(QSize(25, 25))
        self.process_file_button.setCheckable(True)

        self.gridLayout_3.addWidget(self.process_file_button, 0, 0, 1, 1)

        self.process_file_edit = QLineEdit(self.proc_main_bottom_left)
        self.process_file_edit.setObjectName(u"process_file_edit")
        self.process_file_edit.setMinimumSize(QSize(200, 25))
        self.process_file_edit.setMaximumSize(QSize(400, 25))
        font11 = QFont()
        font11.setFamilies([u"Arial"])
        font11.setBold(False)
        self.process_file_edit.setFont(font11)
        self.process_file_edit.setCursor(QCursor(Qt.ArrowCursor))
        self.process_file_edit.setStyleSheet(u" border-radius:8px;\n"
"background-color:rgba(255,255,255,90);")
        self.process_file_edit.setInputMethodHints(Qt.ImhNone)
        self.process_file_edit.setEchoMode(QLineEdit.Normal)
        self.process_file_edit.setCursorPosition(12)
        self.process_file_edit.setDragEnabled(False)
        self.process_file_edit.setReadOnly(True)

        self.gridLayout_3.addWidget(self.process_file_edit, 0, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.process_dir_button = QPushButton(self.proc_main_bottom_left)
        self.process_dir_button.setObjectName(u"process_dir_button")
        self.process_dir_button.setMinimumSize(QSize(30, 30))
        self.process_dir_button.setFont(font1)
        self.process_dir_button.setStyleSheet(u"/*\u6309\u94ae\u505c\u7559\u6001*/\n"
"QPushButton:hover\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(44 , 137 , 255);\n"
"}\n"
"\n"
"/*\u6309\u94ae\u6309\u4e0b\u6001*/\n"
"QPushButton:pressed\n"
"{\n"
"    /*\u80cc\u666f\u989c\u8272*/  \n"
"    background-color:rgb(14 , 135 , 228);\n"
"    /*\u5de6\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u53f3\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-left:3px;\n"
"    /*\u4e0a\u5185\u8fb9\u8ddd\u4e3a3\u50cf\u7d20\uff0c\u8ba9\u6309\u4e0b\u65f6\u5b57\u5411\u4e0b\u79fb\u52a83\u50cf\u7d20*/  \n"
"    padding-top:3px;\n"
"}")
        icon13 = QIcon()
        icon13.addFile(u":/icons_v2/images/icons_v2/folder.png", QSize(), QIcon.Normal, QIcon.Off)
        self.process_dir_button.setIcon(icon13)
        self.process_dir_button.setIconSize(QSize(25, 25))
        self.process_dir_button.setCheckable(True)

        self.gridLayout_3.addWidget(self.process_dir_button, 2, 0, 1, 1)

        self.istrack_checkbox = QCheckBox(self.proc_main_bottom_left)
        self.istrack_checkbox.setObjectName(u"istrack_checkbox")
        self.istrack_checkbox.setMinimumSize(QSize(0, 25))
        font12 = QFont()
        font12.setFamilies([u"Arial"])
        font12.setPointSize(13)
        font12.setBold(True)
        self.istrack_checkbox.setFont(font12)
        self.istrack_checkbox.setStyleSheet(u"\n"
"QCheckBox::indicator {\n"
"	font: 13pt \"Arial\";\n"
"  padding-top: 1px;\n"
"   padding-left: 10px;\n"
"            width: 60px;\n"
"            height: 40px;\n"
"            border: none;\n"
"        }\n"
"\n"
"        QCheckBox::indicator:unchecked {\n"
"            image: url(:/icons_v2/images/icons_v2/check_no.png);\n"
"        }\n"
"\n"
"        QCheckBox::indicator:checked {\n"
"            image: url(:/icons_v2/images/icons_v2/check_yes.png);\n"
"        }")

        self.gridLayout_3.addWidget(self.istrack_checkbox, 2, 3, 1, 1)

        self.save_media_checkbox = QCheckBox(self.proc_main_bottom_left)
        self.save_media_checkbox.setObjectName(u"save_media_checkbox")
        self.save_media_checkbox.setMinimumSize(QSize(0, 25))
        self.save_media_checkbox.setFont(font2)
        self.save_media_checkbox.setStyleSheet(u"\n"
"        QCheckBox::indicator {\n"
"            padding-top: 1px;\n"
"   padding-left: 10px;\n"
"            width: 60px;\n"
"            height: 40px;\n"
"            border: none;\n"
"        }\n"
"\n"
"        QCheckBox::indicator:unchecked {\n"
"            image: url(:/icons_v2/images/icons_v2/check_no.png);\n"
"        }\n"
"\n"
"        QCheckBox::indicator:checked {\n"
"            image: url(:/icons_v2/images/icons_v2/check_yes.png);\n"
"        }")

        self.gridLayout_3.addWidget(self.save_media_checkbox, 1, 3, 1, 1)

        self.label_10 = QLabel(self.proc_main_bottom_left)
        self.label_10.setObjectName(u"label_10")
        font13 = QFont()
        font13.setFamilies([u"Segoe UI"])
        font13.setPointSize(12)
        font13.setBold(True)
        font13.setItalic(True)
        self.label_10.setFont(font13)
        self.label_10.setStyleSheet(u"font: 700 italic 12pt \"Segoe UI\";")

        self.gridLayout_3.addWidget(self.label_10, 1, 0, 1, 2)

        self.process_dir_edit = QLineEdit(self.proc_main_bottom_left)
        self.process_dir_edit.setObjectName(u"process_dir_edit")
        self.process_dir_edit.setMinimumSize(QSize(200, 25))
        self.process_dir_edit.setMaximumSize(QSize(400, 25))
        self.process_dir_edit.setFont(font11)
        self.process_dir_edit.setCursor(QCursor(Qt.ArrowCursor))
        self.process_dir_edit.setStyleSheet(u" border-radius:8px;\n"
"background-color:rgba(255,255,255,90);")
        self.process_dir_edit.setInputMethodHints(Qt.ImhNone)
        self.process_dir_edit.setEchoMode(QLineEdit.Normal)
        self.process_dir_edit.setCursorPosition(17)
        self.process_dir_edit.setDragEnabled(False)
        self.process_dir_edit.setReadOnly(True)

        self.gridLayout_3.addWidget(self.process_dir_edit, 2, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 3, 3, 1, 1)

        self.gridLayout_3.setRowStretch(0, 1)
        self.gridLayout_3.setRowStretch(1, 6)
        self.gridLayout_3.setRowStretch(2, 4)

        self.gridLayout_4.addWidget(self.proc_main_bottom_left, 2, 0, 1, 1)

        self.proc_main_bottom_right = QFrame(self.proc_main)
        self.proc_main_bottom_right.setObjectName(u"proc_main_bottom_right")
        self.proc_main_bottom_right.setFrameShape(QFrame.StyledPanel)
        self.proc_main_bottom_right.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.proc_main_bottom_right)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(12, 0, 0, 0)
        self.match_show_img = QLabel(self.proc_main_bottom_right)
        self.match_show_img.setObjectName(u"match_show_img")
        sizePolicy3.setHeightForWidth(self.match_show_img.sizePolicy().hasHeightForWidth())
        self.match_show_img.setSizePolicy(sizePolicy3)
        self.match_show_img.setFont(font1)
        self.match_show_img.setStyleSheet(u"background-color: rgb(238, 242, 255);\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:15px")
        self.match_show_img.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.match_show_img, 0, 0, 3, 1)

        self.label_3 = QLabel(self.proc_main_bottom_right)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font11)
        self.label_3.setStyleSheet(u"")
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label_3.setWordWrap(False)

        self.gridLayout_2.addWidget(self.label_3, 0, 1, 1, 1)

        self.match_show_id = QLineEdit(self.proc_main_bottom_right)
        self.match_show_id.setObjectName(u"match_show_id")
        self.match_show_id.setMinimumSize(QSize(100, 25))
        self.match_show_id.setFont(font12)
        self.match_show_id.setStyleSheet(u"\n"
"background-color:rgb(198, 225, 240);")

        self.gridLayout_2.addWidget(self.match_show_id, 0, 2, 1, 1)

        self.label_8 = QLabel(self.proc_main_bottom_right)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font11)
        self.label_8.setStyleSheet(u"")
        self.label_8.setAlignment(Qt.AlignCenter)
        self.label_8.setWordWrap(False)

        self.gridLayout_2.addWidget(self.label_8, 1, 1, 1, 1)

        self.match_show_status = QLineEdit(self.proc_main_bottom_right)
        self.match_show_status.setObjectName(u"match_show_status")
        self.match_show_status.setMinimumSize(QSize(100, 25))
        self.match_show_status.setFont(font12)
        self.match_show_status.setStyleSheet(u"\n"
"background-color:rgb(198, 225, 240);")

        self.gridLayout_2.addWidget(self.match_show_status, 1, 2, 1, 1)

        self.label_9 = QLabel(self.proc_main_bottom_right)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font11)
        self.label_9.setStyleSheet(u"")
        self.label_9.setAlignment(Qt.AlignCenter)
        self.label_9.setWordWrap(False)

        self.gridLayout_2.addWidget(self.label_9, 2, 1, 1, 1)

        self.match_show_dist = QLineEdit(self.proc_main_bottom_right)
        self.match_show_dist.setObjectName(u"match_show_dist")
        self.match_show_dist.setMinimumSize(QSize(100, 25))
        self.match_show_dist.setFont(font12)
        self.match_show_dist.setStyleSheet(u"\n"
"background-color:rgb(198, 225, 240);")

        self.gridLayout_2.addWidget(self.match_show_dist, 2, 2, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 4)
        self.gridLayout_2.setColumnStretch(2, 2)

        self.gridLayout_4.addWidget(self.proc_main_bottom_right, 2, 1, 1, 1)

        self.gridLayout_4.setRowStretch(0, 5)
        self.gridLayout_4.setRowStretch(2, 2)
        self.gridLayout_4.setColumnStretch(0, 2)
        self.gridLayout_4.setColumnStretch(1, 1)

        self.verticalLayout_20.addWidget(self.proc_main)

        self.stackedWidget.addWidget(self.proc)

        self.horizontalLayout_13.addWidget(self.stackedWidget)


        self.horizontalLayout_4.addWidget(self.pagesContainer)

        self.prm_page = QFrame(self.content)
        self.prm_page.setObjectName(u"prm_page")
        self.prm_page.setMinimumSize(QSize(0, 0))
        self.prm_page.setMaximumSize(QSize(0, 16777215))
        self.prm_page.setStyleSheet(u"QFrame#extraRightBox{\n"
"background-color: qradialgradient(cx:0, cy:0, radius:1, fx:0.1, fy:0.1, stop:0 rgb(143, 175, 189),  stop:1 rgb(155, 138, 218));\n"
"border-top-left-radius:30px;\n"
"border-top-right-radius:0px;\n"
"border-bottom-right-radius:0px;\n"
"border-bottom-left-radius:30px;\n"
"}")
        self.prm_page.setFrameShape(QFrame.NoFrame)
        self.prm_page.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.prm_page)
        self.verticalLayout_5.setSpacing(34)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 30, 0, 30)
        self.Device_Set = QFrame(self.prm_page)
        self.Device_Set.setObjectName(u"Device_Set")
        self.Device_Set.setMinimumSize(QSize(200, 90))
        self.Device_Set.setMaximumSize(QSize(200, 90))
        self.Device_Set.setStyleSheet(u"QFrame#Device_Set{\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:12px;\n"
"}")
        self.Device_Set.setFrameShape(QFrame.StyledPanel)
        self.Device_Set.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.Device_Set)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.pushButton_6 = QPushButton(self.Device_Set)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setMinimumSize(QSize(0, 30))
        self.pushButton_6.setMaximumSize(QSize(16777215, 30))
        self.pushButton_6.setFont(font7)
        self.pushButton_6.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 10px solid transparent;\n"
"\n"
"text-align: left;\n"
"padding-left: 30px;\n"
"padding-bottom: 2px;\n"
"color: rgba(0, 0, 0, 199);\n"
"}")
        icon14 = QIcon()
        icon14.addFile(u":/icons_v2/images/icons_v2/apple.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_6.setIcon(icon14)

        self.verticalLayout_12.addWidget(self.pushButton_6)

        self.device_box = QComboBox(self.Device_Set)
        self.device_box.addItem("")
        self.device_box.addItem("")
        self.device_box.setObjectName(u"device_box")
        self.device_box.setMinimumSize(QSize(170, 20))
        self.device_box.setMaximumSize(QSize(170, 20))
        font14 = QFont()
        font14.setFamilies([u"Arial"])
        font14.setPointSize(12)
        font14.setBold(False)
        self.device_box.setFont(font14)
        self.device_box.setStyleSheet(u"QComboBox {\n"
"            background-color: rgba(255,255,255,90);\n"
"			color: rgba(0, 0, 0, 200);\n"
"\n"
"            border: 1px solid lightgray;\n"
"            border-radius: 10px;\n"
"            padding-left: 15px;\n"
"        }\n"
"        \n"
"        QComboBox:on {\n"
"            border: 1px solid #63acfb;\n"
"        }\n"
"\n"
"        QComboBox::drop-down {\n"
"            width: 22px;\n"
"            border-left: 1px solid lightgray;\n"
"            border-top-right-radius: 15px;\n"
"            border-bottom-right-radius: 15px;\n"
"        }\n"
"        \n"
"        QComboBox::drop-down:on {\n"
"            border-left: 1px solid #63acfb;\n"
"        }\n"
"\n"
"        QComboBox::down-arrow {\n"
"            width: 16px;\n"
"            height: 16px;\n"
"            image: url(:/icons_v2/images/icons_v2/box_down.png);\n"
"        }\n"
"\n"
"        QComboBox::down-arrow:on {\n"
"            image: url(:/icons_v2/images/icons_v2/box_up.png);\n"
"        }\n"
"\n"
"        QComboBox QAbstractIt"
                        "emView {\n"
"            border: none;\n"
"            outline: none;\n"
"			padding: 10px;\n"
"            background-color: rgb(223, 188, 220);\n"
"        }\n"
"\n"
"\n"
"        QComboBox QScrollBar:vertical {\n"
"            width: 2px;\n"
"           background-color: rgba(255,255,255,150);\n"
"        }\n"
"\n"
"        QComboBox QScrollBar::handle:vertical {\n"
"            background-color: rgba(255,255,255,90);\n"
"        }")

        self.verticalLayout_12.addWidget(self.device_box)


        self.verticalLayout_5.addWidget(self.Device_Set)

        self.Sample_Set = QFrame(self.prm_page)
        self.Sample_Set.setObjectName(u"Sample_Set")
        self.Sample_Set.setMinimumSize(QSize(200, 90))
        self.Sample_Set.setMaximumSize(QSize(200, 90))
        font15 = QFont()
        font15.setPointSize(12)
        font15.setBold(True)
        self.Sample_Set.setFont(font15)
        self.Sample_Set.setStyleSheet(u"\n"
"QFrame#Sample_Set{\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:12px;\n"
"}")
        self.Sample_Set.setFrameShape(QFrame.StyledPanel)
        self.Sample_Set.setFrameShadow(QFrame.Raised)
        self.gridLayout_7 = QGridLayout(self.Sample_Set)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.pushButton_7 = QPushButton(self.Sample_Set)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setMinimumSize(QSize(0, 30))
        self.pushButton_7.setMaximumSize(QSize(16777215, 30))
        self.pushButton_7.setFont(font7)
        self.pushButton_7.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 10px solid transparent;\n"
"\n"
"text-align: left;\n"
"padding-left: 30px;\n"
"padding-bottom: 2px;\n"
"color: rgba(0, 0, 0, 199);\n"
"}")
        icon15 = QIcon()
        icon15.addFile(u":/icons_v2/images/icons_v2/score.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_7.setIcon(icon15)
        self.pushButton_7.setIconSize(QSize(20, 20))

        self.gridLayout_7.addWidget(self.pushButton_7, 0, 0, 1, 2)

        self.sample_ft_spinbox = QSpinBox(self.Sample_Set)
        self.sample_ft_spinbox.setObjectName(u"sample_ft_spinbox")
        self.sample_ft_spinbox.setMinimumSize(QSize(0, 20))
        self.sample_ft_spinbox.setMaximumSize(QSize(16777215, 20))
        font16 = QFont()
        font16.setFamilies([u"Arial"])
        font16.setPointSize(12)
        font16.setBold(True)
        font16.setItalic(False)
        self.sample_ft_spinbox.setFont(font16)
        self.sample_ft_spinbox.setStyleSheet(u"QSpinBox {\n"
"border: 0px solid lightgray;\n"
"border-radius: 2px;\n"
"background-color: rgba(255,255,255,90);\n"
"\n"
"}\n"
"        \n"
"QSpinBox::up-button {\n"
"width: 10px;\n"
"height: 9px;\n"
"margin: 0px 3px 0px 0px;\n"
"border-image: url(:/icons_v2/images/icons_v2/box_up.png);\n"
"}\n"
"QSpinBox::up-button:pressed {\n"
"margin-top: 1px;\n"
"}\n"
"            \n"
"QSpinBox::down-button {\n"
"width: 10px;\n"
"height: 9px;\n"
"margin: 0px 3px 0px 0px;\n"
"border-image:url(:/icons_v2/images/icons_v2/box_down.png);\n"
"}\n"
"QSpinBox::down-button:pressed {\n"
"margin-bottom: 1px;\n"
"}")
        self.sample_ft_spinbox.setMinimum(1)
        self.sample_ft_spinbox.setMaximum(150)
        self.sample_ft_spinbox.setValue(6)

        self.gridLayout_7.addWidget(self.sample_ft_spinbox, 1, 0, 1, 1)

        self.sample_ft_slider = QSlider(self.Sample_Set)
        self.sample_ft_slider.setObjectName(u"sample_ft_slider")
        self.sample_ft_slider.setMinimumSize(QSize(0, 20))
        self.sample_ft_slider.setMaximumSize(QSize(16777215, 20))
        self.sample_ft_slider.setFont(font1)
        self.sample_ft_slider.setStyleSheet(u"QSlider::groove:horizontal {\n"
"border: none;\n"
"height: 10px;\n"
"background-color: rgba(255,255,255,90);\n"
"border-radius: 5px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"width: 10px;\n"
"margin: -1px 0px -1px 0px;\n"
"border-radius: 3px;\n"
"background-color: white;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #59969b, stop:1 #04e7fa);\n"
"border-radius: 5px;\n"
"}")
        self.sample_ft_slider.setMinimum(1)
        self.sample_ft_slider.setMaximum(150)
        self.sample_ft_slider.setValue(6)
        self.sample_ft_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_7.addWidget(self.sample_ft_slider, 1, 1, 1, 1)


        self.verticalLayout_5.addWidget(self.Sample_Set)

        self.Model_Set = QFrame(self.prm_page)
        self.Model_Set.setObjectName(u"Model_Set")
        self.Model_Set.setMinimumSize(QSize(200, 90))
        self.Model_Set.setMaximumSize(QSize(200, 90))
        self.Model_Set.setStyleSheet(u"QFrame#Model_Set{\n"
"border:2px solid rgb(255, 255, 255);\n"
"border-radius:12px;\n"
"}\n"
"")
        self.Model_Set.setFrameShape(QFrame.StyledPanel)
        self.Model_Set.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.Model_Set)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.pushButton_8 = QPushButton(self.Model_Set)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setMinimumSize(QSize(0, 30))
        self.pushButton_8.setMaximumSize(QSize(16777215, 30))
        self.pushButton_8.setFont(font7)
        self.pushButton_8.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 10px solid transparent;\n"
"\n"
"text-align: left;\n"
"padding-left: 30px;\n"
"padding-bottom: 2px;\n"
"color: rgba(0, 0, 0, 199);\n"
"\n"
"}")
        icon16 = QIcon()
        icon16.addFile(u":/icons_v2/images/icons_v2/motion-sensor.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_8.setIcon(icon16)
        self.pushButton_8.setIconSize(QSize(20, 20))

        self.verticalLayout_14.addWidget(self.pushButton_8)

        self.model_box = QComboBox(self.Model_Set)
        self.model_box.addItem("")
        self.model_box.addItem("")
        self.model_box.setObjectName(u"model_box")
        self.model_box.setMinimumSize(QSize(170, 20))
        self.model_box.setMaximumSize(QSize(170, 20))
        font17 = QFont()
        font17.setFamilies([u"Arial"])
        font17.setPointSize(12)
        self.model_box.setFont(font17)
        self.model_box.setStyleSheet(u"QComboBox {\n"
"            background-color: rgba(255,255,255,90);\n"
"			color: rgba(0, 0, 0, 200);\n"
"            border: 1px solid lightgray;\n"
"            border-radius: 10px;\n"
"            padding-left: 15px;\n"
"        }\n"
"        \n"
"        QComboBox:on {\n"
"            border: 1px solid #63acfb;\n"
"        }\n"
"\n"
"        QComboBox::drop-down {\n"
"            width: 22px;\n"
"            border-left: 1px solid lightgray;\n"
"            border-top-right-radius: 15px;\n"
"            border-bottom-right-radius: 15px;\n"
"        }\n"
"        \n"
"        QComboBox::drop-down:on {\n"
"            border-left: 1px solid #63acfb;\n"
"        }\n"
"\n"
"        QComboBox::down-arrow {\n"
"            width: 16px;\n"
"            height: 16px;\n"
"            image: url(:/icons_v2/images/icons_v2/box_down.png);\n"
"        }\n"
"\n"
"        QComboBox::down-arrow:on {\n"
"            image: url(:/icons_v2/images/icons_v2/box_up.png);\n"
"        }\n"
"\n"
"        QComboBox QAbstractItemVie"
                        "w {\n"
"            border: none;\n"
"            outline: none;\n"
"			padding: 10px;\n"
"            background-color: rgb(223, 188, 220);\n"
"        }\n"
"\n"
"\n"
"        QComboBox QScrollBar:vertical {\n"
"            width: 2px;\n"
"           background-color: rgba(255,255,255,150);\n"
"        }\n"
"\n"
"        QComboBox QScrollBar::handle:vertical {\n"
"            background-color: rgba(255,255,255,90);\n"
"        }")

        self.verticalLayout_14.addWidget(self.model_box)


        self.verticalLayout_5.addWidget(self.Model_Set)

        self.Thres_Set = QFrame(self.prm_page)
        self.Thres_Set.setObjectName(u"Thres_Set")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(200)
        sizePolicy4.setVerticalStretch(90)
        sizePolicy4.setHeightForWidth(self.Thres_Set.sizePolicy().hasHeightForWidth())
        self.Thres_Set.setSizePolicy(sizePolicy4)
        self.Thres_Set.setMinimumSize(QSize(200, 90))
        self.Thres_Set.setMaximumSize(QSize(200, 90))
        self.Thres_Set.setStyleSheet(u"border:2px solid rgb(255, 255, 255);\n"
"border-radius:12px;")
        self.Thres_Set.setFrameShape(QFrame.StyledPanel)
        self.Thres_Set.setFrameShadow(QFrame.Raised)
        self.gridLayout_8 = QGridLayout(self.Thres_Set)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.thresh_slider = QSlider(self.Thres_Set)
        self.thresh_slider.setObjectName(u"thresh_slider")
        self.thresh_slider.setFont(font1)
        self.thresh_slider.setStyleSheet(u"QSlider::groove:horizontal {\n"
"border: none;\n"
"height: 10px;\n"
"background-color: rgba(255,255,255,90);\n"
"border-radius: 5px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"width: 10px;\n"
"margin: -1px 0px -1px 0px;\n"
"border-radius: 3px;\n"
"background-color: white;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #59969b, stop:1 #04e7fa);\n"
"border-radius: 5px;\n"
"}")
        self.thresh_slider.setMinimum(10)
        self.thresh_slider.setMaximum(50)
        self.thresh_slider.setSingleStep(1)
        self.thresh_slider.setValue(20)
        self.thresh_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_8.addWidget(self.thresh_slider, 1, 1, 1, 1)

        self.thresh_spinbox = QDoubleSpinBox(self.Thres_Set)
        self.thresh_spinbox.setObjectName(u"thresh_spinbox")
        font18 = QFont()
        font18.setFamilies([u"Arial"])
        font18.setPointSize(12)
        font18.setBold(True)
        self.thresh_spinbox.setFont(font18)
        self.thresh_spinbox.setStyleSheet(u"QDoubleSpinBox {\n"
"border: 0px solid lightgray;\n"
"border-radius: 2px;\n"
"background-color: rgba(255,255,255,90);\n"
"\n"
"}\n"
"        \n"
"QDoubleSpinBox::up-button {\n"
"width: 10px;\n"
"height: 9px;\n"
"margin: 0px 3px 0px 0px;\n"
"border-image: url(:/icons_v2/images/icons_v2/box_up.png);\n"
"}\n"
"QDoubleSpinBox::up-button:pressed {\n"
"margin-top: 1px;\n"
"}\n"
"            \n"
"QDoubleSpinBox::down-button {\n"
"width: 10px;\n"
"height: 9px;\n"
"margin: 0px 3px 0px 0px;\n"
"border-image:url(:/icons_v2/images/icons_v2/box_down.png);\n"
"}\n"
"QDoubleSpinBox::down-button:pressed {\n"
"margin-bottom: 1px;\n"
"}")
        self.thresh_spinbox.setMinimum(0.100000000000000)
        self.thresh_spinbox.setMaximum(0.500000000000000)
        self.thresh_spinbox.setSingleStep(0.010000000000000)
        self.thresh_spinbox.setValue(0.200000000000000)

        self.gridLayout_8.addWidget(self.thresh_spinbox, 1, 0, 1, 1)

        self.pushButton = QPushButton(self.Thres_Set)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setFont(font7)
        self.pushButton.setStyleSheet(u"QPushButton{\n"
"background-repeat: no-repeat;\n"
"background-position: left center;\n"
"border: none;\n"
"border-left: 10px solid transparent;\n"
"\n"
"text-align: left;\n"
"padding-left: 30px;\n"
"padding-bottom: 2px;\n"
"color: rgba(0, 0, 0, 199);\n"
"\n"
"}")
        icon17 = QIcon()
        icon17.addFile(u":/icons_v2/images/icons_v2/face-scanner.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton.setIcon(icon17)

        self.gridLayout_8.addWidget(self.pushButton, 0, 0, 1, 2)


        self.verticalLayout_5.addWidget(self.Thres_Set)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)


        self.horizontalLayout_4.addWidget(self.prm_page)


        self.verticalLayout_6.addWidget(self.content)


        self.verticalLayout_2.addWidget(self.contentBottom)


        self.appLayout.addWidget(self.contentBox)


        self.gridLayout_5.addWidget(self.Main_QF, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.LittleAntP2)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.ToggleBotton.setText(QCoreApplication.translate("MainWindow", u"         Hide", None))
        self.btn_proc.setText(QCoreApplication.translate("MainWindow", u"         Process", None))
        self.btn_reg.setText(QCoreApplication.translate("MainWindow", u"        Register", None))
        self.btn_mag.setText(QCoreApplication.translate("MainWindow", u"         Manager", None))
        self.btn_exit.setText(QCoreApplication.translate("MainWindow", u"          Exit", None))
#if QT_CONFIG(tooltip)
        self.settings_button.setToolTip(QCoreApplication.translate("MainWindow", u"Settings", None))
#endif // QT_CONFIG(tooltip)
        self.settings_button.setText("")
#if QT_CONFIG(tooltip)
        self.min_sf.setToolTip(QCoreApplication.translate("MainWindow", u"Minimize", None))
#endif // QT_CONFIG(tooltip)
        self.min_sf.setText("")
#if QT_CONFIG(tooltip)
        self.max_sf.setToolTip(QCoreApplication.translate("MainWindow", u"Maximize", None))
#endif // QT_CONFIG(tooltip)
        self.max_sf.setText("")
#if QT_CONFIG(tooltip)
        self.close_button.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.close_button.setText("")
        self.mag_nameedit_button.setText(QCoreApplication.translate("MainWindow", u"\u786e\u8ba4\u4fee\u6539ID", None))
        self.mag_delete_button.setText(QCoreApplication.translate("MainWindow", u"\u786e\u8ba4\u5220\u9664", None))
        self.mag_grly_img_show.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u603b\u6ce8\u518c\u6570:", None))
        self.reg_show_main_img.setText("")
        self.reg_show_crop_img.setText("")
        self.reg_processd_box.setItemText(0, QCoreApplication.translate("MainWindow", u"\u8bf7\u9009\u62e9\u6ce8\u518c\u76ee\u6807", None))

        self.reg_to_makesure_reg.setText(QCoreApplication.translate("MainWindow", u"\u786e\u8ba4\u6ce8\u518c", None))
        self.reg_file_process.setText(QCoreApplication.translate("MainWindow", u"\u786e\u8ba4\u5f55\u5165\u56fe\u50cf", None))
        self.pushButton_2.setText("")
        self.reg_file_open.setText("")
        self.reg_file_lineEdit.setPlaceholderText("")
        self.det_pano_img.setText("")
        self.proc_run_button.setText("")
        self.proc_stop_button.setText("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Source From", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Matching Info", None))
        self.save_csv_checkbox.setText(QCoreApplication.translate("MainWindow", u"Save CSV", None))
        self.process_file_button.setText("")
        self.process_file_edit.setText(QCoreApplication.translate("MainWindow", u"  \u8bf7\u9009\u62e9media\u6587\u4ef6", None))
        self.process_file_edit.setPlaceholderText("")
        self.process_dir_button.setText("")
        self.istrack_checkbox.setText(QCoreApplication.translate("MainWindow", u"Is Track", None))
        self.save_media_checkbox.setText(QCoreApplication.translate("MainWindow", u"Save Media", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"OR", None))
        self.process_dir_edit.setText(QCoreApplication.translate("MainWindow", u"  \u8bf7\u9009\u62e9\u6279\u91cf\u5904\u7406media\u6587\u4ef6\u5939", None))
        self.process_dir_edit.setPlaceholderText("")
        self.match_show_img.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"ID: ", None))
        self.match_show_id.setText("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"status:", None))
        self.match_show_status.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Dist:", None))
        self.match_show_dist.setText("")
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"      Device", None))
        self.device_box.setItemText(0, QCoreApplication.translate("MainWindow", u"CPU", None))
        self.device_box.setItemText(1, QCoreApplication.translate("MainWindow", u"GPU", None))

        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"     SampleFt", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"Track Method", None))
        self.model_box.setItemText(0, QCoreApplication.translate("MainWindow", u"BotSort", None))
        self.model_box.setItemText(1, QCoreApplication.translate("MainWindow", u"ByteTrack", None))

        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"  Match Thresh", None))
    # retranslateUi

