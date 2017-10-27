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


####### TO DO #######
# - remover do imu.yaml streamming de dados que não esão sendo usados
# - remover o publish do loop da main(). Está publicando acima da taxa de atualização das imus e distorcendo o gráfico

##################################################
##### Máquina de estados #########################
##################################################

def state0():
	# Leva a perna direita para frente e esquerda para trás
	print('state0')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	### PERNA DIREITA ###
	# comando para atuador: flexão do quadril direito
	stimMsg.pulse_width[0] = 0 # relaxa o quadríceps direito
	stimMsg.pulse_width[1] = 500 # contrai o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 500 # levanta o pé direito
	stimMsg.pulse_width[3] = 0 # relaxa panturrilhas direito

	### PERNA ESQUERDA ###
	# comando para atuador: extensão do quadril esquerdo
	stimMsg.pulse_width[4] = 500 # contrai o quadríceps esquerdo
	stimMsg.pulse_width[5] = 0 # relaxa o grupo isquiotíbias (posterior) esquerdo
	stimMsg.pulse_width[6] = 0 # relaxa o pé esquerdo
	stimMsg.pulse_width[7] = 250 # meia contração panturrilhas esquerdo


	if upperRightLegAngle > 30:
		state = state1


def state1():
	# Estica a perna direita à frente
	print('state1')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	### PERNA DIREITA ###
	# comando para atuador: extensão do quadril direito
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps direito
	stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 250 # meia contração do pé direito (calcanhar toca o chão primeiro)
	stimMsg.pulse_width[3] = 0 # relaxa panturrilha direito
	
	### PERNA ESQUERDA ###
	# comando para atuador: estabiliza o quadril esquerdo
	stimMsg.pulse_width[4] = 500 # contrai o quadríceps esquerdo
	stimMsg.pulse_width[5] = 0 # relaxa o grupo isquiotíbias (posterior) esquerdo
	stimMsg.pulse_width[6] = 0 # relaxa o pé esquerdo
	stimMsg.pulse_width[7] = 250 # meia contração panturrilhas esquerdo

	if rightKneeAngle < 5:
		state = state2


def state2():
	# Pisa no chão e executa a passada ate upperRightLeg 0 graus
	print('state2')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	### PERNA DIREITA ###
	# comando para atuador: extensão do quadril direito
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps direito
	stimMsg.pulse_width[1] = 500 # contrai o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 0 # levanta o pé direito
	stimMsg.pulse_width[3] = 250 # meia contração panturrilha direito
	
	### PERNA ESQUERDA ###
	# comando para atuador: estabiliza do quadril esquerdo
	stimMsg.pulse_width[4] = 500 # contrai o quadríceps esquerdo
	stimMsg.pulse_width[5] = 0 # relaxa o grupo isquiotíbias (posterior) esquerdo
	stimMsg.pulse_width[6] = 0 # relaxa o pé esquerdo
	stimMsg.pulse_width[7] = 500 # contrai panturrilhas esquerdo

	if upperRightLegAngle < 0:
		state = state3
	

### A PARTIR DAQUI, O MOVIMENTO É ANALOGO PARA A OUTRA PERNA ###

def state3():
	# Leva a perna esquerda para frente e direita para trás
	print('state3')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	### PERNA DIREITA ###
	# comando para atuador: extensão do quadril direito
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps direito
	stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 0 # levanta o pé direito
	stimMsg.pulse_width[3] = 250 # relaxa panturrilha direito
	
	### PERNA ESQUERDA ###
	# comando para atuador: flexão do quadril esquerdo
	stimMsg.pulse_width[4] = 0 # relaxa o quadríceps esquerdo
	stimMsg.pulse_width[5] = 500 # contrai o grupo isquiotíbias (posterior) esquerdo
	stimMsg.pulse_width[6] = 500 # levanta o pé esquerdo
	stimMsg.pulse_width[7] = 0 # contrai panturrilhas esquerdo

	if upperLeftLegAngle > 30:
		state = state4
		
	
def state4():
	# Estica a perna esquerda à frente
	print('state4')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	### PERNA DIREITA ###
	# comando para atuador: estabiliza do quadril direito
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps direito
	stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 0 # relaxa o pé direito
	stimMsg.pulse_width[3] = 250 # relaxa panturrilha direito
	
	### PERNA ESQUERDA ###
	# comando para atuador: extensão o quadril esquerdo
	stimMsg.pulse_width[4] = 500 # contrai o quadríceps esquerdo
	stimMsg.pulse_width[5] = 0 # relaxa o grupo isquiotíbias (posterior) esquerdo
	stimMsg.pulse_width[6] = 250 # meia contração do pé esquerdo (calcanhar toca o chão primeiro)
	stimMsg.pulse_width[7] = 0 # meia contração panturrilhas esquerdo

	if leftKneeAngle < 5:
		state = state5


def state5():
	# Pisa no chão e executa a passada ate upperLeftLeg 0 graus
	print('state5')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	### PERNA DIREITA ###
	# comando para atuador: estabiliza do quadril direito
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps direito
	stimMsg.pulse_width[1] = 0 # contrai o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 0 # levanta o pé direito
	stimMsg.pulse_width[3] = 500 # relaxa panturrilha direito
	
	### PERNA ESQUERDA ###
	# comando para atuador: extensão do quadril esquerdo
	stimMsg.pulse_width[4] = 500 # contrai o quadríceps esquerdo
	stimMsg.pulse_width[5] = 500 # relaxa o grupo isquiotíbias (posterior) esquerdo
	stimMsg.pulse_width[6] = 0 # relaxa o pé esquerdo
	stimMsg.pulse_width[7] = 250 # contrai panturrilhas esquerdo

	if upperLeftLegAngle < 0:
		state = state0	
	
##################################################
##### Funções de Callback ########################
##################################################

def lowerRightLegAngle_callback(data):
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	lowerRightLegAngle = euler[0]
	lowerRightLegAngle = lowerRightLegAngle * (180/pi)
 
	rightKneeAngle  = upperRightLegAngle - lowerRightLegAngle



def upperRightLegAngle_callback(data):
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	upperRightLegAngle = euler[0]
	upperRightLegAngle = upperRightLegAngle * (180/pi)

	rightKneeAngle  = upperRightLegAngle - lowerRightLegAngle


def lowerLeftLegAngle_callback(data):
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	lowerLeftLegAngle = euler[0]
	lowerLeftLegAngle = lowerLeftLegAngle * (180/pi)
 
	leftKneeAngle  = upperLeftLegAngle - lowerLeftLegAngle



def upperLeftLegAngle_callback(data):
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	global plotRightKnee
	global plotLeftKnee
	global pubStim

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	upperLeftLegAngle = euler[0]
	upperLeftLegAngle = upperLeftLegAngle * (180/pi)

	leftKneeAngle  = upperLeftLegAngle - lowerLeftLegAngle

	# Publica valores para estimulação e gráfico
	plotRightKnee.publish(rightKneeAngle)
	plotLeftKnee.publish(leftKneeAngle)
	pubStim.publish(stimMsg)



##################################################
##### Iniciação de variáveis globais ############
##################################################
lowerRightLegAngle = -1
upperRightLegAngle = -1
rightKneeAngle = -1
lowerLeftLegAngle = -1
upperLeftLegAngle = -1
leftKneeAngle = -1
state = state0
stimMsg = Stimulator()

#[quadrícepsDireito, ísquiosDireito, 'pé caído'Direito, panturrilhaDireito, quadrícepsEsquerdo, ísquiosEsquerdo, 'pé caído'Esquerdo, panturrilhaEsquerdo]
# Nota: músculo do 'pé caído' ativa com facilidade, usar corrente baixa
stimMsg.channel = [1, 2, 3, 4, 5, 6, 7, 8]
stimMsg.mode = ['single', 'single', 'single', 'single', 'single', 'single', 'single', 'single']
stimMsg.pulse_current = [16, 4, 2, 2, 16, 4, 2, 2] # currenet in mA
stimMsg.pulse_width = [0, 0, 0, 0, 0, 0, 0, 0]


##################################################
##### Loop do ROS ################################
##################################################

def stateMachine():
	global state
	global plotRightKnee
	global plotLeftKnee
	global pubStim

	rospy.init_node('stateMachine', anonymous = True)
	rospy.Subscriber('imu/lowerRightLeg', Imu, callback = lowerRightLegAngle_callback)
	rospy.Subscriber('imu/upperRightLeg', Imu, callback = upperRightLegAngle_callback)
	rospy.Subscriber('imu/lowerLeftLeg', Imu, callback = lowerLeftLegAngle_callback)
	rospy.Subscriber('imu/upperLeftLeg', Imu, callback = upperLeftLegAngle_callback)
	plotRightKnee = rospy.Publisher('rightKneeAngle', Float64, queue_size = 10)
	plotLeftKnee = rospy.Publisher('leftKneeAngle', Float64, queue_size = 10)
	pubStim = rospy.Publisher('stimulator/ccl_update', Stimulator, queue_size=10)

	rate = rospy.Rate(100)
	
	#espera terminar calibragem
	rospy.sleep(5)

	while not rospy.is_shutdown():
		state()

		rate.sleep()




if __name__ == '__main__':
	stateMachine()