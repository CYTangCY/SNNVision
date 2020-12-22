import numpy as np
import cv2
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Potential():

	def __init__(self, numNeurons):
		potentialY = np.full(525, 255 )
		self.win = pg.GraphicsWindow()
		self.win.setWindowTitle('Potentials')
		self.curvePotentials = [0] * numNeurons
		for index in range(numNeurons):
			if index % 8 == 0:
				self.win.nextRow()
			self.plotPotentials = self.win.addPlot()
			self.plotPotentials.setYRange(-5, 50, padding=0)
			self.curvePotentials[index] = self.plotPotentials.plot(potentialY)

	def display(self, potentials, numNeurons):
		npPotentials = np.zeros(500 * numNeurons)
		npPotentials[-len(potentials):] = np.array(potentials)
		npPotentials = npPotentials.reshape(500, numNeurons)
		for index in range(numNeurons):
			self.curvePotentials[index].setData(npPotentials[:, index])

class Obstacle_old():

	def __init__(self, threshold1, threshold2, saver=None):
		self.saver = saver
		self.trapezoids = []
		outUp = np.array([[2, 0], [638, 2], [398, 118], [242, 118]], np.int)
		outUp = outUp.reshape((-1, 1, 2))
		self.trapezoids.append(outUp)
		outLeft = np.array([[0, 0], [0, 478], [238, 360], [238, 120]], np.int)
		outLeft = outLeft.reshape((-1, 1, 2))
		self.trapezoids.append(outLeft)
		outDown = np.array([[0, 480], [638, 480], [400, 362], [240, 362]], np.int)
		outDown = outDown.reshape((-1, 1, 2))
		self.trapezoids.append(outDown)
		outRight = np.array([[640, 0], [640, 478], [400, 358], [400, 122]], np.int)
		outRight = outRight.reshape((-1, 1, 2))
		self.trapezoids.append(outRight)
		outMid = np.array([[242, 122], [398, 122], [398, 358], [242, 358]], np.int)
		outMid = outMid.reshape((-1, 1, 2))


		
		self.threshold1 = threshold1
		self.threshold2 = threshold2

	def display(self, frame, activity, fps):
		showFrame = frame.copy()
		showFrame = cv2.resize(showFrame, (640, 480))
		
		cv2.line(showFrame, (0, 0), (240, 120), (0, 0, 0), 2)
		cv2.line(showFrame, (640, 0), (400, 120), (0, 0, 0), 2)
		cv2.line(showFrame, (0, 480), (240, 360), (0, 0, 0), 2)
		cv2.line(showFrame, (400, 360), (640, 480), (0, 0, 0), 2)
		cv2.rectangle(showFrame, (240, 120), (400, 360), (0, 0, 0), 2)
			   
		for loc, val in enumerate(self.trapezoids):
			if activity[loc ] > self.threshold1:
				cv2.polylines(showFrame, [val], True, (0, 215, 255), 3)
			if activity[loc ] > self.threshold2:
				cv2.polylines(showFrame, [val], True, (131, 121, 244), 3)

		if self.saver is not None:
			self.saver.write(showFrame)
		else:
			cv2.putText(showFrame, "FPS={:.1f}".format(fps), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (5, 255, 5))
		cv2.imshow("Obstacles", showFrame)
	  
class Spike_old():

	def __init__(self, numNeurons):
		self.win = pg.GraphicsWindow(title = None, size = (800, 200))
		self.win.setWindowTitle("Spike")
		self.countspikes = [index0 for index0 in range(numNeurons)]
		for index1 in range(numNeurons):
			if index1 % 5 == 0:
				self.win.nextRow()
			self.labelspikes = self.win.addLabel()
			self.labelspikes.setAttr(str(index1), 0)

	def display(self, spikes, numNeurons):
		displayspike = [ nN for nN in range(numNeurons)]
		for index2 in range(numNeurons):
			displayspike[index2] = str(spikes)
		for index3 in range(numNeurons):
			self.labelspikes.setText(str(displayspike[index3]), size = '16pt')

class Spike():

	def __init__(self, numNeurons):
		spikeY = np.full(0, 0 )
		self.win = pg.GraphicsWindow()
		self.win.setWindowTitle('spikes')
		self.curveSpikes = [0] * numNeurons
		for index in range(numNeurons):
			if index % 8 == 0:
				self.win.nextRow()
			self.plotSpikes = self.win.addPlot()
			self.plotSpikes.setYRange(-5, 30, padding=0)
			self.curveSpikes[index] = self.plotSpikes.plot(spikeY,  pen=pg.mkPen('g', width=10))

	def display(self, spikes, numNeurons):
		npSpikes = np.zeros(10 * numNeurons)
		npSpikes[-len(spikes):] = np.array(spikes)
		npSpikes = npSpikes.reshape(10, numNeurons)
		for index in range(numNeurons):
			self.curveSpikes[index].setData(npSpikes[:, index])
		
class Obstacle():

	def __init__(self, threshold1, threshold2, saver=None):
		self.saver = saver
		self.boxes = []
		box1 = np.array([[0, 120], [78, 120], [78, 360], [0, 360]], np.int)
		box1 = box1.reshape((-1, 1, 2))
		self.boxes.append(box1)
		box2 = np.array([[80, 120], [158, 120], [158, 360], [80, 360]], np.int)
		box2 = box2.reshape((-1, 1, 2))
		self.boxes.append(box2)
		box3 = np.array([[160, 120], [238, 120], [238, 360], [160, 360]], np.int)
		box3 = box3.reshape((-1, 1, 2))
		self.boxes.append(box3)
		box4 = np.array([[240, 120], [318, 120], [318, 360], [240, 360]], np.int)
		box4 = box4.reshape((-1, 1, 2))
		self.boxes.append(box4)
		box5 = np.array([[320, 120], [398, 120], [398, 360], [320, 360]], np.int)
		box5 = box5.reshape((-1, 1, 2))
		self.boxes.append(box5)
		box6 = np.array([[400, 120], [478, 120], [478, 360], [400, 360]], np.int)
		box6 = box6.reshape((-1, 1, 2))
		self.boxes.append(box6)
		box7 = np.array([[480, 120], [558, 120], [558, 360], [480, 360]], np.int)
		box7 = box7.reshape((-1, 1, 2))
		self.boxes.append(box7)
		box8 = np.array([[560, 120], [638, 120], [638, 360], [560, 360]], np.int)
		box8 = box8.reshape((-1, 1, 2))
		self.boxes.append(box8)



		
		self.threshold1 = threshold1
		self.threshold2 = threshold2

	def display(self, frame, activity, fps):
		showFrame = frame.copy()
		showFrame = cv2.resize(showFrame, (640, 480))
		
		cv2.line(showFrame, (0, 120), (640, 120), (0, 0, 0), 2)
		cv2.line(showFrame, (0, 360), (640, 360), (0, 0, 0), 2)
		cv2.line(showFrame, (80, 120), (80, 360), (0, 0, 0), 2)
		cv2.line(showFrame, (160, 120), (160, 360), (0, 0, 0), 2)
		cv2.line(showFrame, (240, 120), (240, 360), (0, 0, 0), 2)
		cv2.line(showFrame, (320, 120), (320, 360), (0, 0, 0), 2)
		cv2.line(showFrame, (400, 120), (400, 360), (0, 0, 0), 2)
		cv2.line(showFrame, (480, 120), (480, 360), (0, 0, 0), 2)
		cv2.line(showFrame, (560, 120), (560, 360), (0, 0, 0), 2)
			   
		for loc, val in enumerate(self.boxes):
			if activity[loc ] > self.threshold1:
				cv2.polylines(showFrame, [val], True, (0, 215, 255), 2)
			if activity[loc ] > self.threshold2:
				cv2.polylines(showFrame, [val], True, (131, 121, 244), 2)

		if self.saver is not None:
			self.saver.write(showFrame)
		else:
			cv2.putText(showFrame, "FPS={:.1f}".format(fps), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (5, 255, 5))
		cv2.imshow("Obstacles", showFrame)


