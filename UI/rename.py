import os
import shutil
from PIL import Image

dir = "/Users/vishalbaskar/OneDrive/Documents/School/College/2020-2021/18-500/Falcon-the-Gym-Pro-Assistant-/UI/images/temp"

def renameFiles():
    # Recursive Case: a folder. Iterate through its files and folders.
    allFiles = os.listdir(dir)
    allFiles = [ fi for fi in allFiles if fi.endswith(".jpg") ]
    allFiles.sort()

    init = 95
    count = 0 
    # for i in range(len(allFiles)-1,-1,-1):
    for i in range(len(allFiles)):
        originalStr = dir+"\\"+allFiles[i]
        newStr = dir+"\\"+"{:03n}".format(count+init)+".gif"
        os.rename(originalStr,newStr)
        count +=2

def duplicateFiles(f):
    init = 173
    duplicateCount = 75
    for i in range(duplicateCount):
        newStr = dir+"/"+"{:03n}".format(i+init)+".gif"
        shutil.copyfile(f,newStr)

def resizeImages(newDir):
    allFiles = os.listdir(dir)
    allFiles = [ fi for fi in allFiles if fi.endswith(".jpg") ]
    allFiles.sort()

    for f in allFiles:
        im = Image.open(dir+"\\"+f)

        #image size
        size=(530,350)
        #resize image
        out = im.resize(size)
        # out = out.transpose(Image.FLIP_LEFT_RIGHT)
        #save resized image
        out.save(newDir+"\\"+f)


duplicateFiles("/Users/vishalbaskar/OneDrive/Documents/School/College/2020-2021/18-500/Falcon-the-Gym-Pro-Assistant-/UI/images/lunge/172.gif")
# renameFiles()
# resizeImages( r"C:\Users\Vishal\OneDrive\Documents\School\College\2020-2021\18-500\Falcon-the-Gym-Pro-Assistant-\UI\images\resized_temp")