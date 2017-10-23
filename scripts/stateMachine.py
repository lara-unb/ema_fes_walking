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
# - mudar o nome do node

##################################################
##### Máquina de estados #########################
##################################################

def state0():
	# Começa a caminhada levando a perna direita à frente
	print('state0')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle
	global lowerLeftLegAngle
	global upperLeftLegAngle
	global leftKneeAngle

	# comando para atuador: flexão do quadril direito
	stimMsg.pulse_width[0] = 0 # relaxa o quadríceps direito
	stimMsg.pulse_width[1] = 500 # contrai o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 500 # levanta o pé direito
	stimMsg.pulse_width[3] = 0 # relaxa panturrilhas direito
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

	# comando para atuador: extensão do quadril direito
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps direito
	stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 500 # levanta o pé direito
	stimMsg.pulse_width[3] = 0 # relaxa panturrilha direito
	# comando para atuador: flexão do quadril esquerdo
	stimMsg.pulse_width[4] = 500 # contrai o quadríceps esquerdo
	stimMsg.pulse_width[5] = 0 # relaxa o grupo isquiotíbias (posterior) esquerdo
	stimMsg.pulse_width[6] = 0 # relaxa o pé esquerdo
	stimMsg.pulse_width[7] = 500 # contrai panturrilhas esquerdo

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

	# comando para atuador: extensão do quadril direito
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps direito
	stimMsg.pulse_width[1] = 500 # relaxa o grupo isquiotíbias (posterior) direito
	stimMsg.pulse_width[2] = 0 # levanta o pé direito
	stimMsg.pulse_width[3] = 250 # relaxa panturrilha direito
	# comando para atuador: estabiliza do quadril esquerdo
	stimMsg.pulse_width[4] = 500 # contrai o quadríceps esquerdo
	stimMsg.pulse_width[5] = 0 # relaxa o grupo isquiotíbias (posterior) esquerdo
	stimMsg.pulse_width[6] = 0 # relaxa o pé esquerdo
	stimMsg.pulse_width[7] = 500 # contrai panturrilhas esquerdo

	if upperRightLegAngle < 0:
		state = state3
	

def state3():
	# Termina a passada até -15 e contrai panturrilha para jogar o corpo para frente
	print('state3')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle

	# comando para atuador: extensão do quadril
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps
	stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior)
	stimMsg.pulse_width[2] = 0 # relaxa o pé
	stimMsg.pulse_width[3] = 500 # contrai a panturrilha
	
	if upperRightLegAngle < -10:
		#state = state4
		#caso espere sinal da outra perna, já estável no chão
		state = state0
		#se não, recomeça o movimento
	
	
def state4():
	# Termina a passada até -15 e contrai panturrilha para jogar o corpo para frente
	print('state4')
	global state
	global stimMsg
	global lowerRightLegAngle
	global upperRightLegAngle
	global rightKneeAngle

	# comando para atuador: mantem a posição do do quadril
	stimMsg.pulse_width[0] = 500 # contrai o quadríceps
	stimMsg.pulse_width[1] = 0 # relaxa o grupo isquiotíbias (posterior)
	stimMsg.pulse_width[2] = 0 # relaxa o pé
	stimMsg.pulse_width[3] = 500 # contrai a panturrilha

	# sinalDaOutraPerna (bool) indica que a outra perna já está estável no chão
	#if sinalDaOutraPerna:
	#	state = state0
		
	
##################################################
##### Funções de Callback ########################
##################################################

def lowerRightLegAngle_callback(data):
	global lowerRightLegAngle
	global rightKneeAngle

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	lowerRightLegAngle = euler[0]
	lowerRightLegAngle = lowerRightLegAngle * (180/pi)
 
	rightKneeAngle  = upperRightLegAngle - lowerRightLegAngle



def upperRightLegAngle_callback(data):
	global upperRightLegAngle
	global rightKneeAngle

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	upperRightLegAngle = euler[0]
	upperRightLegAngle = upperRightLegAngle * (180/pi)

	rightKneeAngle  = upperRightLegAngle - lowerRightLegAngle


def lowerLeftLegAngle_callback(data):
	global lowerLeftLegAngle
	global leftKneeAngle

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	lowerLeftLegAngle = euler[0]
	lowerLeftLegAngle = lowerLeftLegAngle * (180/pi)
 
	leftKneeAngle  = upperLeftLegAngle - lowerLeftLegAngle



def upperLeftLegAngle_callback(data):
	global upperLeftLegAngle
	global leftKneeAngle

	qx,qy,qz,qw = data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w
	euler = transformations.euler_from_quaternion([qx, qy, qz, qw], axes='syxz')

	upperLeftLegAngle = euler[0]
	upperLeftLegAngle = upperLeftLegAngle * (180/pi)

	leftKneeAngle  = upperLeftLegAngle - lowerLeftLegAngle


##################################################
##### Iniciação de variáveis globais ############
##################################################
lowerRightLegAngle = -1
upperRightLegAngle = -1
rightKneeAngle = -1
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

	rospy.init_node('stateMachine', anonymous = True)
	rospy.Subscriber('imu/lowerRightLeg', Imu, callback = lowerRightLegAngle_callback)
	rospy.Subscriber('imu/upperRightLeg', Imu, callback = upperRightLegAngle_callback)
	rospy.Subscriber('imu/lowerLeftLeg', Imu, callback = lowerLeftLegAngle_callback)
	rospy.Subscriber('imu/upperLeftLeg', Imu, callback = upperLeftLegAngle_callback)
	plot = rospy.Publisher('rightKneeAngle', Float64, queue_size = 10)
	plot1 = rospy.Publisher('upperRightLegAngle', Float64, queue_size = 10)
	pub = rospy.Publisher('stimulator/ccl_update', Stimulator, queue_size=10)

	rate = rospy.Rate(100)
	
	#espera terminar calibragem
	rospy.sleep(5)

	while not rospy.is_shutdown():
		state()

		# Publica valores para estimulação e gráfico
		plot.publish(rightKneeAngle)
		plot1.publish(upperRightLegAngle)
		pub.publish(stimMsg)

		rate.sleep()




if __name__ == '__main__':
	stateMachine()