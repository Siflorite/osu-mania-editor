import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QLabel, QMessageBox
from PySide6.QtCore import QStringListModel

from PySide6.QtGui import QPixmap
from main_ui import Ui_MainWindow
import os
import zipfile
from zipfile import ZipFile
import json
import math

import osuFunc
import malodyFunc

typeName = ""
FileName = ""
osuFiles=[]
active_osu_file = ""
base_path = ""

title = ""
titleUnicode = ""
artist = ""
artistUnicode = ""
creator = ""
version = ""
bgPic = ""
HP = 0
Keys = 0
OD = 0
bNewFile = True

class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.loadButton.clicked.connect(self.loadButtonClicked)
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.listView_osulist.clicked.connect(self.osulistClicked)
        self.generateButton.clicked.connect(self.generateButtonClicked)
        self.pushButton_mc2osu.clicked.connect(self.ButtonMC2OSUClickeed)
        self.checkBox_bNewFile.clicked.connect(self.checkBoxBNewFileClicked)
        self.lineEdit_title.textChanged.connect(self.lineEditTitleModified)
        self.lineEdit_title_unicode.textChanged.connect(self.lineEditTitleUnicodeModified)
        self.lineEdit_artist.textChanged.connect(self.lineEditArtistModified)
        self.lineEdit_artist_unicode.textChanged.connect(self.lineEditArtistUnicodeModified)
        self.lineEdit_creator.textChanged.connect(self.lineEditCreatorModified)
        self.lineEdit_version.textChanged.connect(self.lineEditVersionModified)
        self.lineEdit_hp.textChanged.connect(self.lineEditHPModified)
        self.lineEdit_od.textChanged.connect(self.lineEditODModified)


    def loadButtonClicked(self):
        fname = QFileDialog.getOpenFileName(self, "打开osu谱面文件或osz压缩文件", '', "Osu Zip Files (*.osz);;Osu Beatmap Files (*.osu)", "Osu Zip Files (*.osz)")
        if(fname[0] == ""):
            return
        global FileName
        FileName = fname[0] # osu or osz file with complete absolute path
        self.lineEdit_file.setText(FileName)

        global typeName
        global osuFiles
        global base_path
        typeName, osuFiles, base_path = osuFunc.loadOsuOrOszFile(FileName)

        if len(osuFiles) > 0:
            model = QStringListModel()
            model.setStringList(osuFiles)
            self.listView_osulist.setModel(model)

    def saveButtonClicked(self):
        global FileName
        global active_osu_file
        global bNewFile
        savedPath = osuFunc.saveOsuOrOszFile(FileName, active_osu_file, bNewFile)
        global typeName
        if typeName == "osz":
            savedPath = osuFunc.saveOszFile(FileName, bNewFile)
        
        dlg = QMessageBox()
        dlg.setWindowTitle("提示")
        dlg.setText("文件已保存至" + savedPath)
        dlg.setStandardButtons(QMessageBox.Yes)
        dlg.exec()
        

    def osulistClicked(self):
        list_index = self.listView_osulist.currentIndex()
        list_model = self.listView_osulist.model()
        global active_osu_file
        if active_osu_file == list_model.itemData(list_index)[0]:
            return
        if not active_osu_file == "":
            osuFunc.saveOsuOrOszFile(FileName, active_osu_file, bNewFile=False)
        active_osu_file = list_model.itemData(list_index)[0]

        global title
        global titleUnicode
        global artist
        global artistUnicode
        global creator
        global version
        global HP
        global Keys
        global OD
        global bgPic

        dataDict = osuFunc.analyzeOsuFile(active_osu_file)
        title = dataDict['Title']
        titleUnicode = dataDict['TitleUnicode']
        artist = dataDict['Artist']
        artistUnicode = dataDict['ArtistUnicode']
        creator = dataDict['Creator']
        version = dataDict['Version']
        HP = dataDict['HP']
        Keys = dataDict['Keys']
        OD = dataDict['OD']
        bgPic = dataDict['Background']

        self.updateLineEdit()
        pixmap_bg = QPixmap(bgPic)
        self.label_bg.setPixmap(pixmap_bg)
        self.label_bg.setScaledContents(True)

    def generateButtonClicked(self):
        global FileName
        oszBasePathDir = os.path.dirname(FileName)
        previewPic = osuFunc.generatePreviewPic(oszBasePathDir, active_osu_file)
        
        pixmap = QPixmap(str(previewPic))
        size = pixmap.size()
        pixmap = pixmap.scaled(size/2)
        self.label_pre = QLabel()
        self.label_pre.setGeometry(0, 0, pixmap.size().width(), pixmap.size().height())
        self.label_pre.setPixmap(pixmap)
        self.label_pre.show()

        dlg = QMessageBox()
        dlg.setWindowTitle("提示")
        dlg.setText("预览图片已保存至" + previewPic)
        dlg.setStandardButtons(QMessageBox.Yes)
        dlg.exec()
    
    def ButtonMC2OSUClickeed(self):
        fname = QFileDialog.getOpenFileNames(self, "打开mc谱面文件或mcz压缩文件", '', "Malody Chart zip Files (*.mcz);;Malody Chart Files (*.mc)", "Malody Chart zip Files (*.mcz)")
        if(fname[0] == []):
            return
        for OriginalFilePath in fname[0]:
            ChartType, savedFilePath, totalErroInfo = malodyFunc.convertMcOrMczFile(OriginalFilePath)
            for item in totalErroInfo:
                dlg = QMessageBox()
                dlg.setWindowTitle("警告")
                dlg.setText(item)
                dlg.setStandardButtons(QMessageBox.Yes)
                dlg.exec()

            newFileType = ".osu" if ChartType == ".mc" else ".osz"
            dlg = QMessageBox()
            dlg.setWindowTitle("提示")
            dlg.setText(newFileType + "文件已保存至" + savedFilePath)
            dlg.setStandardButtons(QMessageBox.Yes)
            dlg.exec()


    def checkBoxBNewFileClicked(self):
        global bNewFile
        bNewFile = self.checkBox_bNewFile.isChecked()
    
    def lineEditTitleModified(self):
        global title
        title = self.lineEdit_title.text()
        changeMiscData("Title", title)
    
    def lineEditTitleUnicodeModified(self):
        global titleUnicode
        titleUnicode = self.lineEdit_title_unicode.text()
        changeMiscData("TitleUnicode", titleUnicode)

    def lineEditArtistModified(self):
        global artist
        artist = self.lineEdit_artist.text()
        changeMiscData("Artist", artist)

    def lineEditArtistUnicodeModified(self):
        global artistUnicode
        artistUnicode = self.lineEdit_artist_unicode.text()
        changeMiscData("ArtistUnicode", artistUnicode)

    def lineEditCreatorModified(self):
        global creator
        creator = self.lineEdit_creator.text()
        changeMiscData("Creator", creator)
    
    def lineEditVersionModified(self):
        global version
        version = self.lineEdit_version.text()
        changeMiscData("Version", version)

    def lineEditHPModified(self):
        global HP
        HP_str = str(self.lineEdit_hp.text())
        HP = osuFunc.clampODHP(HP_str) if osuFunc.clampODHP(HP_str) >= 0 else HP
        changeMiscData("HP", str(HP))

    def lineEditKeysModified(self):
        global Keys
        Keys_str = str(self.lineEdit_keys.text())
        Keys = osuFunc.clampKeys(Keys_str) if osuFunc.clampKeys(Keys_str) > 0 else Keys
        changeMiscData("Keys", str(Keys))

    def lineEditODModified(self):
        global OD
        OD_str = str(self.lineEdit_hp.text())
        OD = osuFunc.clampODHP(OD_str) if osuFunc.clampODHP(OD_str) >= 0 else OD
        changeMiscData("OD", str(OD))

    def updateLineEdit(self):
        global title
        global titleUnicode
        global artist
        global artistUnicode
        global creator
        global version
        global HP
        global Keys
        global OD

        self.lineEdit_title.setText(title)
        self.lineEdit_title_unicode.setText(titleUnicode)
        self.lineEdit_artist.setText(artist)
        self.lineEdit_artist_unicode.setText(artistUnicode)
        self.lineEdit_creator.setText(creator)
        self.lineEdit_version.setText(version)
        if HP - int(HP) == 0:
            HP_str = str(int(HP))
        else:
            HP_str = str(HP)
        self.lineEdit_hp.setText(HP_str)
        self.lineEdit_keys.setText(str(Keys))
        if OD - int(OD) == 0:
            OD_str = str(int(OD))
        else:
            OD_str = str(OD)
        self.lineEdit_od.setText(OD_str)

def changeMiscData(name, val):
    osuFunc.changeModuleMiscData(name, val)

def cleanOsuFile():
    global FileName
    global active_osu_file
    global bNewFile
    if FileName == "": return
    osuFunc.cleanTempOsuFile(FileName, active_osu_file, bNewFile)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    app.aboutToQuit.connect(cleanOsuFile)
    sys.exit(app.exec())