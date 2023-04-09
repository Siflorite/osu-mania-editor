import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QLabel
from PySide6.QtCore import QStringListModel

from PySide6.QtGui import QPixmap
from main_ui import Ui_MainWindow
import os
import zipfile
import hashlib

from reamber.osu.OsuMap import OsuMap
from reamber.algorithms.playField import PlayField
from reamber.algorithms.playField.parts import PFDrawColumnLines, PFDrawBeatLines, PFDrawBpm, PFDrawSv, PFDrawNotes

typeName = ""
FileName = ""
osuFiles=[]
osu_file_name=[]
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
pic = ""
HP = 0
Keys = 0
OD = 0

class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.loadButton.clicked.connect(self.loadButtonClicked)
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.listView_osulist.clicked.connect(self.osulistClicked)
        self.generateButton.clicked.connect(self.generateButtonClicked)
        self.lineEdit_title.textChanged.connect(self.lineEditTitleModified)
        self.lineEdit_title_unicode.textChanged.connect(self.lineEditTitleUnicodeModified)
        self.lineEdit_artist.textChanged.connect(self.lineEditArtistModified)
        self.lineEdit_artist_unicode.textChanged.connect(self.lineEditArtistUnicodeModified)
        self.lineEdit_creator.textChanged.connect(self.lineEditCreatorModified)
        self.lineEdit_version.textChanged.connect(self.lineEditVersionModified)
        self.lineEdit_hp.textChanged.connect(self.lineEditHPModified)
        self.lineEdit_od.textChanged.connect(self.lineEditODModified)


    def loadButtonClicked(self):
        fname = QFileDialog.getOpenFileName(self, "打开osu铺面文件或osz压缩文件", '', "Osu zip files (*.osz);;Osu Beatmap Files (*.osu)", "Osu zip files (*.osz)")
        self.lineEdit_file.setText(fname[0])
        global typeName
        typeName = fname[0].split(".")[-1]
        global FileName
        FileName = fname[0]
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

    def saveButtonClicked(self):
        saveOsuFile(bSaveOsz=True)

    def osulistClicked(self):
        list_index = self.listView_osulist.currentIndex()
        list_model = self.listView_osulist.model()
        global active_osu_file
        if active_osu_file == list_model.itemData(list_index)[0]:
            return
        global FileName
        if not active_osu_file == "":
            saveOsuFile(bSaveOsz=False)
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
                HP = float(item.strip("HPDrainRate:").strip("\n"))
            elif item.startswith("CircleSize:"):
                Keys = int(item.strip("CircleSize:").strip("\n"))
            elif item.startswith("OverallDifficulty:"):
                OD = float(item.strip("OverallDifficulty:").strip("\n"))
        self.updateLineEdit()
        for item in events:
            if "\"" in item:
                arr = item.split("\"")
                dirname = os.path.dirname(active_osu_file)
                pixmap_bg = QPixmap(dirname + "/" + arr[1])
                self.label_bg.setPixmap(pixmap_bg)
                self.label_bg.setScaledContents(True)

    def generateButtonClicked(self):
        previewPic = generate_preview_pic(active_osu_file)
        
        pixmap = QPixmap(str(previewPic))
        size = pixmap.size()
        pixmap = pixmap.scaled(size/2)

        self.label_pre = QLabel()
        self.label_pre.setGeometry(0, 0, pixmap.size().width(), pixmap.size().height())
        self.label_pre.setPixmap(pixmap)
        self.label_pre.show()
    
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
        if not HP_str.strip(".").isdigit():
            return
        HP = clamp(float(HP_str), 0.0, 10.0)
        if HP - int(HP) == 0:
            HP_str = str(int(HP))
        else:
            HP_str = str(HP)
        changeMiscData("HP", HP_str)

    def lineEditKeysModified(self):
        global Keys
        Keys_str = str(self.lineEdit_keys.text())
        if not Keys_str.isdigit():
            return
        Keys = clamp(int(Keys), 0, 10)
        changeMiscData("Keys", str(Keys))

    def lineEditODModified(self):
        global OD
        OD_str = str(self.lineEdit_od.text())
        if not OD_str.strip(".").isdigit():
            return
        OD = clamp(float(OD_str), 0.0, 10.0)
        if OD - int(OD) == 0:
            OD_str = str(int(OD))
        else:
            OD_str = str(OD)
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

def clamp(num, minn, maxn):
    return max(min(num, max(minn, maxn)), min(minn, maxn))

def extractOsz(FilePath):
    dirName = os.path.dirname(FilePath)
    global base_path
    base_path = dirName + "/temp"
    global osu_file_name
    osu_file_name = []
    with zipfile.ZipFile(FilePath, 'r') as osz_zip:
        for file_name in osz_zip.namelist():
            osz_zip.extract(file_name, base_path)
            if file_name.endswith(".osu"):
                osu_file_name.append(file_name)
    osu_file_name_withpath = [base_path+'/'+osu_file_name[i] for i in range(len(osu_file_name))]
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
    bWriteEvents = False
    bWriteNotes = False
    bWriteTimingPoints = False
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

def changeMiscData(name, val):
    startStr = ""
    if name == "Title" or name ==  "TitleUnicode" or name ==  "Artist" or name ==  "ArtistUnicode" or name ==  "Creator" or name == "Version":
        startStr = name + ":"
    elif name == "HP":
        startStr = "HPDrainRate:"
    elif name == "Keys":
        startStr = "CircleSize:"
    elif name == "OD":
        startStr = "OverallDifficulty:"
    global misc
    for index, item in enumerate(misc):
        if item.startswith(startStr):
            misc[index] = startStr + str(val) + "\n"


def saveOsuFile(bSaveOsz=False):
    global misc
    global events
    global timingPoints
    global hitObjects

    global active_osu_file
    if active_osu_file == "":
        return
    global typeName
    global FileName

    with open(file = active_osu_file, mode = 'w', encoding = "utf-8") as FileWrite:
        for l in misc:
            FileWrite.write(l)
        for l in events:
            FileWrite.write(l)
        for l in timingPoints:
            FileWrite.write(l)
        for l in hitObjects:
            FileWrite.write(l)
    
    if(typeName == "osz" and bSaveOsz):
        saveOszFile(FileName)

def check_md5(file1, file2):
    def get_md5(file):
        md5 = hashlib.md5()
        with open(file, 'rb') as f:
            while True:
                content = f.read(1024)
                if content:
                    md5.update(content)
                else:
                    break
        return md5.hexdigest()
    print(get_md5(file1))
    print(get_md5(file2))
    return get_md5(file1) == get_md5(file2)

def saveOszFile(FilePath):
    oszBasePathDir = os.path.dirname(FilePath)
    OriginalOszName = os.path.split(FilePath)[1]
    ModifiedOszName = os.path.splitext(OriginalOszName)[0] + "_modified" + os.path.splitext(OriginalOszName)[1]
    ModifiedOszPath = oszBasePathDir + "/" + ModifiedOszName
    print(ModifiedOszPath)
    if os.path.exists(ModifiedOszPath):
        os.remove(ModifiedOszPath)
    global base_path
    with zipfile.ZipFile(ModifiedOszPath, 'w', zipfile.ZIP_DEFLATED) as new_osz_zip:
        for path, dirNames, fileNames in os.walk(base_path):
            fpath = path.replace(base_path, '')
            for file in fileNames:
                new_osz_zip.write(os.path.join(path, file), os.path.join(fpath, file))
    if(check_md5(FilePath, ModifiedOszPath)):
        os.remove(ModifiedOszPath)
        

def generate_preview_pic(file):
    global FileName
    base_path = os.path.dirname(FileName)
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
    saveOsuFile(bSaveOsz=True)
    global typeName
    if typeName == "osu":
        return
    global base_path
    for root, dirs, files in os.walk(base_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root,name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(base_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    app.aboutToQuit.connect(cleanOsuFile)
    sys.exit(app.exec())