from PIL import Image 
import cv2 
import numpy as np
import copy
import time 

def writeFile(matrix, path):
    string = ""
    for row in matrix: 
        ans = ""
        for col in row: 
            ans += str(col) + ", "
        ans += "\n"
        string += ans

    with open(path, "wt") as f:
        f.write(string)




def outputImage(temp_image, imageMask, path):
    temp_pixel = temp_image.load()

    for row in range(resized_row):
        for col in range(resized_col):
            temp_pixel[row, col] = (255, 255, 255) 
            if (imageMask[row][col] == 1):
                temp_pixel[row, col] = (0, 0, 0) 
    temp_image.save(path)

def printMat(matrix):
    for row in matrix: 
        print(row)
    print("\n\n")

originalPath = 'images/lungeForward.png'
downscalePath = 'images/lungeForward_160x120.png'
trackDownscale = 'images/track_lungeForward_160x120.png'

resized_row = 160
resized_col = 120 

time0 = time.time()
# Read Image and Downscale the image 
original_image = Image.open(originalPath)
original_image_pixels = original_image.load()

new_image = original_image.resize((resized_row, resized_col))
new_image_pixels = new_image.load()
new_image.save(downscalePath)


temp_image = Image.open(downscalePath)
converted_image = temp_image.convert('HSV')
converted_pixel = converted_image.load()
time1 = time.time()



# Delete Afterward
track_image = Image.open(downscalePath)
track_image_pixels = track_image.load()

row = 102
col = 102
size = 1
done = False
for r in range(resized_row):
    for c in range(resized_col):
        if abs(r - row) < (size) and abs(c - col) < (size): 
            
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r, c]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r+1, c]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r, c+1]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r-1, c-1]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r+1, c+1]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r+2, c+2]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r+3, c+3]))
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r+4, c+4]))
            print(str(r) + "x" + str(c+1) + ": " + str(converted_pixel[r, c+1]))
            done = True
            track_image_pixels[r, c] = (255, 10, 10)#(255, 10, 10)
            track_image_pixels[r+1, c] = (255, 10, 10)
            track_image_pixels[r, c+1] = (255, 10, 10)
            track_image_pixels[r-1, c-1] = (255, 10, 10)
            track_image_pixels[r+1, c+1] = (255, 10, 10)
            track_image_pixels[r+2, c+2] = (255, 10, 10)
            track_image_pixels[r+3, c+3] = (255, 10, 10)
            track_image_pixels[r+4, c+4] = (255, 10, 10)
    if(done):
        print("break")
        done = False

track_image.save(trackDownscale)
# Use this as the final 
image = converted_image
pixels = converted_pixel



# Create the Upper and Lower Bound for the mask 
# list of the color masks: red, yellow, blue, etc... 
maskList = []


# Bitwise and with the mask (Convolution) 
# positions = [(142,98), (131,99), (133,114), (116,105), (65,105), (39,107)]

# 142x98 (pushupDown)
# Lower: (17, 87, 160)
# Upper: (29, 133, 246)
shoulderOrangeL = (17, 87, 160)
shoulderOrangeU = (29, 133, 246)


# 131x99 (pushupDown)
# Lower: (21, 13, 170)
# Upper: (36, 24, 201)
elbowPeachL = (21, 13, 170)
elbowPeachU = (36, 24, 201)

# 133x114 (pushupDown)
# Lower: (171, 55, 140)
# Upper: (187, 94, 157)
wristPurpleL = (171, 55, 140)
wristPurpleU = (187, 94, 157)

# 116x105 (pushupDown)
# Lower: (42, 70, 209)
# Upper: (45, 100, 250)
hipYellowL = (38, 65, 165)
hipYellowU = (45, 100, 253)

# 65x105 size 6x3
# Lower: (239, 73, 133)
# Upper: (253, 134, 202)
kneeRedL = (239, 73, 133)
kneeRedU = (252, 134, 202)

# 39x107 (pushupDown)
# Lower: (130, 52, 200)
# Upper: (141, 78, 243)
ankleBlueL = (130, 52, 200)
ankleBlueU = (141, 78, 243)

# Lower: (50, 45, 160)
# Upper: (60, 65, 240)
kneeOtherGreenL = (50, 45, 160)
kneeOtherGreenU = (60, 65, 240)

# Lower: (210, 30, 170)
# Upper: (242, 82, 250)
ankleOtherPinkL = (210, 30, 170)
ankleOtherPinkU = (242, 82, 250)

bodyHSVBounds = [(shoulderOrangeL, shoulderOrangeU), (elbowPeachL, elbowPeachU), 
                 (wristPurpleL, wristPurpleU), (hipYellowL, hipYellowU), 
                 (kneeRedL, kneeRedU), (kneeOtherGreenL, kneeOtherGreenU), 
                 (ankleBlueL, ankleBlueU), (ankleOtherPinkL, ankleOtherPinkU)]

            
# lowerMask = kneeRedL
# upperMask = kneeRedU

def jointTracking(lowerMask, upperMask): 
    imageMask = []
    for row in range(resized_row):
        imageRowMask = [0] * resized_col 
        for col in range(resized_col):
            (h, s, v) = pixels[row, col]
            if (h >= lowerMask[0] and s >= lowerMask[1] and v >= lowerMask[2] and 
                h <= upperMask[0] and s <= upperMask[1] and v <= upperMask[2]): 
                imageRowMask[col] = 1
        imageMask.append(imageRowMask)
    return imageMask

# lowerMask = shoulderOrangeL
# upperMask = shoulderOrangeU
# imageMask = jointTracking(lowerMask, upperMask)
# outputImage(temp_image, imageMask, "images/test.png")

def erosion(imageMask):
    # imageMask = [[1, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]]

    # printMat(imageMask)
    # resized_col = 5
    # resized_row = 5


    # Morphological Transform (Dilation, Erosion) to get rid of noise 
    directions = [[-1, 0], [0, -1], [1, 0], [0, 1]]
    # directions2 = [[-1, 0], [0, -1], [1, 0], [0, 1], [1,1], [-1, 1], [1, -1], [-1,-1], [0, 2], [0, -2], [-2, 0], [2, 0]]
    erosionMask = []
    for row in range(resized_row):
        erosionMaskRow = []
        for col in range(resized_col):
            colorIn = True 
            if (imageMask[row][col] == 0): 
                colorIn = False 
            else:
                for direction in directions: 
                    x = row + direction[0]
                    y = col + direction[1]
                    if (x < 0 or x >= resized_row or y < 0 or y >= resized_col):
                        colorIn = False 
                    elif (imageMask[x][y] == 0):
                        colorIn = False 
            if (colorIn):
                erosionMaskRow.append(1)
            else: 
                erosionMaskRow.append(0)
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

# outputImage(temp_image, imageMask, "images/testFiltered.jpg")

# Figure out the center of the pixel 
def max_area_histogram(histogram):
    stack = list() 
    max_area = 0
    maxCol = 0 
    width = 0 
    height = 0

    index = 0
    while (index < len(histogram)): 
        # print(stack)
        if (not stack) or (histogram[stack[-1]] <= histogram[index]): 
            stack.append(index) 
            index += 1

        else: 
            top_of_stack = stack.pop() 

            area = (histogram[top_of_stack] * 
                ((index - stack[-1] - 1) 
                if stack else index)) 

            if (max_area < area):
                max_area = area 
                height = histogram[top_of_stack]
                if (stack):
                    # print("Hi: " + str(area) + " " + str(stack[-1]))
                    maxCol = stack[-1] + 1
                    width = (index - stack[-1] - 1) 
                else: 
                    # print("bob")
                    maxCol = 0
                    width = index 


    while stack: 
        top_of_stack = stack.pop() 
        area = (histogram[top_of_stack] * ((index - stack[-1] - 1) if stack else index)) 

        if (max_area < area):
            max_area = area 
            height = histogram[top_of_stack]
            if (stack):
                maxCol = stack[-1] + 1
                width = (index - stack[-1] - 1) 
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
        # print(A[i])
        # print(max_area_histogram(A[i]))
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



def mainFunction(bodyHSVBounds): 
    resized_row = 160
    resized_col = 120 
    positions = []
    count = 0
    for bodyPart in bodyHSVBounds: 
        lowerMask = bodyPart[0]
        upperMask = bodyPart[1]
        imageMask = jointTracking(lowerMask, upperMask)
        if(count == 3):
            temp_image = Image.open(downscalePath) 
            outputImage(temp_image, imageMask, "images/test.png")
            
        imageMask = dilation(imageMask)
        imageMask = dilation(imageMask)
        imageMask = erosion(imageMask)
        # imageMask = erosion(imageMask)
        (row, col) = getCenter(imageMask, resized_row, resized_col)
        positions.append((row, col))
        count += 1
    
    return positions


positions = mainFunction(bodyHSVBounds)
positions[1] = (133,98)

# 133x98 Up Position
# 132x99 Down Position 

print(positions)

#positions.pop(7)
#positions.pop(5)
positions.pop(2)
positions.pop(1)
positions.pop(0)
# positions = positions[:-1]
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

    # print(str(row) + " " + str(col))
    for r in range(resized_row):
        for c in range(resized_col):
            if abs(r - row) < (size) and abs(c - col) < (size): 
                # print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r, c]))
                #print(str(r) + "x" + str(c+1) + ": " + str(converted_pixel[r, c+1]))
                done = True
                track_image_pixels[r, c] = (100, 100, 255) #(255, 10, 10)
        if(done):
            # print("break")
            done = False
    

# outputImage(temp_image, imageMask, "images/testFinal.jpg")
print(positions)
track_image.save('images/findPixels.png')