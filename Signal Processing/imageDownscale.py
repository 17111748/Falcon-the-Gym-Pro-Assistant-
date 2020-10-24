from PIL import Image 
import cv2 
import numpy as np
import copy
import time 

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

# def nothing(x):
#     pass 

# cv2.namedWindow("Tracking")
# cv2.createTrackbar("LH", "Tracking", 0, 255, nothing)
# cv2.createTrackbar("LS", "Tracking", 0, 255, nothing)
# cv2.createTrackbar("LV", "Tracking", 0, 255, nothing)
# cv2.createTrackbar("UH", "Tracking", 255, 255, nothing)
# cv2.createTrackbar("US", "Tracking", 255, 255, nothing)
# cv2.createTrackbar("UV", "Tracking", 255, 255, nothing)

# while True: 
#     frame = cv2.imread('images/color.jpg')
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
    
#     l_h = cv2.getTrackbarPos("LH", "Tracking")
#     l_s = cv2.getTrackbarPos("LS", "Tracking")
#     l_v = cv2.getTrackbarPos("LV", "Tracking")

#     u_h = cv2.getTrackbarPos("UH", "Tracking")
#     u_s = cv2.getTrackbarPos("US", "Tracking")
#     u_v = cv2.getTrackbarPos("UV", "Tracking")

#     # l_b = np.array([110, 50, 50])
#     # u_b = np.array([130, 255, 255])
    
#     l_b = np.array([l_h, l_s, l_v])
#     u_b = np.array([u_h, u_s, u_v])

#     mask = cv2.inRange(hsv, l_b, u_b)
    
#     res = cv2.bitwise_and(frame, frame, mask=mask)
    
#     cv2.imshow("frame", frame)
#     cv2.imshow("mask", mask)
#     cv2.imshow("res", res) 
    
#     key = cv2.waitKey(1)
#     if key == 27: 
#         break 

####################################################################################################################################

resized_row = 160
resized_col = 120 

# # https://www.geeksforgeeks.org/program-change-rgb-color-model-hsv-color-model/
# def rgb_to_hsv(r, g, b): 
#     # R, G, B values are divided by 255 
#     # to change the range from 0..255 to 0..1: 
#     r, g, b = r / 255.0, g / 255.0, b / 255.0
  
#     # h, s, v = hue, saturation, value 
#     cmax = max(r, g, b)    # maximum of r, g, b 
#     cmin = min(r, g, b)    # minimum of r, g, b 
#     diff = cmax-cmin       # diff of cmax and cmin. 
  
#     # if cmax and cmax are equal then h = 0 
#     if cmax == cmin:  
#         h = 0
      
#     # if cmax equal r then compute h 
#     elif cmax == r:  
#         h = (60 * ((g - b) / diff) + 360) % 360
  
#     # if cmax equal g then compute h 
#     elif cmax == g: 
#         h = (60 * ((b - r) / diff) + 120) % 360
  
#     # if cmax equal b then compute h 
#     elif cmax == b: 
#         h = (60 * ((r - g) / diff) + 240) % 360
  
#     # if cmax equal zero 
#     if cmax == 0: 
#         s = 0
#     else: 
#         s = (diff / cmax) * 100
  
#     # compute v 
#     v = cmax * 100
#     return h, s, v 

time0 = time.time()
# Read Image and Downscale the image 
original_image = Image.open('images/pushupDown.png')
original_image_pixels = original_image.load()

new_image = original_image.resize((resized_row, resized_col))
new_image_pixels = new_image.load()
new_image.save('images/pushupDown_160x120.png')


temp_image = Image.open('images/pushupDown_160x120.png')
converted_image = temp_image.convert('HSV')
converted_pixel = converted_image.load()
time1 = time.time()



# Delete Afterward
track_image = Image.open('images/pushupDown_160x120.png')
track_image_pixels = track_image.load()

row = 39
col = 107
size = 2
done = False
for r in range(resized_row):
    for c in range(resized_col):
        if abs(r - row) < (size) and abs(c - col) < (size): 
            
            print(str(r) + "x" + str(c) + ": " + str(converted_pixel[r, c]))
            #print(str(r) + "x" + str(c+1) + ": " + str(converted_pixel[r, c+1]))
            done = True
            track_image_pixels[r, c] = (255, 10, 10)#(255, 10, 10)
    if(done):
        print("break")
        done = False

track_image.save('images/track_pushupDown_160x120.png')
# Use this as the final 
image = converted_image
pixels = converted_pixel



# Create the Upper and Lower Bound for the mask 
# list of the color masks: red, yellow, blue, etc... 
maskList = []


# Bitwise and with the mask (Convolution) 


# 142x98 (pushupDown)
# Lower: (21, 106, 160)
# Upper: (29, 133, 203)
shoulderOrangeL = (21, 106, 160)
shoulderOrangeU = (29, 133, 203)


# 131x99 (pushupDown)
# Lower: (21, 13, 170)
# Upper: (36, 24, 201)
elbowPeachL = (21, 13, 170)
elbowPeachU = (36, 24, 201)


# 116x105 (pushupDown)
# Lower: (42, 70, 209)
# Upper: (45, 100, 250)
hipYellowL = (42, 70, 209)
hipYellowU = (45, 100, 250)

# 133x114 (pushupDown)
# Lower: (171, 55, 140)
# Upper: (187, 94, 157)
wristPurpleL = (171, 55, 140)
writstPurpleU = (187, 94, 157)


# 65x105 size 6x3
# Lower: (239, 73, 133)
# Upper: (253, 134, 202)
kneeRedL = (239, 73, 133)
kneeRedU = (252, 134, 202)

# 39x107 (pushupDown)
# Lower: (136, 70, 209)
# Upper: (141, 78, 243)
ankleBlueL = (136, 70, 209)
ankleBlueU = (141, 78, 243)

kneeOtherGreenL = (32, 23, 64)
kneeOtherGreenU = (32,255,255)


ankleOtherPinkL = (246, 99, 162)
ankleOtherPinkU = (252, 134, 255)


lowerMask = kneeRedL
upperMask = kneeRedU


imageMask = []
for row in range(resized_row):
    imageRowMask = [] 
    for col in range(resized_col):
        (h, s, v) = pixels[row, col]
        if (h >= lowerMask[0] and s >= lowerMask[1] and v >= lowerMask[2] and 
            h <= upperMask[0] and s <= upperMask[1] and v <= upperMask[2]): 
            imageRowMask.append(1)
        else:
            imageRowMask.append(0)
    imageMask.append(imageRowMask)




outputImage(temp_image, imageMask, "images/test.png")

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

# printMat(erosionMask)  

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

# (row, col) = getCenter(imageMask, resized_row, resized_col)
# print(str(row) + " " + str(col))
for r in range(resized_row):
    for c in range(resized_col):
        imageMask[r][c] = 0
        if abs(r - row) < 5 and abs(c - col) < 5: 
            imageMask[r][c] = 1

# outputImage(temp_image, imageMask, "images/testFinal.jpg")

# print(getCenter(imageMask, resized_row, resized_col))


