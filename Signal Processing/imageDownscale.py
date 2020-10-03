from PIL import Image 
import cv2 
import numpy as np
import copy


def outputImage(temp_image, imageMask):
    temp_pixel = temp_image.load()

    for row in range(resized_row):
        for col in range(resized_col):
            temp_pixel[row, col] = (255, 255, 255) 
            if (imageMask[row][col] == 1):
                temp_pixel[row, col] = (0, 0, 0) 
    temp_image.save('images/test.jpg')

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


# Read Image and Downscale the image 
original_image = Image.open('images/color.jpg')
original_image_pixels = original_image.load()

new_image = original_image.resize((resized_row, resized_col))
new_image_pixels = new_image.load()
new_image.save('images/color_160x120.jpg')

# image = []
# # Convert RGB values to HSV values 
# # 1. Convert every pixel in Hardware 
# new_image = Image.open('images/image_160x120.jpg')
# new_image_pixels = new_image.load()
# print("Image: " + str(new_image_pixels[0,0]))
# for row in range(resized_row):
#     rowList = [] 
#     for col in range(resized_col):
#         (r,g,b) = new_image_pixels[row, col]
#         rowList.append(rgb_to_hsv(r,g,b))
#     image.append(rowList)
# print("Hardware: " + str(image[0][0]))

# 2. Using Pillow Library  
temp_image = Image.open('images/color_160x120.jpg')
converted_image = temp_image.convert('HSV')
converted_pixel = converted_image.load()
# print("Pillow: " + str(converted_pixel[0,0]))

# # 3. Using OpenCV 
# opencv_frame = cv2.imread('images/image_160x120.jpg')
# opencv_image = cv2.cvtColor(opencv_frame, cv2.COLOR_RGB2HSV) 
# print("OpenCV After: " + str(opencv_image[0,0]))


# Use this as the final 
image = converted_image
pixels = converted_pixel



# Create the Upper and Lower Bound for the mask 
# list of the color masks: red, yellow, blue, etc... 
maskList = []


# Bitwise and with the mask (Convolution) 
greenL = (32, 23, 64)
greenU = (59, 255, 255)
redL = (0, 23, 64)
redU = (30,255,255)
yellowL = (15, 23, 64)
yellowU = (32,255,255)

lowerMask = redL
upperMask = redU

# print(str(converted_pixel[0,0]))

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
outputImage(temp_image, imageMask)

imageMask = [[1, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]]

# printMat(imageMask)
resized_col = 5
resized_row = 5


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



printMat(imageMask)

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

imageMask = [[1, 0, 1, 0, 0], [0, 0, 1, 1, 0], [1, 0, 1, 1, 0], [1, 0, 1, 1, 1], [0, 0, 1, 1, 1]]
printMat(imageMask)



print(maxRectangle(imageMask, resized_row, resized_col)) 

