#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy

#import ros msgs
from sensor_msgs.msg import Imu
from std_msgs.msg import Float64
from ema_common_msgs.msg import Stimulator

# import utilities
from math import pi
from tf import transformations
import time

pedalOrientation = -1
remoteOrientation = -1

#current_milli_time = lambda: int(round(time.time() * 1000))

def pedal_callback(data):
	global pedalOrientation

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	pedalOrientation = euler[0]

	pedalOrientation = pedalOrientation * (180/pi)
    

def remote_callback(data):
	global remoteOrientation

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	remoteOrientation = euler[0]


	remoteOrientation = remoteOrientation * (180/pi)
    	

def threshold():
	global pedalOrientation
	global remoteOrientation

	#lastTime = current_milli_time()

	rospy.init_node('threshold', anonymous = True)
	rospy.Subscriber('imu/pedal', Imu, callback = pedal_callback)
	#rospy.Subscriber('imu/remote', Imu, callback = remote_callback)
	plot = rospy.Publisher('kneeAngle', Float64, queue_size = 10)
	pub = rospy.Publisher('stimulator/ccl_update', Stimulator, queue_size=10)
	
	stimMsg = Stimulator()

	"""
	stimMsg.channel = [1, 2]
	stimMsg.mode = ['single', 'single']
	stimMsg.pulse_current = [4, 4] # currenet in mA
	stimMsg.pulse_width = [0, 0]
	"""
	""" CONTROLE ON-OFF """
	stimMsg.channel = [1]
	stimMsg.mode = ['single']
	stimMsg.pulse_current = [18] # currenet in mA
	stimMsg.pulse_width = [0]
	



	rate = rospy.Rate(100)


	while not rospy.is_shutdown():
		kneeAngle  = pedalOrientation

		"""
		kneeAngle  = remoteOrientation - pedalOrientation

		if remoteOrientation > 30:
			stimMsg.pulse_width[0] = 500 # contrai quadríceps (anterior) caso a perna esteja elevada à frente para esticar o joelho
		else:
			stimMsg.pulse_width[0] = 250 # "meia contração" para estabilidade

		if kneeAngle < 5:
			stimMsg.pulse_width[1] = 500 # contrai o grupo isquiotíbias (posterior)
		"""


		""" CONTROLE ON-OFF """
		if kneeAngle > 180:
			#stimMsg.pulse_width = [500, 500] # pulse width of each channel in us (micro)
			stimMsg.pulse_width = [500] # pulse width of each channel in us (micro)
		else:
			#stimMsg.pulse_width = [0, 0]	
			stimMsg.pulse_width = [abs(500*kneeAngle/180)]
		

		plot.publish(kneeAngle)
		pub.publish(stimMsg)

		rate.sleep()
	

if __name__ == '__main__':
	threshold()