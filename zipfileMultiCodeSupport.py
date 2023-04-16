from zipfile import ZipFile

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