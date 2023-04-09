# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QLineEdit,
    QListView, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.loadButton = QPushButton(self.centralwidget)
        self.loadButton.setObjectName(u"loadButton")
        self.loadButton.setGeometry(QRect(20, 10, 75, 24))
        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setGeometry(QRect(110, 10, 75, 24))
        self.label_title = QLabel(self.centralwidget)
        self.label_title.setObjectName(u"label_title")
        self.label_title.setGeometry(QRect(40, 70, 54, 16))
        self.lineEdit_title = QLineEdit(self.centralwidget)
        self.lineEdit_title.setObjectName(u"lineEdit_title")
        self.lineEdit_title.setGeometry(QRect(110, 70, 231, 20))
        self.lineEdit_title_unicode = QLineEdit(self.centralwidget)
        self.lineEdit_title_unicode.setObjectName(u"lineEdit_title_unicode")
        self.lineEdit_title_unicode.setGeometry(QRect(110, 110, 231, 20))
        self.label_title_unicode = QLabel(self.centralwidget)
        self.label_title_unicode.setObjectName(u"label_title_unicode")
        self.label_title_unicode.setGeometry(QRect(13, 110, 81, 20))
        self.lineEdit_artist = QLineEdit(self.centralwidget)
        self.lineEdit_artist.setObjectName(u"lineEdit_artist")
        self.lineEdit_artist.setGeometry(QRect(110, 150, 231, 20))
        self.label_artist = QLabel(self.centralwidget)
        self.label_artist.setObjectName(u"label_artist")
        self.label_artist.setGeometry(QRect(40, 150, 54, 16))
        self.lineEdit_file = QLineEdit(self.centralwidget)
        self.lineEdit_file.setObjectName(u"lineEdit_file")
        self.lineEdit_file.setGeometry(QRect(220, 10, 511, 20))
        self.listView_osulist = QListView(self.centralwidget)
        self.listView_osulist.setObjectName(u"listView_osulist")
        self.listView_osulist.setGeometry(QRect(370, 70, 381, 311))
        self.label_artist_unicode = QLabel(self.centralwidget)
        self.label_artist_unicode.setObjectName(u"label_artist_unicode")
        self.label_artist_unicode.setGeometry(QRect(10, 190, 91, 16))
        self.lineEdit_artist_unicode = QLineEdit(self.centralwidget)
        self.lineEdit_artist_unicode.setObjectName(u"lineEdit_artist_unicode")
        self.lineEdit_artist_unicode.setGeometry(QRect(110, 190, 231, 20))
        self.lineEdit_creator = QLineEdit(self.centralwidget)
        self.lineEdit_creator.setObjectName(u"lineEdit_creator")
        self.lineEdit_creator.setGeometry(QRect(110, 230, 231, 20))
        self.label_creator = QLabel(self.centralwidget)
        self.label_creator.setObjectName(u"label_creator")
        self.label_creator.setGeometry(QRect(30, 230, 91, 16))
        self.lineEdit_version = QLineEdit(self.centralwidget)
        self.lineEdit_version.setObjectName(u"lineEdit_version")
        self.lineEdit_version.setGeometry(QRect(110, 270, 231, 20))
        self.label_version = QLabel(self.centralwidget)
        self.label_version.setObjectName(u"label_version")
        self.label_version.setGeometry(QRect(30, 270, 91, 16))
        self.label_hp = QLabel(self.centralwidget)
        self.label_hp.setObjectName(u"label_hp")
        self.label_hp.setGeometry(QRect(20, 330, 54, 16))
        self.lineEdit_hp = QLineEdit(self.centralwidget)
        self.lineEdit_hp.setObjectName(u"lineEdit_hp")
        self.lineEdit_hp.setGeometry(QRect(50, 330, 71, 20))
        self.lineEdit_keys = QLineEdit(self.centralwidget)
        self.lineEdit_keys.setObjectName(u"lineEdit_keys")
        self.lineEdit_keys.setEnabled(False)
        self.lineEdit_keys.setGeometry(QRect(170, 330, 71, 20))
        self.label_keys = QLabel(self.centralwidget)
        self.label_keys.setObjectName(u"label_keys")
        self.label_keys.setGeometry(QRect(140, 330, 54, 16))
        self.lineEdit_od = QLineEdit(self.centralwidget)
        self.lineEdit_od.setObjectName(u"lineEdit_od")
        self.lineEdit_od.setGeometry(QRect(280, 330, 71, 20))
        self.label_od = QLabel(self.centralwidget)
        self.label_od.setObjectName(u"label_od")
        self.label_od.setGeometry(QRect(250, 330, 54, 16))
        self.label_bg = QLabel(self.centralwidget)
        self.label_bg.setObjectName(u"label_bg")
        self.label_bg.setGeometry(QRect(30, 370, 321, 201))
        self.generateButton = QPushButton(self.centralwidget)
        self.generateButton.setObjectName(u"generateButton")
        self.generateButton.setGeometry(QRect(370, 390, 75, 24))
        self.checkBox_bNewFile = QCheckBox(self.centralwidget)
        self.checkBox_bNewFile.setObjectName(u"checkBox_bNewFile")
        self.checkBox_bNewFile.setGeometry(QRect(380, 530, 91, 20))
        self.checkBox_bNewFile.setChecked(True)
        self.pushButton_mc2osu = QPushButton(self.centralwidget)
        self.pushButton_mc2osu.setObjectName(u"pushButton_mc2osu")
        self.pushButton_mc2osu.setGeometry(QRect(370, 460, 131, 24))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"osu!mania chart simple editor", None))
        self.loadButton.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.saveButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.label_title.setText(QCoreApplication.translate("MainWindow", u"Title", None))
        self.label_title_unicode.setText(QCoreApplication.translate("MainWindow", u"Title(Unicode)", None))
        self.label_artist.setText(QCoreApplication.translate("MainWindow", u"Artist", None))
        self.label_artist_unicode.setText(QCoreApplication.translate("MainWindow", u"Artist(Unicode)", None))
        self.label_creator.setText(QCoreApplication.translate("MainWindow", u"Creator", None))
        self.label_version.setText(QCoreApplication.translate("MainWindow", u"Version", None))
        self.label_hp.setText(QCoreApplication.translate("MainWindow", u"HP", None))
        self.label_keys.setText(QCoreApplication.translate("MainWindow", u"Keys", None))
        self.label_od.setText(QCoreApplication.translate("MainWindow", u"OD", None))
        self.label_bg.setText("")
        self.generateButton.setText(QCoreApplication.translate("MainWindow", u"\u751f\u6210\u9884\u89c8", None))
        self.checkBox_bNewFile.setText(QCoreApplication.translate("MainWindow", u"\u50a8\u5b58\u4e3a\u65b0\u6587\u4ef6", None))
        self.pushButton_mc2osu.setText(QCoreApplication.translate("MainWindow", u".mc/.mcz\u8f6c.osu/.osz", None))
    # retranslateUi

