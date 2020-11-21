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
    HISTORY = 5

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
    def __init__(self, x, y, w,h, col, text, textSize = 4,textbox = False):
        self.x = x-w/2
        self.y = y-h/2
        self.textbox = textbox
        self.highlight = False
        #set location of the rectangle which will be updated if needed
        self.rect = (self.x,self.y,w,h)
        self.color = col
        self.text = Text(text,(x,y),w/textSize)

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
        if(self.textbox):
            pygame.draw.rect(d.screen, color.white, self.rect)
            pygame.draw.rect(d.screen, self.color, self.rect, 4)
            self.text.draw(d)
        elif(self.highlight==False):
            pygame.draw.rect(d.screen, self.color,self.rect,2)
            self.text.draw(d)
        else:
            pygame.draw.rect(d.screen,color.lightRed,self.rect)
            pygame.draw.rect(d.screen, self.color, self.rect,4)
            self.text.draw(d)

class TextBox(object):
    def __init__(self,loc,w,h,blankColor):
        self.location = loc
        self.rect = (loc[0],loc[1],w,h)
        self.blankColor = blankColor
        self.typing = False
        self.indicator = ""
        self.text = ""

    def handle_mouse(self):
        pos = pygame.mouse.get_pos()
        isClicked = pygame.mouse.get_pressed()
        isClicked = isClicked[0]
        #check if clicked and within the button
        if(pos[0]>self.rect[0] and pos[0]<self.rect[2]+self.rect[0]\
            and pos[1]>self.rect[1] and pos[1]<self.rect[3]+self.rect[1]):
            if (isClicked):
                return True
        else:
            if(isClicked):
                return False
        return None

    def key_handle(self):
        for event in pygame.event.get():
            if(event.type==pygame.KEYDOWN):
                self.text+=event.unicode

    def draw(self):
        if(self.handle_mouse()):
            self.typing = True
        elif(self.handle_mouse()==False):
            self.typing = False
        if(self.typing):
            self.key_handle()
            pygame.draw.rect(data.screen,color.white, self.rect)
            if((time.time()-data.start_time)%1<0.65):
                self.indicator = "|"
            else:
                self.indicator = ""
            Text(self.text+self.indicator,(self.rect[0],self.rect[1]),size=self.rect[3]/2,color=color.black,topmode=True).draw()
        else:
            pygame.draw.rect(data.screen, self.blankColor, self.rect)
        pygame.draw.rect(data.screen, color.black, self.rect, int(data.width/150))