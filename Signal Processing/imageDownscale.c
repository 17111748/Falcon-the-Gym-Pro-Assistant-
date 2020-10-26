#include <stdio.h> 



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


// Result[] = [maxArea, maxcol, maxWidth, maxHeight]
int maxRectangle() {
    int[] result = maxAreaHistogram(outputImage[0]);
    int maxRow = 0; 

    for(int i = 1; i < resized_row; i++) 



}