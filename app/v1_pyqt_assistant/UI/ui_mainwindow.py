# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

from resources import static_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1600, 900)
        MainWindow.setMinimumSize(QSize(1600, 900))
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies([u"HarmonyOS Sans SC"])
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setSpacing(0)
        self.leftLayout.setObjectName(u"leftLayout")
        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(0, 60))
        self.widget_2.setMaximumSize(QSize(800, 16777215))
        self.widget_2.setStyleSheet(u"background-color: rgb(236, 239, 246);")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.cameraLabel = QLabel(self.widget_2)
        self.cameraLabel.setObjectName(u"cameraLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cameraLabel.sizePolicy().hasHeightForWidth())
        self.cameraLabel.setSizePolicy(sizePolicy)
        self.cameraLabel.setMaximumSize(QSize(16777215, 60))
        font1 = QFont()
        font1.setFamilies([u"HarmonyOS Sans SC"])
        font1.setBold(False)
        font1.setItalic(False)
        font1.setStyleStrategy(QFont.PreferDefault)
        font1.setHintingPreference(QFont.PreferNoHinting)
        self.cameraLabel.setFont(font1)
        self.cameraLabel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cameraLabel.setStyleSheet(u"	font: 40px \"HarmonyOS Sans SC\";")
        self.cameraLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.cameraLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.leftLayout.addWidget(self.widget_2)

        self.cameraDisplay = QLabel(self.centralwidget)
        self.cameraDisplay.setObjectName(u"cameraDisplay")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cameraDisplay.sizePolicy().hasHeightForWidth())
        self.cameraDisplay.setSizePolicy(sizePolicy1)
        self.cameraDisplay.setMinimumSize(QSize(800, 600))
        self.cameraDisplay.setMaximumSize(QSize(800, 600))
        self.cameraDisplay.setFrameShape(QFrame.Shape.Box)
        self.cameraDisplay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.leftLayout.addWidget(self.cameraDisplay)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer_3)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 90))
        self.widget.setMaximumSize(QSize(800, 9999999))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.openCameraButton = QPushButton(self.widget)
        self.openCameraButton.setObjectName(u"openCameraButton")
        sizePolicy1.setHeightForWidth(self.openCameraButton.sizePolicy().hasHeightForWidth())
        self.openCameraButton.setSizePolicy(sizePolicy1)
        self.openCameraButton.setMinimumSize(QSize(300, 80))
        font2 = QFont()
        font2.setFamilies([u"HarmonyOS Sans SC"])
        font2.setBold(False)
        font2.setItalic(False)
        font2.setHintingPreference(QFont.PreferNoHinting)
        self.openCameraButton.setFont(font2)
        self.openCameraButton.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 30px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 30px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout.addWidget(self.openCameraButton)

        self.closeCameraButton = QPushButton(self.widget)
        self.closeCameraButton.setObjectName(u"closeCameraButton")
        sizePolicy1.setHeightForWidth(self.closeCameraButton.sizePolicy().hasHeightForWidth())
        self.closeCameraButton.setSizePolicy(sizePolicy1)
        self.closeCameraButton.setMinimumSize(QSize(300, 80))
        self.closeCameraButton.setFont(font2)
        self.closeCameraButton.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 30px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 30px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout.addWidget(self.closeCameraButton)


        self.leftLayout.addWidget(self.widget)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer)


        self.mainLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.widget_3 = QWidget(self.centralwidget)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setMinimumSize(QSize(0, 60))
        self.widget_3.setStyleSheet(u"background-color: rgb(236, 239, 246);\n"
"font: 21pt \"HarmonyOS Sans SC\";")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.comboBox = QComboBox(self.widget_3)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        font3 = QFont()
        font3.setFamilies([u"HarmonyOS Sans SC"])
        font3.setBold(False)
        font3.setItalic(False)
        self.comboBox.setFont(font3)
        self.comboBox.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"font: 25px \"HarmonyOS Sans SC\";\n"
"")
        self.comboBox.setMaxVisibleItems(3)

        self.horizontalLayout_4.addWidget(self.comboBox)

        self.voiceLabel = QLabel(self.widget_3)
        self.voiceLabel.setObjectName(u"voiceLabel")
        self.voiceLabel.setFont(font3)
        self.voiceLabel.setStyleSheet(u"	font: 40px \"HarmonyOS Sans SC\";")
        self.voiceLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_4.addWidget(self.voiceLabel)

        self.settingsButton = QPushButton(self.widget_3)
        self.settingsButton.setObjectName(u"settingsButton")
        self.settingsButton.setMinimumSize(QSize(0, 40))
        self.settingsButton.setMaximumSize(QSize(16777215, 40))
        self.settingsButton.setFont(font3)
        self.settingsButton.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 25px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 25px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout_4.addWidget(self.settingsButton)

        self.horizontalLayout_4.setStretch(1, 3)
        self.horizontalLayout_4.setStretch(2, 1)

        self.rightLayout.addWidget(self.widget_3)

        self.chatListWidget = QListWidget(self.centralwidget)
        self.chatListWidget.setObjectName(u"chatListWidget")
        font4 = QFont()
        font4.setFamilies([u"\u5b8b\u4f53"])
        self.chatListWidget.setFont(font4)
        self.chatListWidget.setStyleSheet(u"background-color: rgb(245, 245, 245);")
        self.chatListWidget.setWordWrap(True)

        self.rightLayout.addWidget(self.chatListWidget)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.rightLayout.addItem(self.verticalSpacer_4)

        self.widget_5 = QWidget(self.centralwidget)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setMinimumSize(QSize(300, 100))
        self.horizontalLayout_2 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_2.setSpacing(60)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(60, -1, 60, -1)
        self.speak_button = QPushButton(self.widget_5)
        self.speak_button.setObjectName(u"speak_button")
        self.speak_button.setMinimumSize(QSize(300, 80))
        self.speak_button.setFont(font3)
        self.speak_button.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 30px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 30px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout_2.addWidget(self.speak_button)

        self.end_button = QPushButton(self.widget_5)
        self.end_button.setObjectName(u"end_button")
        self.end_button.setMinimumSize(QSize(300, 80))
        self.end_button.setFont(font3)
        self.end_button.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 30px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"	font: 30px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout_2.addWidget(self.end_button)


        self.rightLayout.addWidget(self.widget_5)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.rightLayout.addItem(self.verticalSpacer_5)

        self.rightLayout.setStretch(1, 5)
        self.rightLayout.setStretch(3, 1)

        self.mainLayout.addLayout(self.rightLayout)

        self.mainLayout.setStretch(0, 1)
        self.mainLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Camera and Voice App", None))
        self.cameraLabel.setText(QCoreApplication.translate("MainWindow", u"\u6444\u50cf\u5934\u663e\u793a\u533a", None))
        self.openCameraButton.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u6444\u50cf\u5934", None))
        self.closeCameraButton.setText(QCoreApplication.translate("MainWindow", u"\u5173\u95ed\u6444\u50cf\u5934", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"\u672c\u5730\u670d\u52a1", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"\u7845\u57fa\u6d41\u52a8", None))

        self.voiceLabel.setText(QCoreApplication.translate("MainWindow", u"\u8bed\u97f3\u5bf9\u8bdd\u533a", None))
        self.settingsButton.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
        self.speak_button.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u5f55\u97f3", None))
        self.end_button.setText(QCoreApplication.translate("MainWindow", u"\u4e2d\u6b62\u5bf9\u8bdd", None))
    # retranslateUi

