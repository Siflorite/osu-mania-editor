# osu-mania-editor
## A quick editor to edit OD, HP, title, etc. and generate previews for osu!mania maps, with GUI based on PySide6  

The program loads osu beatmaps from a Pyside's QFileDialog. If the selected file is a .osz file (osu zip file), it will extract the .osu files to the path of the .osz file. Then you can click on the item on the table to select osu map file. The program will then load the map's data. You can modify these data and press Save button to save modified osu map back to the .osz zip file. You can also press the preview button to generate a preview of the selected osu map and it will be stored at the path of the osu file in png format.  

The preview module is completed mainly using [reamber module](https://github.com/Eve-ning/reamberPy)  (you have to pip install it), thanks Evening and his peers for their contribution to rhythm community!  

Version 0.1 at 2023.4.8: Load function complete, generate preview function complete.  
