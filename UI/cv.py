from pygame.locals import KEYDOWN, K_ESCAPE, K_q
import pygame
import cv2
import sys
import time

camera = cv2.VideoCapture(0)
pygame.init()
pygame.display.set_caption("OpenCV camera stream on Pygame")
screen = pygame.display.set_mode([1280, 720])

total_frame = 0 
frameFrequency = 25
photoID = 0 
while True:
    ret, frame = camera.read()

    if(ret is False):
        break

    total_frame+=1

    screen.fill([0, 0, 0])

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = frame.swapaxes(0, 1)
    frame = cv2.flip(frame, 0)
    pygame.surfarray.blit_array(screen, frame)

    if total_frame%frameFrequency == 0:
        photoID += 1
        image_name = str(photoID) +'.jpg'
        cv2.imwrite(image_name, frame)
        print(image_name)

    pygame.display.update()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:

            sys.exit(0)
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                sys.exit(0)
        
