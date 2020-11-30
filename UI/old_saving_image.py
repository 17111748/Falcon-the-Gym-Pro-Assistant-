import sys, pygame, cv2
from structs import *
from colors import *

def init(d):
    #constants
    d.FRAME_FREQUENCY = 100
    d.WINDOW_WIDTH = 1280
    d.WINDOW_HEIGHT = int(d.WINDOW_WIDTH/1.6)
    d.LIVE_VIDEO_DIMS = (int(d.WINDOW_WIDTH*0.5),int(d.WINDOW_HEIGHT*0.5))
    d.IMAGE_DIR = '/Users/vishalbaskar/OneDrive/Documents/School/College/2020-2021/18-500/Falcon-the-Gym-Pro-Assistant-/UI/images/leg_raise/'

    #setup pygame/camera
    d.camera  = cv2.VideoCapture(0)
    # d.camera = cv2.VideoCapture(1)
    if not d.camera.isOpened():
        print("Could not open video device")
    pygame.init()
    pygame.display.set_caption("OpenCV camera stream on Pygame")
    screen = pygame.display.set_mode([d.WINDOW_WIDTH, d.WINDOW_HEIGHT])
    d.screen = screen
    d.live_video = pygame.Surface(d.LIVE_VIDEO_DIMS)
    d.clock = pygame.time.Clock()

    #if focused on core then that is 4 sets rest is 3
    d.workoutSets = {
        "core": ["c","u","l","c","u","l","c","u","l","c"],
        "upper": ["u","c","l","u","c","l","u","c","l","u"],
        "leg": ["l","c","u","l","c","u","l","c","u","l"],
        "all_leg_temp": ["l","l","l","l","l","l","l","l","l","l"]
    }
    d.workoutFocus = "all_leg_temp"
    d.currSet = 0

    d.currWorkoutFrame = 0
    d.currentRep = 0 

    d.workoutTotalFrames = {
        "l": 120, 
        "c": 30,
        "u": 30
    }

    d.font = pygame.font.Font('freesansbold.ttf', 32) 

    d.currentScreen = screenMode.WORKOUT
    d.newScreen = True

def drawMain(d):
    if(d.newScreen):
        #draw start and settings
        #draw 
        d.screen.fill(color.white)
        d.newScreen = False

def drawWorkout(d):
    if(d.newScreen):
        d.currWorkoutFrame = 0
        d.currentRep = 0 
        d.screen.fill(color.white)
        repText = d.font.render("Rep: "+str(d.currentRep)+"/10", True, color.green, color.blue) 
        textRect = repText.get_rect()  
        textRect.center = (int(d.WINDOW_WIDTH / 1.5), int(d.WINDOW_HEIGHT / 4))
        d.screen.blit(repText, textRect)
        d.newScreen = False
    #incrementing rep
    if(d.workoutRepFrame>=d.legRaiseFrameCount):
        #adjusting rep
        d.currentRep+=1   
        d.currWorkoutFrame=0
        if(d.currentRep>=10):
            d.currentRep = 0 
            d.currSet+=1
            if(d.currSet>=10):
                #TODO: code to go to workout summary screen
                return True
            #scenario to go to next set will call new screen again from main method
            return True
    d.screen.blit(pygame.image.load(d.IMAGE_DIR+"{:03n}".format(d.currWorkoutFrame)+'.gif'),(0,0))
    d.currWorkoutFrame+=1

    ret, frame = d.camera.read()
    if(ret is False): break
    else:
        total_frame+=1
        frame = cv2.resize(frame, d.LIVE_VIDEO_DIMS, interpolation = cv2.INTER_AREA)

    frame = frame.swapaxes(0,1)
    frame = cv2.flip(frame,0)
    d.screen.blit(d.live_video, (d.WINDOW_WIDTH*0.45,d.WINDOW_HEIGHT*0.325))
    pygame.surfarray.blit_array(d.live_video, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


def main(d):
    total_frame = 0 
    photo_ID = 0 
    while True:
        if(d.currentScreen == screenMode.MAIN):
            drawMain(d) 
        elif(d.currentScreen == screenMode.WORKOUT):
            # create a text suface object, 
            # on which text is drawn on it. 
            repText = d.font.render("Rep: "+str(d.currentRep)+"/10", True, color.green, color.blue) 
            
            # create a rectangular object for the 
            # text surface object 
            textRect = repText.get_rect()  
            
            # set the center of the rectangular object. 
            textRect.center = (int(d.WINDOW_WIDTH / 1.5), int(d.WINDOW_HEIGHT / 4))
            d.screen.blit(repText, textRect)

            #updating workout gif
            if(d.workoutRepFrame>=d.legRaiseFrameCount):
                d.currentRep+=1   
                d.workoutRepFrame=d.workoutRepFrame%d.legRaiseFrameCount
            d.screen.blit(pygame.image.load(d.IMAGE_DIR+"{:03n}".format(d.workoutRepFrame)+'.gif'),(0,0))
            d.workoutRepFrame+=1

            ret, frame = d.camera.read()
            if(ret is False): break
            else:
                total_frame+=1
                frame = cv2.resize(frame, d.LIVE_VIDEO_DIMS, interpolation = cv2.INTER_AREA)

            frame = frame.swapaxes(0,1)
            frame = cv2.flip(frame,0)
            d.screen.blit(d.live_video, (d.WINDOW_WIDTH*0.45,d.WINDOW_HEIGHT*0.325))
            pygame.surfarray.blit_array(d.live_video, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


            #saving photos and sending through UART
            if total_frame%d.FRAME_FREQUENCY == 0:
                photo_ID += 1
                image_name = str(photo_ID) +'.jpg'

                cv2.imwrite(image_name, frame.swapaxes(0,1))
                #albert downscale and send to uart?
                #might need to thread this process if downscale and sending takes a while

            #ensures between every call of this function at least 1/60 seconds have passed (allows for 60fps movie)
            #loading an image limits frame rate to be 33ms between iterations or around 30fps or 33ms between frames at min
        
        pygame.display.update()
        pygameCheckQuit()
        d.clock.tick(30)
        total_frame+=1

def pygameCheckQuit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                sys.exit(0)

data = data()
init(data)
main(data)