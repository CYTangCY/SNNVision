import cv2
import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class VideoPreprocessor:

    def __init__(self, videoHeight, videoWidth, width, height):
        self.frameHW = (videoHeight, videoWidth)
        self.targetFrameSize = (width, height)

    def FrameInput(self, frame):
        return frame

    def convertFrameIntoSpecifiedFormat(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, self.targetFrameSize, cv2.INTER_AREA)
        return frame


class Algorithm:

    def calculateOpticalFlow(self, previousFrame, currentFrame):
        dis = cv2.DISOpticalFlow_create(0)
        flow = dis.calc(previousFrame, currentFrame, None, )
        #flow = cv2.calcOpticalFlowFarneback(previousFrame, currentFrame, None, 0.5, 8, 15, 3, 5, 1.2, 0)
        return flow
        
    def calculateFrameDifference(self, previousFrame, currentFrame):
        diff = cv2.absdiff(previousFrame, currentFrame)
        return diff

    def contrastEnhance(self, frame):
        kernel_size = (9,9)
        sigma = 7.0 
        # GaussianSTD1 = 5.0
        frame_c = frame.copy()
        blur = cv2.GaussianBlur(frame_c,kernel_size,sigma)
        unsharpFrame = cv2.addWeighted(frame_c, 5, blur, -4, 0, frame_c)
        return unsharpFrame
        
class VirtualWall:
	
	def makewall(self, width, height,WallDistance):
		width = width
		height = height
		WallDistance = WallDistance
		grid = width//16
		focalLength = min(height, width)/2/np.tan(35/180*np.pi)

		K = np.array([[focalLength, 0, width/2, 0],
					  [0, focalLength, height/2, 0],
					  [0, 0, 1, 0],
					  [0, 0, 0, 1]])
		K_inv = LA.inv(K)

		rotation = [0, 0, 0]
		rx = rotation[0]
		ry = rotation[1]
		rz = rotation[2]
		Rz = np.array([[np.cos(rz), -np.sin(rz), 0],
					  [ np.sin(rz),  np.cos(rz), 0],
				  	[		  0,		   0, 1]])
		Ry = np.array([[np.cos(ry), 0, np.sin(ry)],
					  [		  0, 1,		  0],
					  [-np.sin(ry), 0, np.cos(ry)]])
		Rx = np.array([[1,		  0,		   0],
					  [ 0, np.cos(rx), -np.sin(rx)],
					  [ 0, np.sin(rx),  np.cos(rx)]])

		translation = [0, 0, 0]
		translation = np.array(translation).reshape(3, 1)

		Rt = np.concatenate((Rz @ Ry @ Rx, translation), axis=1)
		Rt = np.concatenate((Rt, np.array([[0, 0, 0, 1]])), axis=0)

		Rt_inv = LA.inv(Rt)
	
		frameWallPair = np.zeros(height//grid*width//grid*4*2)
		frameWallPair = frameWallPair.reshape(height//grid*width//grid, 4*2)

		for u in range(grid//2, width, grid):
			for v in range(grid//2, height, grid):
				p_frame = np.array([u, v, 1, 1]).reshape(4, 1)
				p_wall = Rt_inv @ K_inv @ p_frame
				p_wall = p_wall / p_wall[2] * WallDistance
		
				frameWallPair[u//grid*(height//grid)+v//grid] = np.concatenate((p_frame, p_wall), axis=None)

		return frameWallPair


