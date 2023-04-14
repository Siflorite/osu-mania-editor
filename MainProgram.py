import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QLabel, QMessageBox
from PySide6.QtCore import QStringListModel

from PySide6.QtGui import QPixmap
from main_ui import Ui_MainWindow
import os
import zipfile
from zipfile import ZipFile
import hashlib
import json
import math

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
        fname = QFileDialog.getOpenFileName(self, "打开osu铺面文件或osz压缩文件", '', "Osu zip files (*.osz);;Osu Beatmap Files (*.osu)", "Osu zip files (*.osz)")
        if(fname[0] == ""):
            return
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
                title = item.replace("Title:", "").strip("\n").replace('/',chr(ord('/')+65248)).replace('\\',chr(ord('\\')+65248))
                title = title.replace(':', chr(ord(':')+65248)).replace('*', chr(ord('*')+65248)).replace('?', chr(ord('?')+65248)).replace('"', chr(ord('"')+65248)).replace('<', chr(ord('<')+65248)).replace('>', chr(ord('>')+65248)).replace('|', chr(ord('|')+65248))
            elif item.startswith("TitleUnicode:"):
                titleUnicode = item.replace("TitleUnicode:", "").strip("\n").replace('/',chr(ord('/')+65248)).replace('\\',chr(ord('\\')+65248))
                titleUnicode = titleUnicode.replace(':', chr(ord(':')+65248)).replace('*', chr(ord('*')+65248)).replace('?', chr(ord('?')+65248)).replace('"', chr(ord('"')+65248)).replace('<', chr(ord('<')+65248)).replace('>', chr(ord('>')+65248)).replace('|', chr(ord('|')+65248))
            elif item.startswith("Artist:"):
                artist = item.replace("Artist:", "").strip("\n").replace('/',chr(ord('/')+65248)).replace('\\',chr(ord('\\')+65248))
                artist = artist.replace(':', chr(ord(':')+65248)).replace('*', chr(ord('*')+65248)).replace('?', chr(ord('?')+65248)).replace('"', chr(ord('"')+65248)).replace('<', chr(ord('<')+65248)).replace('>', chr(ord('>')+65248)).replace('|', chr(ord('|')+65248))
            elif item.startswith("ArtistUnicode:"):
                artistUnicode = item.replace("ArtistUnicode:", "").strip("\n").replace('/',chr(ord('/')+65248)).replace('\\',chr(ord('\\')+65248))
                artistUnicode = artistUnicode.replace(':', chr(ord(':')+65248)).replace('*', chr(ord('*')+65248)).replace('?', chr(ord('?')+65248)).replace('"', chr(ord('"')+65248)).replace('<', chr(ord('<')+65248)).replace('>', chr(ord('>')+65248)).replace('|', chr(ord('|')+65248))
            elif item.startswith("Creator:"):
                creator = item.replace("Creator:","").strip("\n").replace('/',chr(ord('/')+65248)).replace('\\',chr(ord('\\')+65248))
                creator = creator.replace(':', chr(ord(':')+65248)).replace('*', chr(ord('*')+65248)).replace('?', chr(ord('?')+65248)).replace('"', chr(ord('"')+65248)).replace('<', chr(ord('<')+65248)).replace('>', chr(ord('>')+65248)).replace('|', chr(ord('|')+65248))
            elif item.startswith("Version:"):
                version = item.replace("Version:", "").strip("\n").replace('/',chr(ord('/')+65248)).replace('\\',chr(ord('\\')+65248))
                version = version.replace(':', chr(ord(':')+65248)).replace('*', chr(ord('*')+65248)).replace('?', chr(ord('?')+65248)).replace('"', chr(ord('"')+65248)).replace('<', chr(ord('<')+65248)).replace('>', chr(ord('>')+65248)).replace('|', chr(ord('|')+65248))
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
            ChartDir = os.path.dirname(OriginalFilePath)
            ChartType = os.path.splitext(OriginalFilePath)[-1]
            if ChartType == ".mc":
                analyzeMCFile(OriginalFilePath)
                dlg = QMessageBox()
                dlg.setWindowTitle("提示")
                dlg.setText(".osu文件已保存至" + os.path.splitext(OriginalFilePath)[0] + ".osu")
                dlg.setStandardButtons(QMessageBox.Yes)
                dlg.exec()
            else:
                temp_path = ChartDir + "/temp"
                mc_file_name = []
                with zipfileDecodingSupport(ZipFile(OriginalFilePath, 'r')) as mcz_zip:
                    for file_name in mcz_zip.namelist():
                        new_file_name = file_name
                        mcz_zip.extract(new_file_name, temp_path)
                        if file_name.endswith(".mc"):
                            mc_file_name.append(file_name)
                for item in mc_file_name:
                    mc_file = os.path.join(temp_path, item)
                    analyzeMCFile(mc_file)

                GeneratedOszFile = os.path.splitext(OriginalFilePath)[0] + ".osz"
                if os.path.exists(GeneratedOszFile):
                    os.remove(GeneratedOszFile)
                with zipfileDecodingSupport(ZipFile(GeneratedOszFile, 'w', zipfile.ZIP_DEFLATED)) as new_osz_zip:
                    for path, dirNames, fileNames in os.walk(temp_path):
                        fpath = path.replace(temp_path, '')
                        for file in fileNames:
                            if file.endswith(".mc") or file.endswith(".mc_"):continue
                            new_osz_zip.write(os.path.join(path, file), os.path.join(fpath, file))
                for root, dirs, files in os.walk(temp_path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root,name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(temp_path)
                dlg = QMessageBox()
                dlg.setWindowTitle("提示")
                dlg.setText(".osz文件已保存至" + GeneratedOszFile)
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

# A patch to support gbk for Chinese and shift-jis for Japanese
def zipfileDecodingSupport(zip_file: ZipFile):
    nameToInfo = zip_file.NameToInfo
    for name, info in nameToInfo.copy().items():
        try:
            real_name = name.encode('cp437').decode('utf-8')
            print("cp437->utf8")
        except:
            try:
                real_name = name.encode('cp437').decode('gb2312')
                print("cp437->gbk")
            except:
                try:
                    real_name = name.encode('cp437').decode('shift-jis')
                    print("cp437->jis")
                except:
                    real_name = name
        if real_name != name:
            info.filename = real_name
            del nameToInfo[name]
            nameToInfo[real_name] = info
    return zip_file # Modified zipfile module to support multi-decoding
        

def clamp(num, minn, maxn):
    return max(min(num, max(minn, maxn)), min(minn, maxn))

def extractOsz(FilePath):
    dirName = os.path.dirname(FilePath)
    global base_path
    base_path = dirName + "/temp"
    global osu_file_name
    osu_file_name = []
    with zipfileDecodingSupport(ZipFile(FilePath, 'r')) as osz_zip:
        for file_name in osz_zip.namelist():
            new_file_name = file_name
            # try:
            #     new_file_name = new_file_name.decode('utf-8')
            # except:
            #     new_file_name = new_file_name.decode('gbk')
            osz_zip.extract(new_file_name, base_path)
            if new_file_name.endswith(".osu"):
                osu_file_name.append(new_file_name)
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
    modifiedStr = ""
    global bNewFile
    if(bNewFile):
        modifiedStr = "_modified"
    ModifiedOszName = os.path.splitext(OriginalOszName)[0] + modifiedStr + os.path.splitext(OriginalOszName)[1]
    ModifiedOszPath = oszBasePathDir + "/" + ModifiedOszName
    print(ModifiedOszPath)
    if os.path.exists(ModifiedOszPath):
        os.remove(ModifiedOszPath)
    global base_path
    with zipfileDecodingSupport(ZipFile(ModifiedOszPath, 'w', zipfile.ZIP_DEFLATED)) as new_osz_zip:
        for path, dirNames, fileNames in os.walk(base_path):
            fpath = path.replace(base_path, '')
            for file in fileNames:
                new_osz_zip.write(os.path.join(path, file), os.path.join(fpath, file))
    # if(check_md5(FilePath, ModifiedOszPath)):
    #     os.remove(ModifiedOszPath)
        

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
    preview_pic = title + " " + version + " preview.png"
    picPath = os.path.join(base_path, preview_pic)
    pf.export_fold(max_height=1000).save(picPath)
    return picPath

def analyzeMCFile(FilePath):
    try:
        with open(FilePath, "r", encoding="UTF-8") as f:
            mcfile = json.load(f)
    except:
        with open(FilePath, "r", encoding="utf-8-sig") as f:
            mcfile = json.load(f)
    creator = mcfile["meta"]["creator"]
    background = mcfile["meta"]["background"]
    version = mcfile["meta"]["version"]
    mode = mcfile["meta"]["mode"] # 0 for Key mode
    if mode != 0:
        dlg = QMessageBox()
        dlg.setWindowTitle("提示")
        dlg.setText("本软件只支持编辑Key模式的Malody谱面！\nThis program only supports Malody Chart in Key Mode!\nError at " + FilePath)
        dlg.setStandardButtons(QMessageBox.Yes)
        dlg.exec()
        return
    title = mcfile["meta"]["song"]["title"] # This is the Unicode Version (that allows non-ascii characters)
    artist = mcfile["meta"]["song"]["artist"] # Ditto
    titleOrg = mcfile["meta"]["song"]["titleorg"] if "titleorg" in mcfile["meta"]["song"] else title
    # I guess this means Original and may not be available in every chart
    artistOrg = mcfile["meta"]["song"]["artistorg"] if "artistorg" in mcfile["meta"]["song"] else artist
    Keys = mcfile["meta"]["mode_ext"]["column"]
    bpmList = mcfile["time"]
    bpmBase = mcfile["time"][0]["bpm"]
    effectList = mcfile["effect"] if "effect" in mcfile else []
    noteList = mcfile["note"]
    sound = mcfile["note"][-1]["sound"]
    offsetMs = mcfile["note"][-1]["offset"] if "offset" in mcfile["note"][-1] else 0
    noteList = noteList[0:-1]
    
    # Produce Osu File [General], [Metadata], [Difficulty], [Events]
    General = []
    General.append("osu file format v14\n\n[General]\n")
    General.append("AudioFilename:" + sound + "\n")
    General.append("AudioLeadIn:" + str(0) +"\n")
    General.append("PreviewTime:-1\nCountdown:0\nSampleSet: Soft\nStackLeniency:0.7\nMode:3\nLetterboxInBreaks:0\nSpecialStyle:0\nWidescreenStoryboard:1\n\n")

    Editor = []
    Editor.append("[Editor]\nDistanceSpacing:1\nBeatDivisor:8\nGridSize:4\nTimelineZoom:2\n\n")

    Metadata = []
    Metadata.append("[Metadata]\n")
    Metadata.append("Title:" + titleOrg + "\n")
    Metadata.append("TitleUnicode:" + title + "\n")
    Metadata.append("Artist:" + artistOrg + "\n")
    Metadata.append("ArtistUnicode:" + artist + "\n")
    Metadata.append("Creator:" + creator + "\n")
    Metadata.append("Version:" + version + "\n")
    Metadata.append("Source:\nTags:\nBeatmapID:0\nBeatmapSetID:-1\n\n")

    Difficulty = []
    Difficulty.append("[Difficulty]\n")
    Difficulty.append("HPDrainRate:8\n")
    Difficulty.append("CircleSize:" + str(Keys) +"\n")
    Difficulty.append("OverallDifficulty:8\n")
    Difficulty.append("ApproachRate:5\nSliderMultiplier:1.4\nSliderTickRate:1\n\n")

    Events = []
    Events.append("[Events]\n")
    Events.append("//Background and Video events\n")
    if background != "":
        Events.append("0,0,\"" + background + "\",0,0\n")
    Events.append("//Break Periods\n//Storyboard Layer 0 (Background)\n//Storyboard Layer 1 (Fail)\n//Storyboard Layer 2 (Pass)\n//Storyboard Layer 3 (Foreground)\n//Storyboard Layer 4 (Overlay)\n//Storyboard Sound Samples\n\n")
    
    # Produce [TimingPoints] (bpmList and effectList)
    TimingPointsList = []
    TimingPointsList.append("[TimingPoints]\n")
    curTime = -offsetMs
    CurBeat = float(bpmList[0]["beat"][0] + bpmList[0]["beat"][1] / bpmList[0]["beat"][2])
    LastBeat = CurBeat
    MsPerBeat = 60 * 1000 / bpmBase
    indexEffect = 0
    BPMCheckList =[]
    for item in bpmList:
        CurBeat = float(item["beat"][0] + item["beat"][1] / item["beat"][2])
        while(indexEffect < len(effectList)):
            effectBeatList = effectList[indexEffect]["beat"]
            effectBeat = float(effectBeatList[0] + effectBeatList[1] / effectBeatList[2])
            if effectBeat < CurBeat and effectBeat >= LastBeat:
                effectTime = curTime + (effectBeat - LastBeat) * MsPerBeat
                if effectList[indexEffect]["scroll"] < 0 : 
                    indexEffect += 1
                    continue
                speedVariation = round(float(-100/effectList[indexEffect]["scroll"]), 12) if effectList[indexEffect]["scroll"] !=0 else -100000000
                TimingPointsList.append(str(int(effectTime)) + "," + '%.15g'%speedVariation + ",4,2,0,10,0,0\n")
                indexEffect += 1
            else:
                break
        curTime += (CurBeat - LastBeat) * MsPerBeat
        MsPerBeat = 60 * 1000 / item["bpm"]
        BPMCheckList.append([CurBeat, MsPerBeat])
        TimingPointsList.append(str(int(curTime)) + "," + str(round(MsPerBeat, 12)) + ",4,2,0,10,1,0\n")
        LastBeat = CurBeat
    while(indexEffect < len(effectList)):
        effectBeatList = effectList[indexEffect]["beat"]
        effectBeat = float(effectBeatList[0] + effectBeatList[1] / effectBeatList[2])
        effectTime = curTime + (effectBeat - LastBeat - 1) * MsPerBeat
        if effectList[indexEffect]["scroll"] < 0 :
            indexEffect += 1 
            continue
        speedVariation = round(float(-100/effectList[indexEffect]["scroll"]), 12) if effectList[indexEffect]["scroll"] !=0 else -100000000
        TimingPointsList.append(str(int(effectTime)) + "," + '%.15g'%speedVariation + ",4,2,0,10,0,0\n")
        indexEffect += 1
    TimingPointsList.append("\n")

    # Produce [HitObjects] (notList)
    HitObjectsList = []
    HitObjectsList.append("[HitObjects]\n")

    def fromBeatGetMs(Beat):
        time = -offsetMs
        BeatIndex = 1
        curBPMBeat = BPMCheckList[0][0]
        nextBPMBeat = BPMCheckList[BeatIndex][0] if len(BPMCheckList) > 1 else curBPMBeat
        curMsPerBeat = BPMCheckList[0][1]
        while(Beat > nextBPMBeat and BeatIndex - 1 < len(BPMCheckList)):
            time += curMsPerBeat * (nextBPMBeat - curBPMBeat)
            curBPMBeat = nextBPMBeat
            curMsPerBeat = BPMCheckList[BeatIndex][1] if len(BPMCheckList) > 1 else curMsPerBeat
            BeatIndex += 1
            if(BeatIndex >= len(BPMCheckList)): break
            nextBPMBeat = BPMCheckList[BeatIndex][0]
        time += (Beat - curBPMBeat) * curMsPerBeat
        return time
    
    itemBeat = float(noteList[0]["beat"][0] + noteList[0]["beat"][1] / noteList[0]["beat"][2])
    BeatTime = fromBeatGetMs(itemBeat)
    FirstTimingPoint = TimingPointsList[1].split(",")
    FirstTimingPoint[0] = str(int(BeatTime))
    TimingPointsList[1] = ",".join(FirstTimingPoint)

    for item in noteList:
        itemBeat = float(item["beat"][0] + item["beat"][1] / item["beat"][2])
        BeatTime = fromBeatGetMs(itemBeat)
        XPos = setXFromColumn(item["column"], Keys)
        if "endbeat" in item:
            itemBeatend = float(item["endbeat"][0] + item["endbeat"][1] / item["endbeat"][2])
            BeatendTime = fromBeatGetMs(itemBeatend)
            HitObjectsList.append(str(int(XPos)) + ",192," + str(int(BeatTime)) + ",128,0," + str(int(BeatendTime)) + ":0:0:0:0:\n")
        else:
            HitObjectsList.append(str(int(XPos)) + ",192," + str(int(BeatTime)) + ",1,0,0:0:0:0:\n")
    FirstHitObjectList = HitObjectsList[1].split(",")
    FirstHitObjectList[3] = "5"
    HitObjectsList[1] = ",".join(FirstHitObjectList)
        
    FinalFile = General + Editor + Metadata + Difficulty + Events + TimingPointsList + HitObjectsList
    (file_path, file_name) = os.path.split(FilePath)
    (name, suffix) = os.path.splitext(file_name)
    TransferredOsuPath = os.path.join(file_path, str(name + ".osu"))
    if os.path.exists(TransferredOsuPath):
        os.remove(TransferredOsuPath)
    with open(file = TransferredOsuPath, mode = "w", encoding = "utf-8") as OsuFileWrite:
        for l in FinalFile:
            OsuFileWrite.write(l)


def setXFromColumn(Col, Keys):
    return math.floor((Col + 0.5) * 512 / Keys)

def ColumnFromX(X, Keys):
    return math.floor(X * Keys / 512)


def cleanOsuFile():
    saveOsuFile(bSaveOsz=True)
    global typeName
    if typeName == "osu":
        return
    global base_path
    if base_path == "":
        return
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