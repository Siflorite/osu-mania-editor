import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QLabel
from PySide6.QtCore import QStringListModel

from PySide6.QtGui import QPixmap
from main_ui import Ui_MainWindow
import os
import zipfile

from reamber.osu.OsuMap import OsuMap
from reamber.algorithms.playField import PlayField
from reamber.algorithms.playField.parts import PFDrawColumnLines, PFDrawBeatLines, PFDrawBpm, PFDrawSv, PFDrawNotes

typeName = ""
osuFiles=[]
active_osu_file = ""
base_path = ""

bWriteEvents = False
bWriteTimingPoints = False
bWriteNotes = False
misc=[] #osu文件开始时的General,Editor,Metadata,Difficulty
events=[] #osu文件关于背景动画和声音sample的信息
timingPoints=[] #osu文件的Timing
hitObjects=[] #osu文件的HitObjects
newHitObjects=[]

title = ""
titleUnicode = ""
artist = ""
artistUnicode = ""
creator = ""
version = ""
HP = ""
Keys = ""
OD = ""

class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.loadButton.clicked.connect(self.loadButtonClicked)
        self.listView_osulist.clicked.connect(self.osulistClicked)
        self.generateButton.clicked.connect(self.generateButtonClicked)

    def loadButtonClicked(self):
        fname = QFileDialog.getOpenFileName(self, "打开osu铺面文件或osz压缩文件", '', "Osu zip files (*.osz);;Osu Beatmap Files (*.osu)", "Osu zip files (*.osz)")
        self.lineEdit_file.setText(fname[0])
        global typeName
        typeName = fname[0].split(".")[-1]
        global osuFiles
        osuFiles = []
        if typeName == 'osz':
            osuFiles = extractOsz(fname[0])
        else:
            osuFiles.append(fname[0])
        if len(osuFiles) > 0:
            model = QStringListModel()
            model.setStringList(osuFiles)
            self.listView_osulist.setModel(model)

    def osulistClicked(self):
        list_index = self.listView_osulist.currentIndex()
        list_model = self.listView_osulist.model()
        global active_osu_file
        if active_osu_file == list_model.itemData(list_index)[0]:
            return
        active_osu_file = list_model.itemData(list_index)[0]
        global bWriteEvents
        global bWriteTimingPoints
        global bWriteNotes
        bWriteEvents = False
        bWriteTimingPoints = False
        bWriteNotes = False
        analyzeOsuFile(active_osu_file)
        global misc
        global events
        global timingPoints
        global hitObjects

        global title
        global titleUnicode
        global artist
        global artistUnicode
        global creator
        global version
        global HP
        global Keys
        global OD
        for item in misc:
            if item.startswith("Title:"):
                title = item.strip("Title:").strip("\n")
            elif item.startswith("TitleUnicode:"):
                titleUnicode = item.strip("TitleUnicode:").strip("\n")
            elif item.startswith("Artist:"):
                artist = item.strip("Artist:").strip("\n")
            elif item.startswith("ArtistUnicode:"):
                artistUnicode = item.strip("ArtistUnicode:").strip("\n")
            elif item.startswith("Creator:"):
                creator = item.strip("Creator:").strip("\n")
            elif item.startswith("Version:"):
                version = item.strip("Version:").strip("\n")
            elif item.startswith("HPDrainRate:"):
                HP = item.strip("HPDrainRate:").strip("\n")
            elif item.startswith("CircleSize:"):
                Keys = item.strip("CircleSize:").strip("\n")
            elif item.startswith("OverallDifficulty:"):
                OD = item.strip("OverallDifficulty:").strip("\n")
        self.updateLineEdit()

    def generateButtonClicked(self):
        previewPic = generate_preview_pic(active_osu_file)
        
        pixmap = QPixmap(str(previewPic))
        size = pixmap.size()
        pixmap = pixmap.scaled(size/2)

        self.label_pre = QLabel()
        self.label_pre.setGeometry(0, 0, pixmap.size().width(), pixmap.size().height())
        self.label_pre.setPixmap(pixmap)
        self.label_pre.show()

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
        self.lineEdit_hp.setText(HP)
        self.lineEdit_keys.setText(Keys)
        self.lineEdit_od.setText(OD)

def extractOsz(FilePath):
    dirName = os.path.dirname(FilePath)
    global base_path
    base_path = dirName
    osu_file_name = []
    with zipfile.ZipFile(FilePath, 'r') as osz_zip:
        for file_name in osz_zip.namelist():
            if file_name.endswith(".osu"):
                osu_file_name.append(file_name)
                osz_zip.extract(file_name, dirName)
    osu_file_name_withpath = [dirName+'/'+osu_file_name[i] for i in range(len(osu_file_name))]
    return osu_file_name_withpath

def analyzeOsuFile(FilePath):
    global misc
    global events
    global timingPoints
    global hitObjects
    misc = []
    events = []
    timingPoints = []
    hitObjects = []
    global bWriteEvents
    global bWriteTimingPoints
    global bWriteNotes
    with open(file = FilePath, mode = 'r', encoding = "utf-8") as FileRead:
        listOfLines = FileRead.readlines()
        for l in listOfLines:
            if "[Events]" in l:
                bWriteEvents = True
            elif "[TimingPoints]" in l:
                bWriteEvents = False
                bWriteTimingPoints = True
            elif "[HitObjects]" in l:
                bWriteTimingPoints = False
                bWriteNotes = True
            
            if bWriteEvents:
                events.append(l)
            elif bWriteTimingPoints:
                timingPoints.append(l)
            elif bWriteNotes:
                hitObjects.append(l)
            else:
                misc.append(l)

def saveOsuFile(FilePath):
    global misc
    global events
    global timingPoints
    global hitObjects

    global title
    global titleUnicode
    global artist
    global artistUnicode
    global creator
    global version
    global HP
    global Keys
    global OD
    for index,l in enumerate(misc):
        if "SpecialStyle:" in l:
            misc[index] = "SpecialStyle:0\n"
        if "Version:" in l:
            misc[index] = misc[index].rstrip("\n") + " 6K converted\n"
        if "CircleSize:" in l:
            misc[index] = "CircleSize:6\n"

def generate_preview_pic(file):
    global base_path
    global title
    global version
    m = OsuMap.read_file(str(file))
    pf = (
            PlayField(m, padding=30)
            + PFDrawColumnLines()
            + PFDrawBeatLines()
            + PFDrawBpm(x_offset=30, y_offset=0)
            + PFDrawSv(y_offset=0)
            + PFDrawNotes()
    )
    pf.export_fold(max_height=1000).save(base_path + "/" + title + " " + version +" preview.png")
    picPath = base_path + "/" + title + " " + version +" preview.png"
    return picPath

def cleanOsuFile():
    global typeName
    if typeName == "osu":
        return
    global osuFiles
    for extractedOsuFile in osuFiles:
        os.remove(extractedOsuFile)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    app.aboutToQuit.connect(cleanOsuFile)
    sys.exit(app.exec())