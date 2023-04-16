import os
import zipfile
from zipfile import ZipFile

from reamber.osu.OsuMap import OsuMap
from reamber.algorithms.playField import PlayField
from reamber.algorithms.playField.parts import PFDrawColumnLines, PFDrawBeatLines, PFDrawBpm, PFDrawSv, PFDrawNotes

import zipfileMultiCodeSupport
import miscFunc

typeName = ""
FileName = ""
osuFiles=[]
basePath = ""

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
bgPic = ""
HP = 0
Keys = 0
OD = 0

def loadOsuOrOszFile(FilePath):
    global FileName
    global typeName
    global osuFiles
    global basePath
    FileName = FilePath
    typeName = os.path.splitext(FilePath)[-1][1:]
    osuFiles = []
    basePath = ""
    if typeName == 'osz':
       osuFiles, basePath = extractOsz(FilePath)
    else:
       osuFiles.append(FilePath)
       basePath = os.path.dirname(FilePath)
    return typeName, osuFiles, basePath

# Only extract Osz to ./temp, do not modify global variables
def extractOsz(FilePath):
    dirName = os.path.dirname(FilePath)
    base_path = dirName + "/temp"
    osu_file_name = []
    with zipfileMultiCodeSupport.zipfileDecodingSupport(ZipFile(FilePath, 'r')) as osz_zip:
        for file_name in osz_zip.namelist():
            osz_zip.extract(file_name, base_path)
            if file_name.endswith(".osu"):
                osu_file_name.append(file_name)
    osu_file_name_withpath = []
    for item in osu_file_name:
        osu_file_name_withpath.append(os.path.join(base_path, item))
    return osu_file_name_withpath, base_path

def saveOsuOrOszFile(FilePath, activeOsuFile, bNewFile=False):
    # bNewFile = false: 
    #   osz: save activeOsuFile with the same name, do not save osz file
    #   osu: save activeOsuFile with the same name
    # bNewFile = true: 
    #   osz: save activeOsuFile with the same name, save osz file
    #   osu: save activeOsuFile with different name
    savedPath = ""
    global typeName
    if bNewFile:
        if typeName == "osz":
            saveOsuFile(activeOsuFile)
            savedPath = saveOszFile(FilePath, bNewFile) # FilePath should be the original Osz file's absolute path
        elif typeName == "osu":
            osuFileDir = os.path.dirname(FilePath)
            OriginalOsuName = os.path.split(FilePath)[1]
            NewOsuName = os.path.splitext(OriginalOsuName)[0] + "_modified" + os.path.splitext(OriginalOsuName)[1]
            NewOsuPath = os.path.join(osuFileDir, NewOsuName)
            saveOsuFile(NewOsuPath)
            savedPath = NewOsuPath
    else:
        saveOsuFile(activeOsuFile)
        if typeName == "osu":
            savedPath = activeOsuFile
    return savedPath

def saveOsuFile(FilePath):
    if FilePath == "": return

    global misc
    global events
    global timingPoints
    global hitObjects

    with open(file = FilePath, mode = 'w', encoding = "utf-8") as FileWrite:
        for l in misc:
            FileWrite.write(l)
        for l in events:
            FileWrite.write(l)
        for l in timingPoints:
            FileWrite.write(l)
        for l in hitObjects:
            FileWrite.write(l)


def saveOszFile(FilePath, bNewFile):
    oszBasePathDir = os.path.dirname(FilePath)
    OriginalOszName = os.path.split(FilePath)[1]
    modifiedStr = ""
    if(bNewFile):
        modifiedStr = "_modified"
    ModifiedOszName = os.path.splitext(OriginalOszName)[0] + modifiedStr + os.path.splitext(OriginalOszName)[1]
    ModifiedOszPath = os.path.join(oszBasePathDir, ModifiedOszName)
    # print(ModifiedOszPath)
    if os.path.exists(ModifiedOszPath):
        os.remove(ModifiedOszPath)
    global basePath
    with zipfileMultiCodeSupport.zipfileDecodingSupport(ZipFile(ModifiedOszPath, 'w', zipfile.ZIP_DEFLATED)) as new_osz_zip:
        for path, dirNames, fileNames in os.walk(basePath):
            fpath = path.replace(basePath, '')
            for file in fileNames:
                new_osz_zip.write(os.path.join(path, file), os.path.join(fpath, file))
    return ModifiedOszPath

def analyzeOsuFile(OsuFile):
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
    with open(file = OsuFile, mode = 'r', encoding = "utf-8") as FileRead:
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

    for item in misc:
        if item.startswith("Title:"):
            title = miscFunc.convertIllegalCharacters(item.replace("Title:", "").strip("\n"))
        elif item.startswith("TitleUnicode:"):
            titleUnicode = miscFunc.convertIllegalCharacters(item.replace("TitleUnicode:", "").strip("\n"))
        elif item.startswith("Artist:"):
            artist = miscFunc.convertIllegalCharacters(item.replace("Artist:", "").strip("\n"))
        elif item.startswith("ArtistUnicode:"):
            artistUnicode = miscFunc.convertIllegalCharacters(item.replace("ArtistUnicode:", "").strip("\n"))
        elif item.startswith("Creator:"):
            creator = miscFunc.convertIllegalCharacters(item.replace("Creator:","").strip("\n"))
        elif item.startswith("Version:"):
            version = miscFunc.convertIllegalCharacters(item.replace("Version:", "").strip("\n"))
        elif item.startswith("HPDrainRate:"):
            HP = float(item.strip("HPDrainRate:").strip("\n"))
        elif item.startswith("CircleSize:"):
            Keys = int(item.strip("CircleSize:").strip("\n"))
        elif item.startswith("OverallDifficulty:"):
            OD = float(item.strip("OverallDifficulty:").strip("\n"))
    for item in events:
        if "\"" in item:
            arr = item.split("\"")
            dirname = os.path.dirname(OsuFile)
            bgPic = os.path.join(dirname, arr[1])
    dict = {}
    dict['Title'] = title
    dict['TitleUnicode'] = titleUnicode
    dict['Artist'] = artist
    dict['ArtistUnicode'] = artistUnicode
    dict['Creator'] = creator
    dict['Version'] = version
    dict['HP'] = HP
    dict['Keys'] = Keys
    dict['OD'] = OD
    dict['Background'] = bgPic
    return dict

def generatePreviewPic(basePath, OsuFile):
    # Base path is the path where preview is stored, usually the path of .osz file or .osu file
    global title
    global version
    m = OsuMap.read_file(str(OsuFile))
    pf = (
            PlayField(m, padding=30)
            + PFDrawColumnLines()
            + PFDrawBeatLines()
            + PFDrawBpm(x_offset=30, y_offset=0)
            + PFDrawSv(y_offset=0)
            + PFDrawNotes()
    )
    preview_pic = title + "_" + version + "_preview.png"
    picPath = os.path.join(basePath, preview_pic)
    pf.export_fold(max_height=1000).save(picPath)
    return picPath

def clampODHP(valStr):
    if not valStr.strip(".").isdigit():
        return -1
    val = miscFunc.clamp(float(valStr), 0.0, 10.0)
    if val - int(val) == 0:
        Outval = int(val)
    else:
        Outval = val
    return Outval

def clampKeys(valStr):
    if not valStr.isdigit():
        return -1
    val = miscFunc.clamp(int(Keys), 0, 10)
    return val

def changeModuleMiscData(name, val):
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

def cleanTempOsuFile(FilePath, activeOsuFile, bNewFile):
    saveOsuOrOszFile(FilePath, activeOsuFile, bNewFile)
    global typeName
    if typeName == "osu":
        return
    else:
        saveOszFile(FilePath, bNewFile=False)
    global basePath
    if basePath == "":
        return
    for root, dirs, files in os.walk(basePath, topdown=False):
        for name in files:
            os.remove(os.path.join(root,name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(basePath)