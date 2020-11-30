import os
import shutil
from PIL import Image

dir = "/Users/venkatavivekthallam/Desktop/College/2020-21 Senior Year/Fall 2020/18500/Falcon-the-Gym-Pro-Assistant-/UI/images/new_lunge"

def renameFiles():
    # Recursive Case: a folder. Iterate through its files and folders.
    allFiles = os.listdir(dir)
    allFiles = [ fi for fi in allFiles if fi.endswith(".gif") ]
    allFiles.sort()
    print(allFiles)

    init = 0
    count = 0 
    # for i in range(len(allFiles)-1,-1,-1):
    for i in range(len(allFiles)):
        originalStr = dir+"/"+allFiles[i]
        newStr = dir+"/"+"{:03n}".format(count+init)+".gif"
        os.rename(originalStr,newStr)
        count += 1

def duplicateFiles(f):
    init = 158
    duplicateCount = 15
    for i in range(duplicateCount):
        newStr = dir+"/"+"{:03n}".format(i+init)+".gif"
        shutil.copyfile(f,newStr)

def resizeImages(newDir):
    allFiles = os.listdir(dir)
    allFiles = [ fi for fi in allFiles if fi.endswith(".jpg") ]
    allFiles.sort()

    for f in allFiles:
        im = Image.open(dir+"/"+f)

        #image size
        size=(530,350)
        #resize image
        out = im.resize(size)
        # out = out.transpose(Image.FLIP_LEFT_RIGHT)
        #save resized image
        out.save(newDir+"/"+f)


# duplicateFiles(r"C:\Users\Vishal\OneDrive\Documents\School\College\2020-2021\18-500\Falcon-the-Gym-Pro-Assistant-\UI\images\temp\frame_119_delay-0.04s.jpg")
# renameFiles()
# resizeImages( r"C:\Users\Vishal\OneDrive\Documents\School\College\2020-2021\18-500\Falcon-the-Gym-Pro-Assistant-\UI\images\resized_temp")

# 0 - 15 = image 32
for i in range(16):
    newStr = "{:03n}".format(i)+".gif"
    oldImage = os.path.join(dir, "032.gif")
    shutil.copyfile(oldImage, newStr)

# 16 - 73 = images 33 - 48
for i in range(16, 74):
    newStr = "{:03n}".format(i)+".gif"
    oldImage = os.path.join(dir, "{:03n}".format((i - 16) * (48 - 33) // (73 - 16) + 33)+".gif")
    shutil.copyfile(oldImage, newStr)

# 74 - 93 = image 49
for i in range(74, 94):
    newStr = "{:03n}".format(i)+".gif"
    oldImage = os.path.join(dir, "049.gif")
    shutil.copyfile(oldImage, newStr)

# 94 - 157 = images 50 - 64
for i in range(94, 158):
    newStr = "{:03n}".format(i)+".gif"
    oldImage = os.path.join(dir, "{:03n}".format((i - 94) * (64 - 50) // (157 - 94) + 50)+".gif")
    shutil.copyfile(oldImage, newStr)

# 158 - 172 = image 65
for i in range(158, 173):
    newStr = "{:03n}".format(i)+".gif"
    oldImage = os.path.join(dir, "065.gif")
    shutil.copyfile(oldImage, newStr)
