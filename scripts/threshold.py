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

def state0():
	global state
	global stimMsg
	global pedalOrientation
	global remoteOrientation

	kneeAngle  = remoteOrientation - pedalOrientation

	# Leva perna direita à frente
	while remoteOrientation < 15:
		# comando para atuador: flexão do quadril
		stimMsg.pulse_width[0] = 0 # relaxa o quadríceps
		stimMsg.pulse_width[1] = 500 # contrai o grupo isquiotíbias (posterior)
		stimMsg.pulse_width[2] = 500 # levanta o pé

	state = state1

def state1():
	global state
	global stimMsg
	global pedalOrientation
	global remoteOrientation

	kneeAngle  = remoteOrientation - pedalOrientation

	# Estica a perna à frente
	while kneeAngle > 30:
		# comando para atuador: flexão do quadril
		stimMsg.pulse_width[0] = 500 # contrai o quadríceps
		stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior)
		stimMsg.pulse_width[2] = 500 # levanta o pé
		stimMsg.pulse_width[3] = 0 # relaxa panturrilha

	state = state2


def state2():
	global state
	global stimMsg
	global pedalOrientation
	global remoteOrientation
	
	# Pisa no chão e executa a passada ate 0o
	while remoteOrientation > 0:
		# comando para atuador: extensão do quadril
		stimMsg.pulse_width[0] = 500 # contrai o quadríceps
		stimMsg.pulse_width[1] = 500 # contrai o grupo isquiotíbias (posterior)
		stimMsg.pulse_width[2] = 0 # relaxa o pé
		stimMsg.pulse_width[3] = 250 # meia contração da panturrilha

	state = state3
	####### SINAL PARA RECOMEÇAR O CICLO DA OUTRA PERNA ######
	

def state3():
	global state
	global stimMsg
	global pedalOrientation
	global remoteOrientation

	# Termina a passada até -15 e contrai panturrilha para jogar o corpo para frente
	while remoteOrientation > -15:
		# comando para atuador: extensão do quadril
		stimMsg.pulse_width[0] = 500 # contrai o quadríceps
		stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior)
		stimMsg.pulse_width[2] = 0 # relaxa o pé
		stimMsg.pulse_width[3] = 500 # contrai a panturrilha

	state = state4
	
	
def state4():
	global state
	global stimMsg
	global pedalOrientation
	global remoteOrientation

	# Termina a passada até -15 e contrai panturrilha para jogar o corpo para frente
	while True:
		# comando para atuador: mantem a posição do do quadril
		stimMsg.pulse_width[0] = 500 # contrai o quadríceps
		stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior)
		stimMsg.pulse_width[2] = 0 # relaxa o pé
		stimMsg.pulse_width[3] = 500 # contrai a panturrilha

		# sinalDaOutraPerna (bool) indica que a outra perna já está estável no chão
		if sinalDaOutraPerna:
			break

	state = state0
	

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
    	

pedalOrientation = -1
remoteOrientation = -1
state = state0
stimMsg = Stimulator()
#[quadríceps, ísquios, 'pé caído', panturrilha]
# Nota: músculo do 'pé caído' ativa com facilidade, usar corrente baixa
stimMsg.channel = [1, 2, 3, 4]
stimMsg.mode = ['single', 'single', 'single', 'single']
stimMsg.pulse_current = [16, 4, 2, 2] # currenet in mA
stimMsg.pulse_width = [0, 0, 0, 0]


def threshold():
	global state


	rospy.init_node('threshold', anonymous = True)
	rospy.Subscriber('imu/pedal', Imu, callback = pedal_callback)
	rospy.Subscriber('imu/remote', Imu, callback = remote_callback)
	plot = rospy.Publisher('kneeAngle', Float64, queue_size = 10)
	pub = rospy.Publisher('stimulator/ccl_update', Stimulator, queue_size=10)

	rate = rospy.Rate(100)

	while not rospy.is_shutdown():
		state()
		rate.sleep()

		plot.publish(kneeAngle)
		plot.publish(remoteOrientation)
		pub.publish(stimMsg)

if __name__ == '__main__':
	threshold()