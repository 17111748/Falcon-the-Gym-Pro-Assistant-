import enum
import pygame
from UI.colors import *
import os

class data(object):
    pass

class screenMode(enum.Enum):
    MAIN = 1
    WORKOUT = 2
    PAUSE = 3
    SUMMARY = 4
    HISTORYSUMMARY = 5
    HISTORYOPTIONS = 6
    HISTORYTRENDS = 7

class Text(object):
    def __init__(self,text,location, size = 60,col = color.white,topmode = False,transparent=False):
        self.location = location
        self.myfont = pygame.font.Font(os.path.join("UI", "resources", "SFProDisplay-Thin.ttf"), int(size))
        self.label = self.myfont.render((text), True, col, color.white)
        if(transparent):
            self.label = self.myfont.render((text), True, col, None)
        self.text_rect = self.label.get_rect(center=location)
        #topmode means anchored to top left 
        self.topmode = topmode
    def draw(self,d):
        if(self.topmode==False):
            d.screen.blit(self.label, self.text_rect)
        else:
            d.screen.blit(self.label,self.location)

class Button(object):
    #initializes button
    def __init__(self, x, y, w, h, col, text, textSize = 32, info = None):
        self.x = x-w/2
        self.y = y-h/2
        self.highlight = False
        #set location of the rectangle which will be updated if needed
        self.rect = (self.x,self.y,w,h)
        self.color = col
        self.textSize = textSize
        self.text = text
        self.textLoc = (x,y)
        self.info = info

    def handle_mouse(self):
        #wait so that code doesnt mess up
        # pygame.event.wait()
        pos = pygame.mouse.get_pos()
        isClicked = pygame.mouse.get_pressed()
        isClicked = isClicked[0]
        #check if clicked and within the button
        if(pos[0]>self.rect[0] and pos[0]<self.rect[2]+self.rect[0]\
            and pos[1]>self.rect[1] and pos[1]<self.rect[3]+self.rect[1]):
            if (isClicked):
                return True
            else:
                self.highlight = True
        else:
            self.highlight = False
        return False

    def draw(self,d):
        tempText = None
        if(self.highlight==False):
            pygame.draw.rect(d.screen, self.color,self.rect, 2, border_radius=10)
            tempText = Text(self.text,self.textLoc,self.textSize, color.black)
        else:
            pygame.draw.rect(d.screen, self.color, self.rect,width=4,border_radius=10)
            tempText = Text(self.text,self.textLoc,self.textSize+2, color.black)

        tempText.draw(d)

class ImageButton(Button):
    def __init__(self, x, y, w, h, col, text, normalImg, highlightedImg, textSize = 32, info = None):
        super().__init__(x, y, w, h, col, text, textSize, info)
        self.normalImg = normalImg
        self.highlightedImg = highlightedImg
        self.w = w
        self.h = h 
    
    def draw(self,d):
        if(self.highlight==False):
            img = pygame.image.load(self.normalImg)
            scaledImg = pygame.transform.scale(img, (self.w, self.h))
            d.screen.blit(scaledImg, (self.x, self.y))
            pygame.draw.rect(d.screen, self.color,self.rect, 2, border_radius=10)
            tempText = Text(self.text,self.textLoc,self.textSize, color.black)
        else:
            img = pygame.image.load(self.highlightedImg)
            scaledImg = pygame.transform.scale(img, (self.w, self.h))
            d.screen.blit(scaledImg, (self.x, self.y))
            pygame.draw.rect(d.screen, self.color, self.rect,width=4,border_radius=10)
            tempText = Text(self.text,self.textLoc,self.textSize+2, color.black)