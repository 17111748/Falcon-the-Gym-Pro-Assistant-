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

// C program for array implementation of stack 

  
// A structure to represent a stack 
struct Stack { 
    int top; 
    unsigned capacity; 
    int* array; 
}; 
  
// function to create a stack of given capacity. It initializes size of 
// stack as 0 
struct Stack* createStack(unsigned capacity) 
{ 
    struct Stack* stack = (struct Stack*)malloc(sizeof(struct Stack)); 
    stack->capacity = capacity; 
    stack->top = -1; 
    stack->array = (int*)malloc(stack->capacity * sizeof(int)); 
    return stack; 
} 
  
// Stack is full when top is equal to the last index 
int isFull(struct Stack* stack) 
{ 
    return stack->top == stack->capacity - 1; 
} 
  
// Stack is empty when top is equal to -1 
int isEmpty(struct Stack* stack) 
{ 
    return stack->top == -1; 
} 
  
// Function to add an item to stack.  It increases top by 1 
void push(struct Stack* stack, int item) 
{ 
    if (isFull(stack)) 
        return; 
    stack->array[++stack->top] = item; 
    printf("%d pushed to stack\n", item); 
} 
  
// Function to remove an item from stack.  It decreases top by 1 
int pop(struct Stack* stack) 
{ 
    if (isEmpty(stack)) 
        return INT_MIN; 
    return stack->array[stack->top--]; 
} 
  
// Function to return the top from stack without removing it 
int peek(struct Stack* stack) 
{ 
    if (isEmpty(stack)) 
        return INT_MIN; 
    return stack->array[stack->top]; 
} 
  
// Driver program to test above functions 
int main() 
{ 
    struct Stack* stack = createStack(100); 
  
    push(stack, 10); 
    push(stack, 20); 
    push(stack, 30); 
  
    printf("%d popped from stack\n", pop(stack)); 
  
    return 0; 
} 


// Call getCenter then it'll call maxRectangle 

int[] maxAreaHistogram(int[] histogram, int resized_col) {
    struct Stack* stack = createStack(resized_col); 
    int maxArea = 0;
    int maxCol = 0; 
    int width = 0; 
    int height = 0; 

    int index = 0; 
    while(index < resized_col) {
        if(isEmpty(stack) || (histogram[peek(stack)] <= histogram[index])) {
            push(stack, index);
            index += 1; 
        }
        else {
            top_of_stack = pop(stack);

            area = histogram[top_of_stack] * (isEmpty(stack) ? index : index - peek(stack) - 1); 
            if (maxArea < area) {
                maxArea = area; 
                height = histogram[top_of_stack];
                if(!isEmpty(stack)) {
                    maxCol = peek(stack) + 1; 
                    width = (index - peek(stack) - 1)
                }
                else {
                    maxCol = 0; 
                    width = index; 
                }
            }

        }
    }
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
