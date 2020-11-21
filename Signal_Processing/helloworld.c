/******************************************************************************
*
* Copyright (C) 2009 - 2014 Xilinx, Inc.  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in
* all copies or substantial portions of the Software.
*
* Use of the Software is limited solely to applications:
* (a) running on a Xilinx device, or
* (b) that interact with a Xilinx device through a bus or interconnect.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
* XILINX  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
* WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
* OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*
* Except as contained in this notice, the name of the Xilinx shall not be used
* in advertising or otherwise to promote the sale, use or other dealings in
* this Software without prior written authorization from Xilinx.
*
******************************************************************************/

/*
 * helloworld.c: simple test application
 *
 * This application configures UART 16550 to baud rate 9600.
 * PS7 UART (Zynq) is not initialized by this application, since
 * bootrom/bsp configures it to baud rate 115200
 *
 * ------------------------------------------------
 * | UART TYPE   BAUD RATE                        |
 * ------------------------------------------------
 *   uartns550   9600
 *   uartlite    Configurable only in HW design
 *   ps7_uart    115200 (configured by bootrom/bsp)
 */

#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"

#include "xparameters.h"
#include "xuartlite.h"

#define UARTLITE_DEVICE_ID	XPAR_UARTLITE_0_DEVICE_ID

XUartLite UartLite;		/* Instance of the UartLite Device */

#define IMAGE_SIZE 57600

#define RESIZED_ROW 120
#define RESIZED_COL 160
#define NUM_DIRECTIONS 4
#define NUM_JOINTS 8
#define NUM_REPS 5

// 								Lunge					Pushup					Leg Raise
int jointList[3][8] = {{0, 0, 0, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 0, 0, 0}, {1, 0, 0, 1, 1, 0, 1, 0}};
int lowerMask[8][3] = {{17, 87, 160},  {142, 79, 150}, {156, 50, 87},  {38, 65, 165},  {239, 64, 133},  {47, 45, 111}, {125, 52, 127}, {210, 30, 170}};
int upperMask[8][3] = {{29, 133, 246}, {160, 140, 252}, {192, 94, 193}, {45, 100, 253}, {252, 137, 216}, {60, 74, 240}, {141, 78, 243}, {242, 82, 250}};
int directions[4][2] = {{-1, 0}, {0, -1}, {1, 0}, {0, 1}};

// Function Prototypes
void initData(unsigned char* dest1, unsigned char* dest2);
void binaryMask(unsigned char* src, unsigned char* dest);
void erode(unsigned char* src, unsigned char* dest);
void dilate(unsigned char* src, unsigned char* dest);
void getCenter(unsigned char* src);

bool testingAccuracy;
bool testingLatency;

testingAccuracy = true;
testingLatency = false;

int main()
{
    init_platform();

    // Initializing the UART connection
	int Status;
	Status = XUartLite_Initialize(&UartLite, UARTLITE_DEVICE_ID);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}
	Status = XUartLite_SelfTest(&UartLite);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

//    xil_printf("hello");

    // Loading the image into memory
    unsigned char* imagePtr = XPAR_BRAM_0_BASEADDR; // Base addr of the BRAM block
    unsigned char *identifierPtr = 0xC0020D00;

    while(1) {

    	initData(identifierPtr, imagePtr);

		if(testingAccuracy) {
			printImage(imagePtr);
			xil_printf("\n");
			continue;	
		}

		if(testingLatency) {
			xil_printf("received all of the info!");
			xil_printf("\n");
			continue;
		}

    	int *neededJoints = jointList[*identifierPtr];

//        xil_printf("loaded image");

    	// Repeat the following for each of the various body locations
    	for(int joint = 0; joint < NUM_JOINTS; joint++) {

    		if(neededJoints[joint] == 0) {
    			xil_printf("%d,%d_", 0, 0);
    			continue;
    		}

    		// Generating Binary Mask
    		unsigned char* binMaskPtr = 0xC000E100;
    		createBinaryMask(imagePtr, binMaskPtr, joint);

//    		xil_printf("Binary mask");
//    		printImage(binMaskPtr);

    		// Performing 2 sets of Dilations
    		unsigned char* dilMaskPtr1 = 0xC0012C00;
    		dilate(binMaskPtr, dilMaskPtr1);
//    		xil_printf("Dilation mask\n\r");
//    		printImage(dilMaskPtr1);


    		unsigned char* dilMaskPtr2 = 0xC0017700;
    		dilate(dilMaskPtr1, dilMaskPtr2);
//    		xil_printf("Dilation mask2\n\r");
//    		printImage(dilMaskPtr2);

    		// Performing Erosion
    		unsigned char* erosMaskPtr = 0xC001C200;
    		erode(dilMaskPtr2, erosMaskPtr);
//    		xil_printf("Erosion mask\n\r");
//    		printImage(erosMaskPtr);

    		// Calculate Result
//    		xil_printf("result");
    		getCenter(erosMaskPtr);

    	}
        xil_printf("\n");

    }

    cleanup_platform();
    return 0;
}

// Function listens to the UART port and loads the identifier and image of IMAGE_SIZE bytes into mem
void initData(unsigned char* dest1, unsigned char* dest2) {
    int received_count;
    // Storing the identifier
	received_count = 0;
	while(received_count < 1) {
		received_count += XUartLite_Recv(&UartLite, dest1, 1); // Storing all of the bytes received from UART into BRAM at the base_addr
//		xil_printf("%d\n\r", received_count);
	}
    // Storing the image
    received_count = 0;
	while(received_count < IMAGE_SIZE) {
		received_count += XUartLite_Recv(&UartLite, dest2 + received_count, IMAGE_SIZE - received_count); // Storing all of the bytes received from UART into BRAM at the base_addr
//		xil_printf("%d\n\r", received_count);
	}
}

void printImage(unsigned char* src) {
	for(int row = 0; row < RESIZED_ROW; row++) {
		for(int col = 0; col < RESIZED_COL; col++) {
			int ind = row * RESIZED_COL + col;
			// if(src[ind] == 1) {
			// 	xil_printf("%d, %d\n\r", row, col);
			// }
			xil_printf("%d ", src[ind]);
		}
	}
}

// Function generates a binary mask with the bytes stored at src and loads into dest
void createBinaryMask(unsigned char* src, unsigned char* dest, int joint) {

	// Gathering the bounds
	int lowerHueBound = lowerMask[joint][0];
	int lowerSatBound = lowerMask[joint][1];
	int lowerValBound = lowerMask[joint][2];
	int higherHueBound = upperMask[joint][0];
	int higherSatBound = upperMask[joint][1];
	int higherValBound = upperMask[joint][2];

//	int ind = 75 * RESIZED_COL + 96;
//	xil_printf("%d, %d, %d", src[3 * ind], src[3 * ind + 1], src[3 * ind + 2]);

	for(int i = 0; i < 160 * 120; i++) {
		int hue = src[3 * i];
		int saturation = src[3 * i + 1];
		int value = src[3 * i + 2];
		if(hue >= lowerHueBound && saturation >= lowerSatBound && value >= lowerValBound && hue <= higherHueBound && saturation <= higherSatBound && value <= higherValBound) {
			dest[i] = 1;
		}
		else {
			dest[i] = 0;
		}
	}
}

// Function performs an erosion with the bytes stored at src and loads into dest
void erode(unsigned char* src, unsigned char* dest) {
	for(int i = 0; i < RESIZED_ROW; i++) {
		for(int j = 0; j < RESIZED_COL; j++) {
			int ind = i * RESIZED_COL + j;
			dest[ind] = 1;
			if (src[ind] == 0) {
				dest[ind] = 0;
			}
			else {
				for(int direction = 0; direction < NUM_DIRECTIONS; direction++) {
					u8 x = i + directions[direction][0];
					u8 y = j + directions[direction][1];
					if(x < 0 || x >= RESIZED_ROW || y < 0 || y >= RESIZED_COL) {
						dest[ind] = 0;
					}
					else if(src[x * RESIZED_COL + y] == 0) {
						dest[ind] = 0;
					}
				}
			}
		}
	}
}

// Function performs a dilation with the bytes stored at src and loads into dest
void dilate(unsigned char* src, unsigned char* dest) {
	for(int row = 0; row < RESIZED_ROW; row++) {
		for(int col = 0; col < RESIZED_COL; col++) {
			int ind = row * RESIZED_COL + col;
			dest[ind] = src[ind];
			if(src[ind] == 0) {
				for(int direction = 0; direction < NUM_DIRECTIONS; direction++) {
					int x = row + directions[direction][0];
					int y = col + directions[direction][1];
					if (x >= 0 && x < RESIZED_ROW && y >= 0 && y < RESIZED_COL && src[x * RESIZED_COL + y] == 1) {
//						xil_printf("%d, %d, %d, %d\n\r", x, y, row, col);
						dest[ind] = 1;
						break;
					}
				}
			}
		}
	}
}


int* maxAreaHistogram(unsigned char* histogram, int *answer) {
	int stack[RESIZED_COL];
	int stackIndex = -1;
    int maxArea = 0;
    int maxCol = 0;
    int width = 0;
    int height = 0;

    int index = 0;

    while(index < RESIZED_COL) {
        if((stackIndex == -1) || (histogram[stack[stackIndex]] <= histogram[index])) {
            stackIndex += 1;
            stack[stackIndex] = index;
            index += 1;
        }
        else {
            int top_of_stack = stack[stackIndex];
            stackIndex -= 1;

            int area = histogram[top_of_stack] * ((stackIndex == -1) ? index : index - stack[stackIndex] - 1);
            if (maxArea < area) {
                maxArea = area;
                height = histogram[top_of_stack];
                if(stackIndex != -1) {
                    maxCol = stack[stackIndex] + 1;
                    width = (index - stack[stackIndex] - 1);
                }
                else {
                    maxCol = 0;
                    width = index;
                }
            }
        }
    }

    while (stackIndex != -1) {
        int top_of_stack = stack[stackIndex];
        stackIndex -= 1;

        int area = histogram[top_of_stack] * ((stackIndex == -1) ? index : index - stack[stackIndex] - 1);
        if (maxArea < area) {
            maxArea = area;
            height = histogram[top_of_stack];
            if(stackIndex != -1) {
                maxCol = stack[stackIndex] + 1;
                width = (index - stack[stackIndex] - 1);
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


// Function finds the center of the biggest rectangle that exists and prints to UART
void getCenter(unsigned char* image) {

	// Implementing maxRectangle(src) and then printing result;
	int result[4];
	maxAreaHistogram(image, &result);
	int maxArea = result[0];
	int maxCol = result[1];
	int maxWidth = result[2];
	int maxHeight = result[3];
	int maxRow = 0;

    for(int row = 1; row < RESIZED_ROW; row++) {
        for(int col = 0; col < RESIZED_COL; col++) {
			int ind = row * RESIZED_COL + col;
			int oldInd = (row-1) * RESIZED_COL + col;
            if (image[ind]) {
                image[ind] += image[oldInd];
                maxAreaHistogram(image + row * RESIZED_COL, &result);
                if(result[0] > maxArea) {
                    maxArea = result[0];
                    maxRow = row;
                    maxCol = result[1];
                    maxWidth = result[2];
                    maxHeight = result[3];
                }
            }
        }
    }

	// Printing out the final location of the result
	xil_printf("%d,%d_", maxRow - (maxHeight/2), maxCol + (maxWidth/2));
}
