# osu-mania-editor
## A quick editor to edit OD, HP, title, etc. and generate previews for osu!mania maps, with GUI based on PySide6  
## 一个可以快速编辑谱面OD, HP, 标题等并生成osu!mania谱面预览的编辑器，使用PySide6编写的GUI

The program loads osu beatmaps from a Pyside's QFileDialog. If the selected file is a .osz file (osu zip file), it will extract the .osu files to the path of the .osz file. Then you can click on the item on the table to select osu map file. The program will then load the map's data. You can modify these data and press Save button to save modified osu map back to the .osz zip file. You can also press the preview button to generate a preview of the selected osu map and it will be stored at the path of the osu file in png format.  

在本程序中点击Load按钮导入osu谱面，可以导入.osu谱面文件和.osz压缩包。如果导入的是.osz压缩包，其中的.osu谱面都会被解压缩到.osz文件所在的目录下，并显示在右侧的列表中。点选右边列表的元素就会读取该osu文件的信息，并可以在程序内修改。在点击Save按钮后就可以保存这些数据并储存回.osz文件。点击谱面预览按钮就会生成一份osu!mania谱面的预览图片，以png格式保存在.osz所在的目录。  

The preview module is completed mainly using [reamber module](https://github.com/Eve-ning/reamberPy)  (you have to pip install it), thanks Evening and his peers for their contribution to rhythm game community!  

预览功能主要通过[reamber模块](https://github.com/Eve-ning/reamberPy)实现（需要自行pip install），在这里由衷感谢Evening等人对音乐游戏社区做出的贡献！  

+ Version 0.1 at 2023.4.8: Load function complete, generate preview function complete.加载功能实现，预览功能实现。  
