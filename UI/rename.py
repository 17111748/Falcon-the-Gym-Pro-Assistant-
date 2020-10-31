import os
import shutil

dir = "/Users/vishalbaskar/OneDrive/Documents/School/College/2020-2021/18-500/Falcon-the-Gym-Pro-Assistant-/UI/images/temp"

def renameFiles():
    # Recursive Case: a folder. Iterate through its files and folders.
    allFiles = os.listdir(dir)
    allFiles = [ fi for fi in allFiles if fi.endswith(".gif") ]
    allFiles.sort()

    init = 60
    count = 0 
    # for i in range(len(allFiles)-1,-1,-1):
    for i in range(len(allFiles)):
        originalStr = dir+"/"+allFiles[i]
        newStr = dir+"/"+"{:03n}".format(count+init)+".gif"
        os.rename(originalStr,newStr)
        count +=1

def duplicateFiles(f):
    init = 45
    duplicateCount = 15
    for i in range(duplicateCount):
        newStr = dir+"/"+"{:03n}".format(i+init)+".gif"
        shutil.copyfile(f,newStr)


# duplicateFiles("/Users/vishalbaskar/OneDrive/Documents/School/College/2020-2021/18-500/Falcon-the-Gym-Pro-Assistant-/UI/images/temp/frame_000_delay-0.04s.gif")
renameFiles()