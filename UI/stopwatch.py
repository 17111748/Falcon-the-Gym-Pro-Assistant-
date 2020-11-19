import pygame

class stopwatch(object):
    """
    docstring
    """
    def __init__(self):
        self.timePassed = 0 
        self.paused = True
        self.prevTime = pygame.time.get_ticks()
    
    def start(self):
        if(not self.paused):
            return 
        self.prevTime = pygame.time.get_ticks()
        self.paused = False
    def stop(self):
        if(not self.paused):
            self.timePassed+=pygame.time.get_ticks()-self.prevTime
        self.paused = True
    def reset(self):
        self.stop()
        self.timePassed = 0
    def getTime(self):
        if(self.paused):
            return self.timePassed/1000
        else:
            return (self.timePassed+(pygame.time.get_ticks()-self.prevTime))/1000


