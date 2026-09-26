# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
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
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(1280, 720)
        Dialog.setMinimumSize(QSize(1280, 720))
        Dialog.setMaximumSize(QSize(1280, 720))
        font = QFont()
        font.setFamilies([u"HarmonyOS Sans SC"])
        font.setPointSize(14)
        Dialog.setFont(font)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 5, 10, 5)
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 50))
        font1 = QFont()
        font1.setFamilies([u"\u5b8b\u4f53"])
        font1.setPointSize(14)
        font1.setBold(False)
        self.widget.setFont(font1)
        self.widget.setStyleSheet(u"background-color: rgb(245, 245, 245);")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(100, 0, 100, 0)
        self.local_service_btn = QPushButton(self.widget)
        self.local_service_btn.setObjectName(u"local_service_btn")
        self.local_service_btn.setMinimumSize(QSize(200, 40))
        self.local_service_btn.setMaximumSize(QSize(200, 40))
        font2 = QFont()
        font2.setFamilies([u"HarmonyOS Sans SC"])
        font2.setBold(False)
        font2.setItalic(False)
        self.local_service_btn.setFont(font2)
        self.local_service_btn.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"font: 26px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"font: 26px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout.addWidget(self.local_service_btn)

        self.siliconflow_service_btn = QPushButton(self.widget)
        self.siliconflow_service_btn.setObjectName(u"siliconflow_service_btn")
        self.siliconflow_service_btn.setMinimumSize(QSize(200, 40))
        self.siliconflow_service_btn.setMaximumSize(QSize(120, 40))
        self.siliconflow_service_btn.setFont(font2)
        self.siliconflow_service_btn.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"font: 26px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"font: 26px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout.addWidget(self.siliconflow_service_btn)


        self.verticalLayout.addWidget(self.widget)

        self.widget_4 = QWidget(Dialog)
        self.widget_4.setObjectName(u"widget_4")
        self.widget_4.setMinimumSize(QSize(50, 70))
        self.widget_4.setMaximumSize(QSize(16777215, 70))
        font3 = QFont()
        font3.setFamilies([u"\u5b8b\u4f53"])
        font3.setPointSize(16)
        font3.setBold(False)
        self.widget_4.setFont(font3)
        self.widget_4.setStyleSheet(u"background-color: rgb(245, 245, 245);")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_13 = QLabel(self.widget_4)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(0, 50))
        self.label_13.setMaximumSize(QSize(16777215, 50))
        self.label_13.setFont(font2)
        self.label_13.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_13)

        self.check_wake = QCheckBox(self.widget_4)
        self.check_wake.setObjectName(u"check_wake")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.check_wake.sizePolicy().hasHeightForWidth())
        self.check_wake.setSizePolicy(sizePolicy)
        self.check_wake.setMinimumSize(QSize(300, 50))
        self.check_wake.setMaximumSize(QSize(16777215, 50))
        font4 = QFont()
        font4.setHintingPreference(QFont.PreferNoHinting)
        self.check_wake.setFont(font4)
        self.check_wake.setStyleSheet(u"")
        self.check_wake.setIconSize(QSize(16, 16))
        self.check_wake.setCheckable(True)
        self.check_wake.setChecked(False)

        self.horizontalLayout_2.addWidget(self.check_wake)

        self.url_qlabel = QLabel(self.widget_4)
        self.url_qlabel.setObjectName(u"url_qlabel")

        self.horizontalLayout_2.addWidget(self.url_qlabel)

        self.horizontalLayout_2.setStretch(2, 1)

        self.verticalLayout.addWidget(self.widget_4)

        self.stackedWidget = QStackedWidget(Dialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setFont(font1)
        self.local_service_page = QWidget()
        self.local_service_page.setObjectName(u"local_service_page")
        self.verticalLayout_2 = QVBoxLayout(self.local_service_page)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, 5, 9, -1)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setVerticalSpacing(40)
        self.formLayout.setContentsMargins(0, 20, -1, 0)
        self.label_4 = QLabel(self.local_service_page)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font2)
        self.label_4.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.local_llm = QLineEdit(self.local_service_page)
        self.local_llm.setObjectName(u"local_llm")
        self.local_llm.setFont(font2)
        self.local_llm.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.local_llm)

        self.label_2 = QLabel(self.local_service_page)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font2)
        self.label_2.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.local_vl = QLineEdit(self.local_service_page)
        self.local_vl.setObjectName(u"local_vl")
        self.local_vl.setFont(font2)
        self.local_vl.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.local_vl)

        self.label_14 = QLabel(self.local_service_page)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.local_speech_rec = QLineEdit(self.local_service_page)
        self.local_speech_rec.setObjectName(u"local_speech_rec")
        self.local_speech_rec.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.local_speech_rec)

        self.label_7 = QLabel(self.local_service_page)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font2)
        self.label_7.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.local_api_key = QLineEdit(self.local_service_page)
        self.local_api_key.setObjectName(u"local_api_key")
        self.local_api_key.setFont(font2)
        self.local_api_key.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")
        self.local_api_key.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.local_api_key)


        self.verticalLayout_2.addLayout(self.formLayout)

        self.stackedWidget.addWidget(self.local_service_page)
        self.siliconflow_page = QWidget()
        self.siliconflow_page.setObjectName(u"siliconflow_page")
        self.verticalLayout_4 = QVBoxLayout(self.siliconflow_page)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(9, 5, -1, 9)
        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setHorizontalSpacing(0)
        self.formLayout_3.setVerticalSpacing(20)
        self.formLayout_3.setContentsMargins(0, 20, -1, 10)
        self.label_11 = QLabel(self.siliconflow_page)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font2)
        self.label_11.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.siliconflow_llm_name = QLineEdit(self.siliconflow_page)
        self.siliconflow_llm_name.setObjectName(u"siliconflow_llm_name")
        self.siliconflow_llm_name.setFont(font2)
        self.siliconflow_llm_name.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.siliconflow_llm_name)

        self.label_12 = QLabel(self.siliconflow_page)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setFont(font2)
        self.label_12.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.siliconflow_vl = QLineEdit(self.siliconflow_page)
        self.siliconflow_vl.setObjectName(u"siliconflow_vl")
        self.siliconflow_vl.setFont(font2)
        self.siliconflow_vl.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.siliconflow_vl)

        self.label = QLabel(self.siliconflow_page)
        self.label.setObjectName(u"label")
        self.label.setFont(font2)
        self.label.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label)

        self.siliconflow_speech_rec = QLineEdit(self.siliconflow_page)
        self.siliconflow_speech_rec.setObjectName(u"siliconflow_speech_rec")
        self.siliconflow_speech_rec.setFont(font2)
        self.siliconflow_speech_rec.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.siliconflow_speech_rec)

        self.label_3 = QLabel(self.siliconflow_page)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.siliconflow_speech_syn = QLineEdit(self.siliconflow_page)
        self.siliconflow_speech_syn.setObjectName(u"siliconflow_speech_syn")
        self.siliconflow_speech_syn.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.FieldRole, self.siliconflow_speech_syn)

        self.label_5 = QLabel(self.siliconflow_page)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font2)
        self.label_5.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_3.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.siliconflow_api_key = QLineEdit(self.siliconflow_page)
        self.siliconflow_api_key.setObjectName(u"siliconflow_api_key")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.siliconflow_api_key.sizePolicy().hasHeightForWidth())
        self.siliconflow_api_key.setSizePolicy(sizePolicy1)
        self.siliconflow_api_key.setFont(font2)
        self.siliconflow_api_key.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")
        self.siliconflow_api_key.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout_3.setWidget(4, QFormLayout.ItemRole.FieldRole, self.siliconflow_api_key)


        self.verticalLayout_4.addLayout(self.formLayout_3)

        self.stackedWidget.addWidget(self.siliconflow_page)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.widget1 = QWidget(Dialog)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setFont(font1)
        self.verticalLayout_3 = QVBoxLayout(self.widget1)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(9, 0, -1, 0)
        self.line = QFrame(self.widget1)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line)

        self.mqttsettings_label = QLabel(self.widget1)
        self.mqttsettings_label.setObjectName(u"mqttsettings_label")
        self.mqttsettings_label.setMinimumSize(QSize(0, 50))
        self.mqttsettings_label.setMaximumSize(QSize(16777215, 50))
        self.mqttsettings_label.setFont(font2)
        self.mqttsettings_label.setStyleSheet(u"font: 30px \"HarmonyOS Sans SC\";")
        self.mqttsettings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.mqttsettings_label)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setVerticalSpacing(10)
        self.formLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.label_17 = QLabel(self.widget1)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setFont(font2)
        self.label_17.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_17)

        self.mqtt_server = QLineEdit(self.widget1)
        self.mqtt_server.setObjectName(u"mqtt_server")
        self.mqtt_server.setFont(font2)
        self.mqtt_server.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.mqtt_server)

        self.label_9 = QLabel(self.widget1)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font2)
        self.label_9.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.mqtt_port = QLineEdit(self.widget1)
        self.mqtt_port.setObjectName(u"mqtt_port")
        self.mqtt_port.setFont(font2)
        self.mqtt_port.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.mqtt_port)

        self.label_8 = QLabel(self.widget1)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font2)
        self.label_8.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.mqtt_sub = QLineEdit(self.widget1)
        self.mqtt_sub.setObjectName(u"mqtt_sub")
        self.mqtt_sub.setFont(font2)
        self.mqtt_sub.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mqtt_sub)

        self.label_10 = QLabel(self.widget1)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFont(font2)
        self.label_10.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.mqtt_pub = QLineEdit(self.widget1)
        self.mqtt_pub.setObjectName(u"mqtt_pub")
        self.mqtt_pub.setFont(font2)
        self.mqtt_pub.setStyleSheet(u"font: 20px \"HarmonyOS Sans SC\";")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.mqtt_pub)


        self.verticalLayout_3.addLayout(self.formLayout_2)

        self.widget_2 = QWidget(self.widget1)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(0, 50))
        self.horizontalLayout_3 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setSpacing(50)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(50, -1, 50, -1)
        self.save_btn = QPushButton(self.widget_2)
        self.save_btn.setObjectName(u"save_btn")
        self.save_btn.setMinimumSize(QSize(0, 30))
        self.save_btn.setMaximumSize(QSize(16777215, 50))
        self.save_btn.setFont(font2)
        self.save_btn.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"font: 20px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"font: 20px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout_3.addWidget(self.save_btn)

        self.default_btn = QPushButton(self.widget_2)
        self.default_btn.setObjectName(u"default_btn")
        self.default_btn.setMinimumSize(QSize(0, 30))
        self.default_btn.setMaximumSize(QSize(16777215, 50))
        self.default_btn.setFont(font2)
        self.default_btn.setStyleSheet(u"QPushButton{\n"
"	background-color: rgb(64, 70, 103);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"font: 20px \"HarmonyOS Sans SC\";\n"
"}\n"
"QPushButton:hover{\n"
"	background-color: rgb(117, 122, 146);\n"
"	border-radius: 10px;\n"
"	color: rgb(255, 255, 255);\n"
"font: 20px \"HarmonyOS Sans SC\";\n"
"}")

        self.horizontalLayout_3.addWidget(self.default_btn)


        self.verticalLayout_3.addWidget(self.widget_2)

        self.verticalLayout_3.setStretch(1, 3)
        self.verticalLayout_3.setStretch(2, 3)
        self.verticalLayout_3.setStretch(3, 1)

        self.verticalLayout.addWidget(self.widget1)

        self.verticalLayout.setStretch(2, 3)

        self.retranslateUi(Dialog)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.local_service_btn.setText(QCoreApplication.translate("Dialog", u"\u672c\u5730\u670d\u52a1", None))
        self.siliconflow_service_btn.setText(QCoreApplication.translate("Dialog", u"\u7845\u57fa\u6d41\u52a8", None))
        self.label_13.setText(QCoreApplication.translate("Dialog", u"\u542f\u7528\u5524\u9192\u8bcd", None))
        self.check_wake.setText("")
        self.url_qlabel.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u5bf9\u8bdd\u5927\u6a21\u578b\u540d\u79f0\uff1a", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u591a\u6a21\u6001\u5927\u6a21\u578b\u540d\u79f0\uff1a", None))
        self.label_14.setText(QCoreApplication.translate("Dialog", u"\u8bed\u97f3\u8bc6\u522b\u5927\u6a21\u578b\u540d\u79f0\uff1a", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"API\u79d8\u94a5\uff1a", None))
        self.label_11.setText(QCoreApplication.translate("Dialog", u"\u5bf9\u8bdd\u5927\u6a21\u578b\u540d\u79f0\uff1a", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"\u591a\u6a21\u6001\u5927\u6a21\u578b\u540d\u79f0\uff1a", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u8bed\u97f3\u8bc6\u522b\u5927\u6a21\u578b\u540d\u79f0\uff1a", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u8bed\u97f3\u5408\u6210\u5927\u6a21\u578b\u540d\u79f0\uff1a", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"API\u79d8\u94a5\uff1a", None))
        self.mqttsettings_label.setText(QCoreApplication.translate("Dialog", u"MQTT\u670d\u52a1\u5668\u8bbe\u7f6e", None))
        self.label_17.setText(QCoreApplication.translate("Dialog", u"\u670d\u52a1\u5668\u5730\u5740\uff1a", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"\u7aef\u53e3\u53f7\uff1a", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"\u8ba2\u9605\u8bdd\u9898\uff1a", None))
        self.label_10.setText(QCoreApplication.translate("Dialog", u"\u53d1\u5e03\u8bdd\u9898\uff1a", None))
        self.save_btn.setText(QCoreApplication.translate("Dialog", u"\u4fdd\u5b58\u914d\u7f6e", None))
        self.default_btn.setText(QCoreApplication.translate("Dialog", u"\u6062\u590d\u9ed8\u8ba4\u914d\u7f6e", None))
    # retranslateUi

