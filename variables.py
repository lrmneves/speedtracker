import cv2
import os

winName = "Movement Indicator"
video = "videos/video1.mov"



#video1
areaOfInterest = [(300,250),(800,630)] 
#video2
# areaOfInterest = [(100,100),(250,200)] 
#video3
# areaOfInterest = [(100,150),(250,250)] 

x0 = areaOfInterest[0][0]
x1 = areaOfInterest[1][0]
y0 = areaOfInterest[0][1]
y1 = areaOfInterest[1][1]
#define in meter the aprox width of the area
#video1
areaOfInterestWidth = 8
#video 2
# areaOfInterestWidth = 4
#video 3
# areaOfInterestWidth = 4

#direction of the cars
LEFT_TO_RIGHT = "leftToRight"
RIGHT_TO_LEFT = "rightToLeft"
TOP_DOWN = "topDown"
BOTTOM_UP = "bottomUp"
direction = LEFT_TO_RIGHT

importantPoints = []
carList = []


threshold = 50

font = cv2.FONT_HERSHEY_SIMPLEX

