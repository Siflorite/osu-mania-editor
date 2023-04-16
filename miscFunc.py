import math

# Changing half width /, \, :, *, ?, ", <, >, | to full width
def convertIllegalCharacters(inputString):
    outputString = inputString.replace('/',chr(ord('/')+65248)).replace('\\',chr(ord('\\')+65248)).replace(':', chr(ord(':')+65248)).replace('*', chr(ord('*')+65248)).replace('?', chr(ord('?')+65248)).replace('"', chr(ord('"')+65248)).replace('<', chr(ord('<')+65248)).replace('>', chr(ord('>')+65248)).replace('|', chr(ord('|')+65248))
    return outputString

def clamp(num, minn, maxn):
    return max(min(num, max(minn, maxn)), min(minn, maxn))

def setXFromColumn(Col, Keys):
    return math.floor((Col + 0.5) * 512 / Keys)

def ColumnFromX(X, Keys):
    return math.floor(X * Keys / 512)

# Useless
# def check_md5(file1, file2):
#     def get_md5(file):
#         md5 = hashlib.md5()
#         with open(file, 'rb') as f:
#             while True:
#                 content = f.read(1024)
#                 if content:
#                     md5.update(content)
#                 else:
#                     break
#         return md5.hexdigest()
#     print(get_md5(file1))
#     print(get_md5(file2))
#     return get_md5(file1) == get_md5(file2)