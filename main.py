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

frameHW = (640, 480)
frameRate = 30
fourcc = cv2.VideoWriter_fourcc(*"MJPG")

#saver setting
#saver = cv2.VideoWriter('output2' + '.avi', fourcc, 30, (640, 480))
saver = None

#resolution setting
width = int(640)
height = int(480)

#SNN model setting
snn = SNN("lif", 1)

#display activity
spikes = [0]
guiSpike = Graphics.Spike(snn.getNumNeurons())

#display potential
#potentials = [0]
#guiPotential = Graphics.Potential(snn.getNumNeurons())

#display obstacle
guiObstacle = Graphics.Obstacle(threshold1 = 9, threshold2 = 11, saver=saver)

   
time.sleep(2.0)
vs = VideoStreamMono("paraleft.mkv", usePiCamera=False, resolution=frameHW, framerate=frameRate).start()

#setting IMU data
pose = open('paraleft.txt', 'r')

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
FDthreshold = 7


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
	Rh, Ry, Rx, RI = opticalmodule.rotationinradius(rx,prx,ry,pry)
	
	# translation in meters
	translation = opticalmodule.translationinmeters(tx,ptx,ty,pty,tz,ptz,rx,ry)
	translation = np.array(translation).reshape(3, 1)
	translation_O = [0, 0, 0]
	translation_O = np.array(translation_O).reshape(3, 1)

	# Rt = [R|t]
	Rt_rotate = np.concatenate((Rh @ Ry @ Rx, translation_O), axis=1)
	Rt_translate = np.concatenate((RI, translation), axis=1)
	
	start_flow = timer()
				  
	#calculate optical flow 
	OptFlow = algo.calculateOpticalFlow(prvs, curr).flatten()
	OptFlow = np.array(OptFlow)
	OptFlow = opticalmodule.reshapearray(OptFlow,width,height)
	meanOptFlow = opticalmodule.meanFlowFirst(OptFlow,width,height)
	meanOptFlow = opticalmodule.meanFlowSecond(meanOptFlow).flatten()
	meanmeanOptFlow = opticalmodule.meanmeanFlow(meanOptFlow)
	OBOptFlow = np.abs(meanmeanOptFlow)
	norOptFlow = opticalmodule.NormalizeFlow(OBOptFlow)

	
	#calculate idealRotation Flow
	idealRotateFlow = opticalmodule.RYP(wall, K, Rt_rotate,width,height).flatten()
	idealRotateFlow = np.array(idealRotateFlow)
	idealRotateFlow = opticalmodule.reshapearray(idealRotateFlow,width,height)
	meanIRFlow = opticalmodule.meanFlowFirst(idealRotateFlow,width,height)
	meanIRFlow = opticalmodule.meanFlowSecond(meanIRFlow).flatten()
	meanmeanIRFlow = opticalmodule.meanmeanFlow(meanIRFlow)
	OBIRFlow = np.abs(meanmeanIRFlow)
	norIRFlow = opticalmodule.NormalizeFlow(OBIRFlow)
	
	#calculate idealTranslation Flow
	idealTranslationFlow = opticalmodule.xyz(wall, K, Rt_translate,width,height).flatten()
	idealTranslationFlow = np.array(idealTranslationFlow)
	idealTranslationFlow = opticalmodule.reshapearray(idealTranslationFlow,width,height)
	meanITFlow = opticalmodule.meanFlowFirst(idealTranslationFlow,width,height)
	meanITFlow =  opticalmodule.meanFlowSecond(meanITFlow).flatten()
	meanmeanITFlow = opticalmodule.meanmeanFlow(meanITFlow)
	OBITFlow = np.abs(meanmeanITFlow)
	norITFlow = opticalmodule.NormalizeFlow(OBITFlow)
	
	#calculate FrameDifference
	Framedifference = algo.calculateFrameDifference(prvs, curr).flatten()
	Framedifference = np.array(Framedifference)
	meanFD = opticalmodule.meanFrameDifference(Framedifference,width,height).flatten()
	meanmeanFD = opticalmodule.meanmeanFlow(meanFD)
	FDcurrent = [ FDthreshold - FDcur for FDcur in meanmeanFD ]
	NFDcurrent = np.array(FDcurrent)
	NFDcurrent = opticalmodule.NormalizeFlow(NFDcurrent)
	NFDcurrent = np.maximum(NFDcurrent, 0)

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
	spikes = activity[-10 * snn.getNumNeurons():]
	guiSpike.display(spikes, snn.getNumNeurons())
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
