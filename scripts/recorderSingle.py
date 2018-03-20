#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy

#usar
#rostopic echo /ema_tao/kneeAngle/data > kneeAngle.txt
#rostopic echo /ema_tao/upperLeg/data > upperLeg.txt

#import ros msgs
from sensor_msgs.msg import Imu
from std_msgs.msg import Float64
#from geometry_msgs.msg import Quaternion

# import utilities
from math import pi
from tf import transformations

	
##################################################
##### Funções de Callback ########################
##################################################

def bodyAngle_callback(data):
	global pubUpperLegAngle
	global pubUpperLegAngle1
	global pubUpperLegAngle2
	
	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	pubUpperLegAngle.publish(euler[0] * (180/pi))



##################################################
##### Loop do ROS ################################
##################################################

def recorder():
	global pubUpperLegAngle
	global pubUpperLegAngle1
	global pubUpperLegAngle2

	rospy.init_node('recorder', anonymous = True)
	pubUpperLegAngle = rospy.Publisher('upperLegAngle', Float64, queue_size = 10)
	rospy.Subscriber('imu/angle', Imu, callback = bodyAngle_callback)

	rate = rospy.rate(50)

	while not rospy.is_shutdown():
		rate.sleep()
		pass



if __name__ == '__main__':
	recorder()