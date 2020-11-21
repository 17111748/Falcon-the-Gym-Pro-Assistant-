import os
import shutil
from PIL import Image

dir = r"C:\Users\Vishal\OneDrive\Documents\School\College\2020-2021\18-500\Falcon-the-Gym-Pro-Assistant-\UI\images\lunge_left"

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
    allFiles = [ fi for fi in allFiles if fi.endswith(".gif") ]
    allFiles = [ fi for fi in allFiles if not fi.startswith("._") ]
    print(allFiles)
    allFiles.sort()

    for f in allFiles:
        im = Image.open(dir+"\\"+f)

        #image size
        size=(528,396)
        #resize image
        out = im.resize(size)
        # out = out.transpose(Image.FLIP_LEFT_RIGHT)
        #save resized image
        out.save(newDir+"\\"+f)


# duplicateFiles(r"C:\Users\Vishal\OneDrive\Documents\School\College\2020-2021\18-500\Falcon-the-Gym-Pro-Assistant-\UI\images\lunge_left\172.gif")
# renameFiles()
resizeImages( r"C:\Users\Vishal\OneDrive\Documents\School\College\2020-2021\18-500\Falcon-the-Gym-Pro-Assistant-\UI\images\temp")