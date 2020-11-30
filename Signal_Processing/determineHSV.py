from PIL import Image 
# import cv2 
import numpy as np
import copy
import time 

resized_row = 120
resized_col = 160 

def writeFile(matrix, path):
    string = ""
    for row in matrix: 
        ans = ""
        for col in row: 
            if(col == 1):
                print("bob")
            ans += str(col) + ", "
        ans += "\n"
        string += ans

    with open(path, "wt") as f:
        f.write(string)

def outputImage(temp_image, imageMask, path):
    temp_pixel = temp_image.load()

    for row in range(resized_row):
        for col in range(resized_col):
            temp_pixel[col, row] = (255, 255, 255) 
            if (imageMask[row][col] == 1):
                temp_pixel[col, row] = (0, 0, 0) 
    temp_image.save(path)

def printMat(matrix):
    for row in matrix: 
        print(row)
    print("\n\n")


# originalPath = 'images/iphone/color.jpg'
# downscalePath = 'images/iphone/color_160x120.png'
# trackDownscale = 'images/iphone/track_color_160x120.png'
# endpath = 'images/iphone/find_Pixels.png'

originalPath = 'images/21/pushup/buttHigh.png'
downscalePath = 'images/21/pushup/high_160x120.png'
trackDownscale = 'images/21/pushup/high_track.png'
endpath = 'images/21/pushup/findPixels.png'


time0 = time.time()
# Read Image and Downscale the image 
original_image = Image.open(originalPath)
original_image_pixels = original_image.load()

new_image = original_image.resize((resized_col, resized_row))
new_image_pixels = new_image.load()
new_image.save(downscalePath)


temp_image = Image.open(downscalePath)
converted_image = temp_image.convert('HSV')
converted_pixel = converted_image.load()



# Delete Afterward
track_image = Image.open(downscalePath)
track_image_pixels = track_image.load()

row = 107
col = 113
size = 1
done = False
for temp_r in range(resized_row):
    for temp_c in range(resized_col):
        r = temp_r
        c = temp_c
        if abs(r - row) < (size) and abs(c - col) < (size): 
            
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[c, r]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[c+1, r]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[c, r+1]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[c-1, r-1]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[c+1, r+1]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[c+2, r+2]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[c+3, r+3]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[c+4, r+4]))
            done = True
            track_image_pixels[c, r] = (255, 10, 10)#(255, 10, 10)
            track_image_pixels[c+1, r] = (255, 10, 10)
            track_image_pixels[c, r+1] = (255, 10, 10)
            track_image_pixels[c-1, r-1] = (255, 10, 10)
            track_image_pixels[c+1, r+1] = (255, 10, 10)
            track_image_pixels[c+2, r+2] = (255, 10, 10)
            track_image_pixels[c+3, r+3] = (255, 10, 10)
            track_image_pixels[c+4, r+4] = (255, 10, 10)
    if(done):
        print("break")
        done = False

track_image.save(trackDownscale)


# Use this as the final 
image = converted_image
pixels = converted_pixel


# 142x98 (pushupDown)
# Lower: (17, 87, 160)
# Upper: (29, 133, 246)
shoulderOrangeL = (17, 87, 160)
shoulderOrangeU = (29, 133, 246)


# 131x99 (pushupDown)
# Lower: (155, 124, 150)
# Upper: (160, 140, 225)
elbowBlueL = (142, 79, 150)
elbowBlueU = (160, 140, 252)

# 133x114 (pushupDown)
# Lower: (171, 55, 140)
# Upper: (187, 94, 157)
wristPurpleL = (156, 50, 87)
wristPurpleU = (192, 94, 193)

# 116x105 (pushupDown)
# Lower: (42, 70, 209)
# Upper: (45, 100, 250)
hipYellowL = (38, 65, 165)
hipYellowU = (45, 100, 253)

# 65x105 size 6x3
# Lower: (239, 73, 133)
# Upper: (253, 134, 202)
kneeRedL = (239, 64, 133)
kneeRedU = (252, 137, 216)

# Lower: (50, 45, 160)
# Upper: (60, 65, 240)
kneeOtherGreenL = (47, 45, 111)
kneeOtherGreenU = (60, 74, 240)

# 39x107 (pushupDown)
# Lower: (130, 52, 200)
# Upper: (141, 78, 243)
ankleBlueL = (125, 52, 127)
ankleBlueU = (141, 78, 243)

# Lower: (210, 30, 170)
# Upper: (242, 82, 250)
ankleOtherPinkL = (210, 30, 170)
ankleOtherPinkU = (242, 82, 250)

bodyHSVBounds = [(shoulderOrangeL, shoulderOrangeU), (elbowBlueL, elbowBlueU), 
                 (wristPurpleL, wristPurpleU), (hipYellowL, hipYellowU), 
                 (kneeRedL, kneeRedU), (kneeOtherGreenL, kneeOtherGreenU), 
                 (ankleBlueL, ankleBlueU), (ankleOtherPinkL, ankleOtherPinkU)]

def picToPix(picture):
    original_image = Image.open(picture)
    new_image = original_image.resize((resized_col, resized_row))
    converted_image = new_image.convert('HSV')
    converted_pixel = converted_image.load()
    return converted_pixel


def jointTracking(lowerMask, upperMask, pixels): 
    imageMask = []
    for row in range(resized_row):
        imageRowMask = [0] * resized_col 
        for col in range(resized_col):
            (h, s, v) = pixels[col, row]
            if (h >= lowerMask[0] and s >= lowerMask[1] and v >= lowerMask[2] and 
                h <= upperMask[0] and s <= upperMask[1] and v <= upperMask[2]): 
                imageRowMask[col] = 1
        imageMask.append(imageRowMask)
    return imageMask


def erosion(imageMask):
    # Morphological Transform (Dilation, Erosion) to get rid of noise 
    directions = [[-1, 0], [0, -1], [1, 0], [0, 1]]
    erosionMask = []
    for row in range(resized_row):
        erosionMaskRow = [0] * resized_col
        for col in range(resized_col):
            erosionMaskRow[col] = 1
            if (imageMask[row][col] == 0): 
                erosionMaskRow[col] = 0
            else:
                for direction in directions: 
                    x = row + direction[0]
                    y = col + direction[1]
                    if (x < 0 or x >= resized_row or y < 0 or y >= resized_col):
                        erosionMaskRow[col] = 0
                    elif (imageMask[x][y] == 0):
                        erosionMaskRow[col] = 0 
        erosionMask.append(erosionMaskRow)
    return erosionMask          


def dilation(erosionMask):
    directions = [[-1, 0], [0, -1], [1, 0], [0, 1]]
    imageMask = copy.deepcopy(erosionMask)
    for row in range(resized_row):
        for col in range(resized_col):
            if (erosionMask[row][col] == 0):
                for direction in directions: 
                    x = row + direction[0]
                    y = col + direction[1]
                    if (x >= 0 and x < resized_row and y >= 0 and y < resized_col and erosionMask[x][y] == 1):
                        imageMask[row][col] = 1
                        break 
    return imageMask

def max_area_histogram(histogram):
    stack = [0] * 160
    stackIndex = -1
    max_area = 0
    maxCol = 0 
    width = 0 
    height = 0

    index = 0
    while (index < len(histogram)): 
        if (stackIndex == -1) or (histogram[stack[stackIndex]] <= histogram[index]): 
            stackIndex += 1
            stack[stackIndex] = index 
            index += 1

        else: 
            top_of_stack = stack[stackIndex]
            stackIndex -= 1 

            area = (histogram[top_of_stack] * 
                ( index
                if (stackIndex == -1) else (index - stack[stackIndex] - 1))) 

            if (max_area < area):
                max_area = area 
                height = histogram[top_of_stack]
                if (stackIndex != -1):
                    maxCol = stack[stackIndex] + 1
                    width = (index - stack[stackIndex] - 1) 
                else: 
                    maxCol = 0
                    width = index 

    while stackIndex != -1: 
        top_of_stack = stack[stackIndex]
        stackIndex -= 1 
        area = (histogram[top_of_stack] * ((index - stack[stackIndex] - 1) if (stack != -1) else index)) 

        if (max_area < area):
            max_area = area 
            height = histogram[top_of_stack]
            if (stackIndex != -1):
                maxCol = stack[stackIndex] + 1
                width = (index - stack[stackIndex] - 1) 
            else: 
                maxCol = 0
                width = index 

    return (max_area, maxCol, width, height)  

# Returns area of the largest rectangle  
# with all 1s in A  
def maxRectangle(A, resized_row, resized_col): 
      
    (maxArea, maxCol, maxWidth, maxHeight) = max_area_histogram(A[0])  
    maxRow = 0
  
    # iterate over row to find maximum rectangular  
    # area considering each row as histogram  
    for i in range(1, resized_row): 
        for j in range(resized_col): 

            # if A[i][j] is 1 then add A[i -1][j]  
            if (A[i][j]): 
                A[i][j] += A[i - 1][j]  
  
        # Update result if area with current  
        # row (as last row) of rectangle) is more  
        (area, col, width, height) = max_area_histogram(A[i])
        if (area > maxArea):
            maxArea = area
            maxRow = i
            maxCol = col  
            maxWidth = width
            maxHeight = height

    return (maxRow, maxCol, maxWidth, maxHeight) 


def getCenter(imageMask, resized_row, resized_col):
    (maxRow, maxCol, maxWidth, maxHeight) = maxRectangle(imageMask, resized_row, resized_col)
    row = maxRow - (maxHeight/2)
    col = maxCol + (maxWidth/2)
    return (row, col)


def testing(imageMask):
    for i in range(len(imageMask)):
        for j in range(len(imageMask[0])):
            if(imageMask[i][j] == 1):
                print(str(i) + ", " + str(j))

def mainFunction(bodyHSVBounds): 
    resized_row = 120
    resized_col = 160 
    positions = []

    
    for bodyPart in bodyHSVBounds: 
        lowerMask = bodyPart[0]
        upperMask = bodyPart[1]
        imageMask = jointTracking(lowerMask, upperMask, pixels)
        imageMask = dilation(imageMask)
        imageMask = dilation(imageMask)
        imageMask = erosion(imageMask)
        (row, col) = getCenter(imageMask, resized_row, resized_col)
        positions.append((row, col))
    
    return positions


positions = mainFunction(bodyHSVBounds)

print(positions)

track_image = Image.open(downscalePath)
track_image_pixels = track_image.load()

imageMask = []
for r in range(resized_row):
    temp = [0] * resized_col
    imageMask.append(temp)

for posIndex in range(len(positions)):
    pos = positions[posIndex]
    row = int(pos[0])
    col = int(pos[1])
    size = 2
    done = False

    for r in range(resized_row):
        for c in range(resized_col):
            if abs(r - row) < (size) and abs(c - col) < (size): 
                done = True
                track_image_pixels[c, r] = (100, 100, 255) #(255, 10, 10)
        if(done):
            done = False
    
track_image.save(endpath)

mainFunction(bodyHSVBounds)


###########################################################################################
# def mainFunction(bodyHSVBounds, picture): 
#     resized_row = 120
#     resized_col = 160 
#     positions = []

#     pixels = picToPix(picture)
#     for bodyPart in bodyHSVBounds: 
#         lowerMask = bodyPart[0]
#         upperMask = bodyPart[1]
#         imageMask = jointTracking(lowerMask, upperMask, pixels)
#         imageMask = dilation(imageMask)
#         imageMask = dilation(imageMask)
#         imageMask = erosion(imageMask)
#         (row, col) = getCenter(imageMask, resized_row, resized_col)
#         positions.append((row, col))
    
#     return positions

# def getJoints(picture):
#     shoulderOrangeL = (17, 87, 160)
#     shoulderOrangeU = (29, 133, 246)

#     elbowBlueL = (155, 124, 150)
#     elbowBlueU = (160, 140, 225)

#     wristPurpleL = (171, 55, 87)
#     wristPurpleU = (192, 94, 157)

#     hipYellowL = (38, 65, 165)
#     hipYellowU = (45, 100, 253)

#     kneeRedL = (239, 64, 133)
#     kneeRedU = (252, 137, 216)

#     kneeOtherGreenL = (47, 45, 111)
#     kneeOtherGreenU = (60, 74, 240)

#     ankleBlueL = (125, 52, 127)
#     ankleBlueU = (141, 78, 243)

#     ankleOtherPinkL = (210, 30, 170)
#     ankleOtherPinkU = (242, 82, 250)

#     bodyHSVBounds = [(shoulderOrangeL, shoulderOrangeU), (elbowBlueL, elbowBlueU), 
#                     (wristPurpleL, wristPurpleU), (hipYellowL, hipYellowU), 
#                     (kneeRedL, kneeRedU), (kneeOtherGreenL, kneeOtherGreenU), 
#                     (ankleBlueL, ankleBlueU), (ankleOtherPinkL, ankleOtherPinkU)]


#     return mainFunction(bodyHSVBounds, picture)