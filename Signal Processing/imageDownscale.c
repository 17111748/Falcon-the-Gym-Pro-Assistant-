#include <stdio.h> 
#include <limits.h> 
#include <stdlib.h> 


int [160][120][3] inputImage; // Pixels 

void imageProcess(AXI_STREAM& inputStream, AXI_STREAM& outputResults)
{

    // Temporary Storage
    int [160][120][3] inputImage;
    int [160][120] binaryMask;
    int [160][120] erosionMask;
    int [160][120] outputImage;
    
    // Parameters 
    lowerMask = [59, 23, 64]
    upperMask = [180, 255, 255]
    resized_row = 160;
    resized_col = 120;

    int[][] directions = [[-1, 0], [0, -1], [1, 0], [0, 1]]; 
    int num_directions = 4; 

    // Storing the input stream into a matrix
    for(int row = 0; row < resized_row; row++) {
        for(int col = 0; col < resized_col; col++) {
            value << inputStream;
            inputStream[row][col][0] = value[];
            inputStream[row][col][1] = value[];
            inputStream[row][col][2] = value[];
        }
    }

    // Generate Binary Mask
    for(int row = 0; row < resized_row; row++) {
        for(int col = 0; col < resized_col; col++) {
            // (hue, saturation, value) = pixels[row, col]
            int hue = inputImage[row][col][0];
            int saturation = inputImage[row][col][1];
            int value = inputImage[row][col][2]; 

            if (hue >= lowerMask[0] && saturation >= lowerMask[1] && value >= lowerMask[2] &&  hue <= upperMask[0] && saturation <= upperMask[1] && value <= upperMask[2]) {
                binaryMask[row][col] = 1;
            }
            else {
                binaryMask[row][col] = 0;
            }
                
        }
    } 
    
    // Performing Erosion
    for(int row = 0; row < resized_row; row++) {
        erosionMask[row][col] = 1;
        outputImage[row][col] = 1;
        for(int col = 0; col < resized_col; col++) {
            if(binaryMask[row][col] == 0) {
                erosionMask[row][col] = 0;
                outputImage[row][col] = 0;
            }
            else {
                for(int direction = 0; direction < num_directions; direction++) {
                    int x = row + directions[direction][0];
                    int y = col + directions[direction][1];
                    if (x < 0 || x >= resized_row || y < 0 || y >= resized_col) {
                        erosionMask[row][col] = 0;
                        outputImage[row][col] = 0;
                    }
                    else if (binaryMask[x][y] == 0) {
                        erosionMask[row][col] = 0;
                        outputImage[row][col] = 0;
                    }                    
                }
            }
        }
    }

    // Performing Dilation
    for(int row = 0; row < resized_row; row++) {
        for(int col = 0; col < resized_col; col++) {
            if(erosionMask[row][col] == 0) {
                for(int direction = 0; direction < num_directions; direction++) {
                    int x = row + directions[direction][0];
                    int y = col + directions[direction][1];
                    if (x >= 0 && x < resized_row && y >= 0 && y < resized_col && erosionMask[x][y] == 1) {
                        outputImage[row][col] = 1;
                        break; 
                    }
                }
            }       
        }
    } 

}


// Call getCenter then it'll call maxRectangle 

int[] maxAreaHistogram(int[] histogram, int resized_col) {
    int[resized_col] stack; 
    int stackIndex = -1; 
    int maxArea = 0;
    int maxCol = 0; 
    int width = 0; 
    int height = 0; 

    int [4] answer; 
    
    int index = 0; 
    while(index < resized_col) {
        if((stackIndex == -1) || (histogram[stack[stackIndex]] <= histogram[index])) {
            stackIndex += 1; 
            stack[stackIndex] = index; 
            index += 1; 
        }
        else {
            top_of_stack = stack[stackIndex];
            stackIndex -= 1; 

            int area = histogram[top_of_stack] * ((stackIndex == -1) ? index : index - stack[stackIndex] - 1); 
            if (maxArea < area) {
                maxArea = area; 
                height = histogram[top_of_stack];
                if(stackIndex != -1) {
                    maxCol = stack[stackIndex] + 1; 
                    width = (index - stack[stackIndex] - 1)
                }
                else {
                    maxCol = 0; 
                    width = index; 
                }
            }
        }
    }

    while (stackIndex != -1) {
        top_of_stack = stack[stackIndex];
        stackIndex -= 1; 

        int area = histogram[top_of_stack] * ((stackIndex == -1) ? index : index - stack[stackIndex] - 1); 
        if (maxArea < area) {
            maxArea = area; 
            height = histogram[top_of_stack];
            if(stackIndex != -1) {
                maxCol = stack[stackIndex] + 1; 
                width = (index - stack[stackIndex] - 1)
            }
            else {
                maxCol = 0; 
                width = index; 
            }
        } 
    }

    answer[0] = maxArea; 
    answer[1] = maxCol; 
    answer[2] = width; 
    answer[3] = height; 

    return answer; 
}



// Result[] = [maxArea, maxcol, maxWidth, maxHeight]
int[] maxRectangle(int[][] image, int resized_row, int resized_col) {
    int[] result = maxAreaHistogram(image[0], resized_col);
    int maxRow = 0; 

    for(int i = 1; i < resized_row; i++) {
        for(int j = 0; j < resized_col; j++) {
            if (image[i][j]) {
                image[i][j] += image[i-1][j];

                int[] temp_result = maxAreaHistogram(image[i], resized_col);
                if(temp_result[0] > result[0]) {
                    result = temp_result; 
                    maxRow = i
                }
            }
        }
    }

    return result; 
}

// Returns [row, col] (Wrapper Function)
int[] getCenter(int[][]imageMask, int resized_row, int resized_col) {
    int[] result = maxRectangle(imageMask, resized_row, resized_col);
    
    int [2] answer; 
    answer[0] = result[0] - (result[3]/2); 
    answer[1] = result[1] + (result[2]/2);

    return answer; 
}
