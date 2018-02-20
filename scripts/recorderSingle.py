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
	pubUpperLegAngle1.publish(euler[1] * (180/pi))
	pubUpperLegAngle2.publish(euler[2] * (180/pi))



##################################################
##### Loop do ROS ################################
##################################################

def recorder():
	global pubUpperLegAngle
	global pubUpperLegAngle1
	global pubUpperLegAngle2

	rospy.init_node('recorder', anonymous = True)
	pubUpperLegAngle = rospy.Publisher('upperLegAngle', Float64, queue_size = 10)
	pubUpperLegAngle1 = rospy.Publisher('upperLegAngle1', Float64, queue_size = 10)
	pubUpperLegAngle2 = rospy.Publisher('upperLegAngle2', Float64, queue_size = 10)
	rospy.Subscriber('imu/angle', Imu, callback = bodyAngle_callback)

	while not rospy.is_shutdown():
		pass



if __name__ == '__main__':
	recorder()