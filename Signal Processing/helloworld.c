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


#define RESIZED_ROW 160
#define RESIZED_COL 120
#define NUM_DIRECTIONS 4
u8 lowerMask[3] = {15, 20, 64};
u8 upperMask[3] = {180, 255, 255};
u8 directions[4][2] = {{-1, 0}, {0, -1}, {1, 0}, {0, 1}};

struct Stack {
    int top;
    unsigned capacity;
    int* array;
};

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

    xil_printf("hello\n\r");

    // Loading the image into memory
    unsigned char* imagePtr = XPAR_BRAM_0_BASEADDR; // Base addr of the BRAM block

    int received_count;
    received_count = 0;
	while(received_count < IMAGE_SIZE) {
		received_count += XUartLite_Recv(&UartLite, imagePtr + received_count, IMAGE_SIZE - received_count); // Storing all of the bytes received from UART into BRAM at the base_addr
//		xil_printf("%d\n\r", received_count);
	}


	// Repeat the following for each of the various body locations
	for(int i = 0; i < 1; i++) {
		// Generating Binary Mask
		unsigned char* binMaskPtr = 0xC000E100;
		for(int i = 0; i < 160 * 120; i ++) {
			u8 hue = imagePtr[3 * i];
			u8 saturation = imagePtr[3 * i + 1];
			u8 value = imagePtr[3 * i + 2];
			if(hue >= lowerMask[0] && saturation >= lowerMask[1] && value >= lowerMask[2] && hue <= upperMask[0] && saturation <= upperMask[1] && value <= upperMask[2]) {
	//			xil_printf("hello");
				binMaskPtr[i] = 1;
			}
			else {
				binMaskPtr[i] = 0;
			}
		}

		// Performing Erosion
		unsigned char* erosMaskPtr = 0xC0012C00;
		unsigned char* dilMaskPtr = 0xC0017700;
		for(int i = 0; i < RESIZED_ROW; i++) {
			for(int j = 0; j < RESIZED_COL; j++) {
				int ind = i * 120 + j;
				erosMaskPtr[ind] = 1;
				if (binMaskPtr[ind] == 0) {
					erosMaskPtr[ind] = 0;
					dilMaskPtr[ind] = 0;
				}
				else {
					for(int direction = 0; direction < NUM_DIRECTIONS; direction++) {
						u8 x = i + directions[direction][0];
						u8 y = j + directions[direction][1];
						if(x < 0 || x >= RESIZED_ROW || y < 0 || y >= RESIZED_COL) {
							erosMaskPtr[ind] = 0;
							dilMaskPtr[ind] = 0;
						}
						else if(binMaskPtr[ind] == 0) {
							erosMaskPtr[ind] = 0;
							dilMaskPtr[ind] = 0;
						}
					}
				}
			}
		}

		for(int row = 0; row < RESIZED_ROW; row++) {
			for(int col = 0; col < RESIZED_COL; col++) {
				int ind = row * RESIZED_COL + col;
				if(erosMaskPtr[ind] == 0) {
					for(int direction = 0; direction < NUM_DIRECTIONS; direction++) {
						int x = row + directions[direction][0];
						int y = col + directions[direction][1];
	                    if (x >= 0 && x < RESIZED_ROW && y >= 0 && y < RESIZED_COL && erosMaskPtr[ind] == 1) {
	                        dilMaskPtr[ind] = 1;
	                        break;
	                    }
					}
				}
			}
		}

	//	for (int i = IMAGE_SIZE - 10; i < IMAGE_SIZE; i++) {
	//		xil_printf("%d\n\r", bramPtr[i]);
	//	}

	//    for(int i = 0; i < 56000; i++) {
	//    	bramPtr[i] = i;
	//    }
	//
	//    for(int i = 0; i < 56000; i++) {
	//    	if(bramPtr[i] != i % 256) {
	//    		xil_printf("FUCK");
	//    		return 1;
	//    	}
	//    }
//		for(int i = 0; i < 160 * 120; i++) {
//			xil_printf("%d\n\r", dilMaskPtr[i]);
//		}
	}

    xil_printf("done\n\r");

    cleanup_platform();
    return 0;
}


//// C program for array implementation of stack
//
//// function to create a stack of given capacity. It initializes size of
//// stack as 0
//struct Stack* createStack(unsigned capacity)
//{
//    struct Stack* stack = (struct Stack*)malloc(sizeof(struct Stack));
//    stack->capacity = capacity;
//    stack->top = -1;
//    stack->array = (int*)malloc(stack->capacity * sizeof(int));
//    return stack;
//}
//
//// Stack is full when top is equal to the last index
//int isFull(struct Stack* stack)
//{
//    return stack->top == stack->capacity - 1;
//}
//
//// Stack is empty when top is equal to -1
//int isEmpty(struct Stack* stack)
//{
//    return stack->top == -1;
//}
//
//// Function to add an item to stack.  It increases top by 1
//void push(struct Stack* stack, int item)
//{
//    if (isFull(stack))
//        return;
//    stack->array[++stack->top] = item;
//    printf("%d pushed to stack\n", item);
//}
//
//// Function to remove an item from stack.  It decreases top by 1
//int pop(struct Stack* stack)
//{
//    if (isEmpty(stack))
//        return INT_MIN;
//    return stack->array[stack->top--];
//}
//
//// Function to return the top from stack without removing it
//int peek(struct Stack* stack)
//{
//    if (isEmpty(stack))
//        return INT_MIN;
//    return stack->array[stack->top];
//}
//
//
//
//// Call getCenter then it'll call maxRectangle
//
//int[] maxAreaHistogram(int[] histogram, int resized_col) {
//    struct Stack* stack = createStack(resized_col);
//    int maxArea = 0;
//    int maxCol = 0;
//    int width = 0;
//    int height = 0;
//
//    int index = 0;
//    while(index < resized_col) {
//        if(isEmpty(stack) || (histogram[peek(stack)] <= histogram[index])) {
//            push(stack, index);
//            index += 1;
//        }
//        else {
//            top_of_stack = pop(stack);
//
//            area = histogram[top_of_stack] * (isEmpty(stack) ? index : index - peek(stack) - 1);
//            if (maxArea < area) {
//                maxArea = area;
//                height = histogram[top_of_stack];
//                if(!isEmpty(stack)) {
//                    maxCol = peek(stack) + 1;
//                    width = (index - peek(stack) - 1)
//                }
//                else {
//                    maxCol = 0;
//                    width = index;
//                }
//            }
//
//        }
//    }
//}
//
//
//
//// Result[] = [maxArea, maxcol, maxWidth, maxHeight]
//int[] maxRectangle(int[][] image, int resized_row, int resized_col) {
//    int[] result = maxAreaHistogram(image[0], resized_col);
//    int maxRow = 0;
//
//    for(int i = 1; i < resized_row; i++) {
//        for(int j = 0; j < resized_col; j++) {
//            if (image[i][j]) {
//                image[i][j] += image[i-1][j];
//
//                int[] temp_result = maxAreaHistogram(image[i], resized_col);
//                if(temp_result[0] > result[0]) {
//                    result = temp_result;
//                    maxRow = i
//                }
//            }
//        }
//    }
//
//    return result;
//}
//
//// Returns [row, col] (Wrapper Function)
//int[] getCenter(int[][]imageMask, int resized_row, int resized_col) {
//    int[] result = maxRectangle(imageMask, resized_row, resized_col);
//
//    int [2] answer;
//    answer[0] = result[0] - (result[3]/2);
//    answer[1] = result[1] + (result[2]/2);
//
//    return answer;
//}
