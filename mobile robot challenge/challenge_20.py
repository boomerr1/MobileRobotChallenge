from picamera2 import Picamera2, Preview
import picar_4wd as fc
import time
from imutils import paths
import imutils
import numpy as np
import cv2
import PIL.Image
import matplotlib.pyplot as plt

from challenge_11 import estimate_distance, drive_distance

def turn_deg(direction, degrees=90):
	ninety_deg_time = 0.94
	if direction == 'r':
		fc.turn_right(20)
	else :
		fc.turn_left(20)
	time.sleep(degrees/90*ninety_deg_time)
	#time.sleep(1.29)
	fc.stop()
		
if __name__ == '__main__':
	


	distance, drive_object_time = estimate_distance()

	drive_distance(drive_object_time-0.5)

	turn_deg('r')

	drive_distance(1)

	turn_deg('l')

	drive_distance(2.5)

	turn_deg('l')

	drive_distance(1)

	turn_deg('r')

	drive_distance(drive_object_time)
