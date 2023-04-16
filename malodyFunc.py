import json
import os
import zipfile
from zipfile import ZipFile

import zipfileMultiCodeSupport
import miscFunc

sound = ""
creator = ""
background = ""
version = ""
mode = ""
title = ""
artist = ""
titleOrg = ""
artistOrg = ""
Keys = 6
background = ""
bpmList = []
effectList = []
noteList = []


def convertMcOrMczFile(FilePath):
    ChartDir = os.path.dirname(FilePath)
    ChartType = os.path.splitext(FilePath)[-1]
    if ChartType == ".mc":
        errorInfo = analyzeMCFile(FilePath)
        totalErrorInfo = []
        if errorInfo != "":
            totalErrorInfo.append(errorInfo)
        newOsuChartPath = convertMcToOsu(FilePath)
        return ChartType, newOsuChartPath, totalErrorInfo
    else:
        temp_path = ChartDir + "/temp"
        mc_file_name = []
        with zipfileMultiCodeSupport.zipfileDecodingSupport(ZipFile(FilePath, 'r')) as mcz_zip:
            for file_name in mcz_zip.namelist():
                mcz_zip.extract(file_name, temp_path)
                if file_name.endswith(".mc"):
                    mc_file_name.append(file_name)
        totalErrorInfo = []
        for item in mc_file_name:
            mc_file = os.path.join(temp_path, item)
            errorInfo = analyzeMCFile(mc_file)
            if errorInfo != "":
                totalErrorInfo.append(errorInfo)
            convertMcToOsu(mc_file)
        
        GeneratedOszFile = os.path.splitext(FilePath)[0] + ".osz"
        if os.path.exists(GeneratedOszFile):
            os.remove(GeneratedOszFile)
        with zipfileMultiCodeSupport.zipfileDecodingSupport(ZipFile(GeneratedOszFile, 'w', zipfile.ZIP_DEFLATED)) as new_osz_zip:
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
        return ChartType, GeneratedOszFile, totalErrorInfo

def analyzeMCFile(FilePath):
    try:
        with open(FilePath, "r", encoding="UTF-8") as f:
            mcfile = json.load(f)
    except:
        with open(FilePath, "r", encoding="utf-8-sig") as f:
            mcfile = json.load(f)
    
    global sound
    global creator
    global background
    global version
    global mode
    global title
    global artist
    global titleOrg
    global artistOrg
    global Keys
    global background
    global bpmList
    global effectList
    global noteList

    creator = mcfile["meta"]["creator"]
    background = mcfile["meta"]["background"]
    version = mcfile["meta"]["version"]
    mode = mcfile["meta"]["mode"] # 0 for Key mode
    if mode != 0:
        return str("本软件只支持编辑Key模式的Malody谱面！\nThis program only supports Malody Chart in Key Mode!\nError at " + FilePath)
    title = mcfile["meta"]["song"]["title"] # This is the Unicode Version (that allows non-ascii characters)
    artist = mcfile["meta"]["song"]["artist"] # Ditto
    titleOrg = mcfile["meta"]["song"]["titleorg"] if "titleorg" in mcfile["meta"]["song"] else title
    # I guess this means Original and may not be available in every chart
    artistOrg = mcfile["meta"]["song"]["artistorg"] if "artistorg" in mcfile["meta"]["song"] else artist
    Keys = mcfile["meta"]["mode_ext"]["column"]
    bpmList = mcfile["time"]
    effectList = mcfile["effect"] if "effect" in mcfile else []
    noteList = mcfile["note"]
    sound = mcfile["note"][-1]["sound"]
    noteList = noteList[0:-1]
    return ""

def convertMcToOsu(FilePath):
    global sound
    global creator
    global background
    global version
    global mode
    global title
    global artist
    global titleOrg
    global artistOrg
    global Keys
    global background
    global bpmList
    global effectList
    global noteList

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
    offsetMs = noteList[-1]["offset"] if "offset" in noteList[-1] else 0
    curTime = -offsetMs
    CurBeat = float(bpmList[0]["beat"][0] + bpmList[0]["beat"][1] / bpmList[0]["beat"][2])
    LastBeat = CurBeat
    bpmBase = bpmList[0]["bpm"]
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
        XPos = miscFunc.setXFromColumn(item["column"], Keys)
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
    return TransferredOsuPath