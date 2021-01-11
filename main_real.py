import time
import argparse

import cv2
import numpy as np

from snn import SNN
from timer import FPS
from Stream import VideoStreamMono
from ImageProcessing import Algorithm
from ImageProcessing import VirtualWall
import Graphics
import opticalmodule
from timeit import default_timer as timer

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--num-threads", type=int, default=1, help="# of threads to accelerate")
ap.add_argument("-dp", "--display-potential", help="Whether or not neural potentials should be displayed", action="store_true")
ap.add_argument("-do", "--display-obstacle", help="Whether or not obstacles should be displayed", action="store_true")
ap.add_argument("-da", "--display-activity", help="Whether or not activity should be displayed", action="store_true")
ap.add_argument("-i", "--input", type=str, help="Input video file instead of live stream.")
ap.add_argument("-p", "--pose", type=str, help="Input IMU data.")
ap.add_argument("-o", "--output", type=str, help="Output processed video file for obstacle detection.")
ap.add_argument("-m", "--models", type=str, help="Use Izhikevich = iz, Use Lif=lif")
args = vars(ap.parse_args())

#resolution setting
width = int(input("please enter the frame width: "))
height = int(input("please enter the frame height: "))

VW = VirtualWall()
algo = Algorithm()
frameHW = (160, 120)
frameRate = 50

#input setting
if args["input"]:
	vs = VideoStreamMono(src=args["input"], usePiCamera=False, resolution=frameHW, framerate=frameRate, width=width, height=height).start()
else:
	print("please enter the input video name, use -i <filename>")
	
#IMU data setting
if args["pose"]:
	pose = open(args["pose"],'r')
else:
	print("please enter the IMU data file name, use -p <filename>")	
	
#saver setting
if args["output"]:
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    saver = cv2.VideoWriter(args["output"] + '.avi', fourcc, 50, (640, 480))
else:
    saver = None

#SNN model setting
snn = SNN(args["models"], args["num_threads"])

#display activity
if args["display_activity"]:
	spikes = [0]
	guiSpike = Graphics.Spike(snn.getNumNeurons())

#display potential
if args["display_potential"]:
	potentials = [0]
	guiPotential = Graphics.Potential(snn.getNumNeurons())

#display obstacle
if args["display_obstacle"]:
	guiObstacle = Graphics.Obstacle(threshold1 = 5, threshold2 = 9, saver=saver)

#Virtual wall 
wall = VW.makewall(width,height,3)
   
time.sleep(2.0)


[ret, raw, _, prvs] = vs.read(width, height)

focalLength = min(height, width)/2/np.tan(35/180*np.pi)
K = np.array([[focalLength, 0.0, width/2],
			 [0.0, focalLength, height/2],
			 [0.0, 0.0, 1.0]])

ptime, ptx, pty, ptz, prx, pry = 89.0093667411804, 0.11249490827322, 0.234294831752777, 1.13050961494446, 0.081444218754768, 0.069610111415386

start = timer()
frame_count = 0
time_flow = 0
time_rt = 0
time_depth = 0
FDthreshold = 15
timestep = 0.0454545
v0x, v0y, v0z = 0, 0, 0
txfix, tyfix, tzfix = -0.063, -0.95, -0.222

fps = FPS().start()
localfps = FPS().start()
realtimeFPS = 0
counter = 0

[ret, raw, _, curr] = vs.read(width, height)
key = cv2.waitKey(1)
for line in pose:
	[ret, raw, _, curr] = vs.read(width, height)
	
	time, useless0, useless1, useless2, rx_, rz_, ry_, tx_, tz_, ty_ = line.split()
	time = float(time)
	tx, ty, tz, rx, ry = float(tx_), float(ty_), float(tz_), float(rx_), float(ry_)
	tx, ty, tz, rx, ry, v0x, v0y, v0z = algo.ConvertToDisplacement(tx, ty, tz, rx, ry, time , ptime, v0x, v0y, v0z, timestep, txfix, tyfix, tzfix)

	   
	# rotation in radius
	Rh, Ry, Rx, RI = opticalmodule.rotationinradius(rx,prx,ry,pry)
	
	# translation in meters
	translation = opticalmodule.translationinmeters_real(tx,ty,tz,rx,ry)
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
	IntneuronCurrents = [ round(float(INC),5) for INC in neuronCurrents ] 
	#print(IntneuronCurrents)	
	# Neuron simulation
	snn.stimulateInOrder(IntneuronCurrents)
	
	for index in range(50):
		snn.run(1)
		if args["display_potential"]:
			potentials = potentials + snn.getAllPotential()

	activity = snn.getFirstNActivityInOrder(32)
	
	if args["display_obstacle"]:
		guiObstacle.display(raw, activity, realtimeFPS)
		
	if args["display_activity"]:	
		spikes = activity[-10 * snn.getNumNeurons():]
		guiSpike.display(spikes, snn.getNumNeurons())
	
	if args["display_potential"]:
		potentials = potentials[-500 * snn.getNumNeurons():]
		guiPotential.display(potentials, snn.getNumNeurons())
		
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
