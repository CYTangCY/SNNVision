import time
import argparse

import cv2
import numpy as np

from snn import SNN
from timer import FPS
from Stream import VideoStreamMono
from ImageProcessing import Algorithm
import Graphics
import opticalmodule
from timeit import default_timer as timer

frameHW = (160, 120)
frameRate = 30
fourcc = cv2.VideoWriter_fourcc(*"MJPG")

#saver setting
#saver = cv2.VideoWriter('output2' + '.avi', fourcc, 30, (640, 480))
saver = None

#resolution setting
width = int(160)
height = int(120)

#SNN model setting
snn = SNN("lif", 1)

#display activity
#spikes = [0]
#guiSpike = Graphics.Spike(snn.getNumNeurons())

#display potential
#potentials = [0]
#guiPotential = Graphics.Potential(snn.getNumNeurons())

#display obstacle
guiObstacle = Graphics.Obstacle(threshold1 = 7, threshold2 = 10, saver=saver)

   
time.sleep(2.0)
vs = VideoStreamMono("video.mkv", usePiCamera=False, resolution=frameHW, framerate=frameRate).start()

#setting IMU data
pose = open('pose.txt', 'r')

#setting Virtual wall
wall = np.loadtxt('wall.txt')

algo = Algorithm()
[ret, raw, _, prvs] = vs.read()


focalLength = min(height, width)/2/np.tan(35/180*np.pi)
K = np.array([[focalLength, 0.0, width/2],
			 [0.0, focalLength, height/2],
			 [0.0, 0.0, 1.0]])

ptime, ptx, pty, ptz, prx, pry = 261.03900, 785.56394, 4.00000, -206.83414, np.radians(-1.35001), np.radians(164.10004)

start = timer()
frame_count = 0
time_flow = 0
time_rt = 0
time_depth = 0
FDthreshold = 6


fps = FPS().start()
localfps = FPS().start()
realtimeFPS = 0
counter = 0

[ret, raw, _, curr] = vs.read()
key = cv2.waitKey(1)
for line in pose:
	[ret, raw, _, curr] = vs.read()

	time, tx_, ty_, tz_, rx_, ry_ = line.split()
	time = float(time)
	
	tx, ty, tz, rx, ry = float(tx_), float(ty_), float(tz_), np.radians(float(rx_)), np.radians(float(ry_))
	   
	# rotation in radius
	Rh = np.array([[1,			0,			 0],
				  [ 0, np.cos(prx), -np.sin(prx)],
				  [ 0, np.sin(prx),  np.cos(prx)]])
	Ry = np.array([[np.cos(ry-pry), 0, np.sin(ry-pry)],
				  [		  0,	  1,			   0],
				  [-np.sin(ry-pry), 0, np.cos(ry-pry)]])
	Rx = np.array([[1,		   0,			0],
				  [ 0, np.cos(-rx), -np.sin(-rx)],
				  [ 0, np.sin(-rx),  np.cos(-rx)]])
	RI = np.eye(3, 3)
	
	# translation in meters
	xd, yd, zd = tx-ptx, ty-pty, tz-ptz
	zd = -zd
	translation = [np.sqrt(xd**2+yd**2+zd**2)*np.sin(np.arctan2(np.sqrt(xd**2+zd**2),yd)-rx)*np.cos(np.pi/2+np.arctan2(-xd,zd)+ry),
			np.sqrt(xd**2+yd**2+zd**2)*np.cos(np.arctan2(np.sqrt(xd**2+zd**2),yd)-rx),
			np.sqrt(xd**2+yd**2+zd**2)*np.sin(np.arctan2(np.sqrt(xd**2+zd**2),yd)-rx)*np.sin(np.pi/2+np.arctan2(-xd,zd)+ry)]
	translation = np.array(translation).reshape(3, 1)
	translation_O = [0, 0, 0]
	translation_O = np.array(translation_O).reshape(3, 1)

	# Rt = [R|t]
	Rt_rotate = np.concatenate((Rh @ Ry @ Rx, translation_O), axis=1)
	Rt_translate = np.concatenate((RI, translation), axis=1)
	
	start_flow = timer()
				  
	# calculate optical flow 
	OptFlow = algo.calculateOpticalFlow(prvs, curr).flatten()
	OptFlow = opticalmodule.reshapearray(OptFlow,width,height)
	meanOptFlow = opticalmodule.meanFlow(OptFlow,width,height).flatten()
	meanmeanOptFlow = opticalmodule.meanmeanFlow(meanOptFlow)
	OBOptFlow = np.abs(meanmeanOptFlow)
	norOptFlow = [ normO / 10 for normO in OBOptFlow ]
	
	#idealRotation Flow
	idealRotateFlow = opticalmodule.RYP(wall, K, Rt_rotate,width,height).flatten()
	idealRotateFlow = opticalmodule.reshapearray(idealRotateFlow,width,height)
	meanIRFlow = opticalmodule.meanFlow(idealRotateFlow,width,height).flatten()
	meanmeanIRFlow = opticalmodule.meanmeanFlow(meanIRFlow)
	OBIRFlow = np.abs(meanmeanIRFlow)
	norIRFlow = [ normR / 10 for normR in OBIRFlow ]
	
	#idealTranslation Flow
	idealTranslationFlow = opticalmodule.xyz(wall, K, Rt_translate,width,height).flatten()
	idealTranslationFlow = opticalmodule.reshapearray(idealTranslationFlow,width,height)
	meanITFlow = opticalmodule.meanFlow(idealTranslationFlow,width,height).flatten()
	meanmeanITFlow = opticalmodule.meanmeanFlow(meanITFlow)
	OBITFlow = np.abs(meanmeanITFlow)
	norITFlow = [ normT / 10 for normT in OBITFlow ]
	
	#FrameDifference
	Framedifference = algo.calculateFrameDifference(prvs, curr).flatten()
	meanFD = opticalmodule.meanFrameDifference(Framedifference,width,height).flatten()
	meanmeanFD = opticalmodule.meanmeanFlow(meanFD)
	FDcurrent = [ FDthreshold - FDcur for FDcur in meanmeanFD ]
	NFDcurrent = np.array(FDcurrent)
	NFDcurrent = [ FDcur / 10 for FDcur in NFDcurrent ]
	NFDcurrent = np.maximum(NFDcurrent, 0)

	time_flow += timer() - start_flow
	# generate neuron input currents
	neuronCurrents = np.concatenate((norOptFlow, norIRFlow, NFDcurrent, norITFlow), axis=None)
	IntneuronCurrents = [ round(float(INC),3) for INC in neuronCurrents ] 
			
	# Neuron simulation
	snn.stimulateInOrder(IntneuronCurrents)
	
	for index in range(50):
		snn.run(1)
		#potentials = potentials + snn.getAllPotential()

	activity = snn.getFirstNActivityInOrder(32)
	guiObstacle.display(raw, activity, realtimeFPS)
	#spikes = activity[-10 * snn.getNumNeurons():]
	#guiSpike.display(spikes, snn.getNumNeurons())
	#potentials = potentials[-500 * snn.getNumNeurons():]
	#guiPotential.display(potentials, snn.getNumNeurons())
	prvs = curr
	ptime, ptx, pty, ptz, prx, pry = time, tx, ty, tz, rx, ry
	
	fps.update()
	localfps.update()
	counter += 1
	if localfps.isPassed(30):
		localfps.stop()
		realtimeFPS = localfps.fps()
		localfps.reset()
		localfps.start()
	activity = 0

	key = cv2.waitKey(1)


fps.stop()
print("Elasped time: {:.3f} s".format(fps.elapsed()))
print("Approx. average FPS: {:.3f}".format(fps.fps()))
endd = timer()
cv2.destroyAllWindows()
saver.release()
vs.stop()
