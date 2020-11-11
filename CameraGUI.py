import os.path
from guizero import App,Text,Combo,Picture
from picamera import PiCamera
#from time import sleep
from os import path

#default Values for GUI
#NOTE: CHANGE VALUES HERE ONLY IF YOU ABSOLUTELY MUST AS THINGS COULD BREAK IN THE GUI. BETTER TO CHANGE IN THE GUI OTHERWISE
defaultCaptureInterval = 60
defaultTimeLapseInterval = 10
defaultCaptureRes = (1280, 720)
defaultSaveRes = (32,32)

#main picamera reference
picamera = PiCamera()
previewResolution = (800, 480)

#time without activity after which app goes into preview mode
idleTimer = 30

#tracker to keep the images captured since the script began
imageCount = 0

#tracker to track which image is being shown
timeLapseIndex = 0

#captureInterval value: changing this changes the frequency at which the camera captures the images
captureInterval = defaultCaptureInterval

#resolution tracker for changing the resolution of the image we capture
captureRes = defaultCaptureRes



#resolution to be used for scientific capture
saveRes = defaultSaveRes

#sets the rate at which images change in the timelapse
timeLapseInterval = defaultTimeLapseInterval

#main file path for saving and retrieving images for timelapse
timeLapsePath = '/home/pi/Desktop/Camera Module/TimeLapse Images/'

#main file path for saving resized images for analysis
scientificResPath = '/home/pi/Desktop/Camera Module/Scientific Images/'

#ImageTitle to be used fop all images captured
imageTitle = 'Image'

#file format to be used for all images captured
imageFormat = '.jpg'

#function to update the app to use the new capture interval
# Warning : when changing the value the function will capture after whole new time interval has passed ignoring the previous interval's duration
def CaptureInterval_Selected(selected_value):
    global captureInterval, GUIApp
    
    #global CaptureImage
    captureInterval = int(selected_value)
    GUIApp.cancel(CaptureImage)
    
    GUIApp.repeat(1000*captureInterval, CaptureImage)
    
    

#function to update the app to use the new camera resolution for capturing the subsequent stills
def CaptureResolution_Selected(selected_value):
    global captureRes
    
    arr = selected_value.split("x")
    captureRes = (int(arr[0]), int(arr[1]))
    print(str(captureRes[0]) + "," + str(captureRes[1]))
    

#function to update the app to use the new reize value
def SaveResolution_Selected(selected_value):
    global saveRes
    
    arr = selected_value.split("x")
    saveRes = (int(arr[0]), int(arr[1])) 
    

#function to update the app to use the new time lapse interval
# Warning : when changing the value the function will change only after whole new time interval has passed ignoring the previous intervals duration
def TimeLapseInterval_Selected(selected_value):
    global timeLapseInterval,TimeLapseImage
    
    timeLapseInterval = int(selected_value)
    TimeLapseImage.cancel(TimeLapse)
    TimeLapseImage.repeat(timeLapseInterval * 1000, TimeLapse)
    
    
#function to capture image stills for both the timelapse as well as the analysis folder everytime its called
def CaptureImage():
    global GUIApp, captureInterval, picamera, imageCount, captureRes
    global timeLapsePath, scientificResPath, imageTitle, imageFormat
    
    print(str(captureRes[0]) + "," + str(captureRes[1]))
    picamera.resolution = captureRes
    
    name = imageTitle + str(imageCount) + imageFormat
    
    #capture Scientific version first without any anotations
    picamera.capture(scientificResPath + name, resize = (saveRes))
    
    #capture TimeLapse Image with anotation
    picamera.annotate_text = name
    picamera.capture(timeLapsePath + name)
    imageCount += 1
    picamera.resolution = previewResolution
    picamera.annotate_text = ""
    

#function to switch image shown in the GUI over a certain interval 
def TimeLapse():
    global imageCount, timeLapseIndex, TimeLapseImage, timeLapsePath
    global imageTitle, imageFormat
    if timeLapseIndex>=imageCount:
        timeLapseIndex = 0
    imagePath = timeLapsePath + imageTitle +  str(timeLapseIndex) + imageFormat
    if os.path.isfile(imagePath):
        TimeLapseImage.value = imagePath
    timeLapseIndex += 1

def On_click():
    global GUIApp, picamera, idleTimer
    GUIApp.cancel(On_Idle)
    print("On Click Event Running")
    GUIApp.after(idleTimer * 1000,On_Idle)
    picamera.stop_preview()
    
def On_Idle():
    global picamera
    picamera.start_preview(fullscreen = True , rotation = 270, alpha = 255)

#function to clear out any scheduled calls before closing the GUI APP
def Closed():
    global GUIApp, TimeLapseImage, picamera
    
    #print("running when closed")
    picamera.stop_preview()
    TimeLapseImage.cancel(TimeLapse)
    GUIApp.cancel(On_Idle)
    GUIApp.cancel(CaptureImage)
    GUIApp.destroy()


#get camera preivew
picamera.resolution = previewResolution
picamera.start_preview(fullscreen = True , rotation = 270, alpha = 255)

#sleep(5)

#main gui App    
GUIApp = App(title = "GUI APP" , width = 800, height = 480, layout = "grid")
GUIApp.when_clicked = On_click
#click the first set of images for preview on screen
CaptureImage();


#schedule calls to capture images at the starting interval
GUIApp.repeat(captureInterval*1000,CaptureImage)
GUIApp.when_closed = Closed

#capture interval GUI for changing the Capture rate of the camera.
CaptureIntervalTitle = Text(GUIApp, text = "Capture Interval",grid = [0,0],width = 22, height = 2)
CaptureIntervalCombo = Combo(GUIApp, grid = [0,1], width = 8, height = 1 , options = ["30","60","90","120","180","240","300"], selected = str(captureInterval), command = CaptureInterval_Selected)

#capture Resolution GUI for chainging the resolution at which the stills are captured
CaptureResolutionTitle = Text(GUIApp, text = "Capture Resolution", grid = [1,0], width = 22, height = 2)
CaptureResCombo = Combo(GUIApp, width = 10 , height = 1, options = ["2048x1536", "1920x1080", "1280x720", "1640x1232", "3280x2464"], selected = (str(captureRes[0]) + "x" + str(captureRes[1])),grid= [1,1], command = CaptureResolution_Selected)

#save Resolution GUI for changing the resize resolution for analysis of the image
SaveResolutionTitle1 = Text(GUIApp, text = "Save Resolution", grid = [2,0], width = 22, height = 1)
SaveResCombo = Combo(GUIApp, width = 10 , height = 1, options = ["16x16","32x32", "64x64", "128x128", "256x256"], grid= [2,1], selected = (str(saveRes[0]) + "x" + str(saveRes[1])), command = SaveResolution_Selected)

#Time lapse interval GUI for changing the rate at which image changes in the app
TimeLapseTitle = Text(GUIApp, text = "Timelapse Interval", grid = [3,0], width = 22, height = 1)
TimeLapseIntervalCombo = Combo(GUIApp, width = 10 , height = 1, options = ["5","10","20","30","40","50","60"], selected = str(timeLapseInterval), grid= [3,1], command = TimeLapseInterval_Selected)
 
EmptySpace = Text(GUIApp, text = " ", grid = [0,2,4,1], height = 1)
 
#Image GUI for displaying the timelapse Image 
TimeLapseImage = Picture(GUIApp, image = timeLapsePath + imageTitle + "0" + imageFormat, grid = [0,3,4,1], width = 780, height = 450)
TimeLapseImage.repeat(timeLapseInterval*1000, TimeLapse)

#GUIApp.full_screen = True
GUIApp.display()


