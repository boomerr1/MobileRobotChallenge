
from picamera2 import Picamera2, Preview
import picar_4wd as fc
import time
import imutils
import numpy as np
import cv2

def capture():
	picam2 = Picamera2()
	camera_config = picam2.create_preview_configuration()
	picam2.configure(camera_config)
	picam2.start()
	image_4_channels = picam2.capture_array("main")
	picam2.close()
	return image_4_channels
	
def show(image):
	cv2.imshow("Show",image)
	cv2.waitKey()  
	cv2.destroyAllWindows()
	
def detect_obj(image):
	pass
	

def estimate_distance(plot=True):
	FOCAL_LENGTH = 4.74 # in mm
	REAL_HEIGHT = 70 # in mm
	IMAGE_HEIGHT = 480 # in px
	SENSOR_HEIGHT = 3.63 # in mm
	HEIGHT_OFFSET = 130
	tr = 0.2

	image_4_channels = capture()
	image_4_channels = image_4_channels[180:-80, 213:-213]
	#image_4_channels = image_4_channels[220:-60]

	gray = cv2.cvtColor(image_4_channels, cv2.COLOR_BGR2GRAY)
	gray = cv2.medianBlur(gray, 5)
	edged = cv2.Canny(gray, 35, 125)

	sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
	sharpen = cv2.filter2D(edged, -1, sharpen_kernel)

	thresh = cv2.threshold(sharpen, 160, 255, cv2.THRESH_BINARY_INV)[1]
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
	close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

	contours = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	contours = imutils.grab_contours(contours)
		
	c = max(contours, key=cv2.contourArea)
	
	x,y,w,h = cv2.boundingRect(c)
		#cv2.rectangle(image_4_channels,(x,y),(x+w,y+h),(0,255,0),2)
	cv2.rectangle(image_4_channels,(x,y),(x+w,y+h),(0,255,0),2)
	
	if plot:
		show(image_4_channels)
		#show(sharpen)
		
	
	distance = (FOCAL_LENGTH * REAL_HEIGHT * IMAGE_HEIGHT) / (h * SENSOR_HEIGHT)

	true_distance = np.sqrt(HEIGHT_OFFSET**2 + distance**2)
	print('distance without correction:',true_distance)

	error = (true_distance - 962)*0.155
	true_distance -= error
	true_distance -= 62
	drive_object_time = (distance + error - 250) / 285
	print('distance with correction:',round(true_distance/10+5, 1), 'cm')
	if input("drive? (y/n)") == "n":
		quit()

	return true_distance, drive_object_time

def drive_distance(drive_object_time):
	# distance_travelled = 285 # in mm
	fc.forward(20)
	time.sleep(drive_object_time)
	fc.stop()
	time.sleep(0.2)

def main():
	distance, drive_object_time = estimate_distance()
	drive_distance(drive_object_time)


if __name__ == "__main__":
	main()
