import picar_4wd as fc
import time
from challenge_1 import estimate_distance, drive_distance

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
