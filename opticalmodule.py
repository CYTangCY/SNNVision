import numpy as np
import cv2
from numpy import linalg as LA
from numba import jit
import numpy as nb
from timeit import default_timer as timer

# template wall translation flow
@jit(nopython = True)
def xyz(wall, K, Rt_translate,width,height):
	hg = 10//2
	arrayidealVectorT = np.zeros((width,height,2))
	for point in wall:	 
		x, y = int(point[0]), int(point[1])
		[ut, vt, wt] = K @ Rt_translate @ np.array([point[4], point[5], point[6],1])
		ut = ut/wt
		vt = vt/wt
		wt = 1.0
		ut = ut-x
		vt = vt-y		
		for i in range(y-hg, y+hg):
			for j in range(x-hg, x+hg):
				arrayidealVectorT[i,j,0] = ut
				arrayidealVectorT[i,j,1] = vt
				
	return arrayidealVectorT

# template wall ideal rotation flow	
@jit(nopython = True)
def RYP(wall, K, Rt_rotate,width,height):
	hg = 10//2
	arrayidealVectorRT = np.zeros((width,height,2))
	for point in wall:	
		x, y = int(point[0]), int(point[1]) 
		[ur, vr, wr] = K @ Rt_rotate @ np.array([point[4], point[5], point[6],1])
		ur = ur/wr
		vr = vr/wr
		wr = 1.0
		ur = ur-x
		vr = vr-y
		for i in range(y-hg, y+hg):
			for j in range(x-hg, x+hg):
				arrayidealVectorRT[i,j,0] = ur
				arrayidealVectorRT[i,j,1] = vr
				
	return arrayidealVectorRT
	

def reshapearray(flow,width,height):
	flow = flow.reshape((width,height, 2))
	
	return flow


def meanFlowFirst(flow,width,height):
	flowX = flow[:, :, 0]
	flowY = flow[:, :, 1]
	sh = (8, int(height/8), 8, int(width/8))
	meanFlowX = flowX.reshape(sh).mean(-1).mean(1)
	meanFlowY = flowY.reshape(sh).mean(-1).mean(1)
	meanFlow = np.dstack((meanFlowX, meanFlowY))
	
	return meanFlow

@jit(nopython = True)	
def meanFlowSecond(meanFlow):
	meanFlowyes = np.zeros((8,8))
	for i in range(8):
		for j in range(8):
			meanFlowyes[i,j] = np.sqrt(meanFlow[i,j,0]**2+meanFlow[i,j,1]**2)
			
	return meanFlowyes

	 
def meanFrameDifference(diff,width,height):
	diff = diff.reshape((width,height))
	sh = (8, int(height/8), 8, int(width/8))
	meanDiff = diff.reshape(sh).mean(-1).mean(1)
	
	return meanDiff

def meanmeanFlow_old(meanflow):
	OBmeanflow = []
	meanmeanflowup = ((meanflow[0]+meanflow[1]+meanflow[2]+meanflow[3]+meanflow[4]+meanflow[5]+meanflow[6]+meanflow[7]+meanflow[9]+meanflow[10]+meanflow[11]+meanflow[12]+meanflow[13]+meanflow[14]) / 14)
	OBmeanflow.append(meanmeanflowup )
	meanmeanflowleft = ((meanflow[8]+meanflow[9]+meanflow[16]+meanflow[17]+meanflow[24]+meanflow[25]+meanflow[32]+meanflow[33]+meanflow[40]+meanflow[41]+meanflow[48]+meanflow[49]) / 12)
	OBmeanflow.append(meanmeanflowleft )
	meanmeanflowdown = ((meanflow[49]+meanflow[50]+meanflow[51]+meanflow[52]+meanflow[53]+meanflow[54]+meanflow[56]+meanflow[57]+meanflow[58]+meanflow[59]+meanflow[60]+meanflow[61]+meanflow[62]+meanflow[63]) / 14)
	OBmeanflow.append(meanmeanflowdown )
	meanmeanflowright = ((meanflow[14]+meanflow[15]+meanflow[22]+meanflow[23]+meanflow[30]+meanflow[31]+meanflow[38]+meanflow[39]+meanflow[46]+meanflow[47]+meanflow[54]+meanflow[55]) / 12)
	OBmeanflow.append(meanmeanflowright )
	meanmeanflowmid = ((meanflow[18]+meanflow[19]+meanflow[20]+meanflow[21]+meanflow[26]+meanflow[27]+meanflow[28]+meanflow[29]+meanflow[34]+meanflow[35]+meanflow[36]+meanflow[37]+meanflow[42]+meanflow[43]+meanflow[44]+meanflow[45]) / 16)	
	OBmeanflow.append(meanmeanflowmid )
	   
	return OBmeanflow
	
def meanmeanFlow(meanflow):
	OBmeanflow = []
	meanmeanflow1 = ((meanflow[16]+meanflow[24]+meanflow[32]+meanflow[40]) / 4)
	OBmeanflow.append(meanmeanflow1 )
	meanmeanflow2 = ((meanflow[17]+meanflow[25]+meanflow[33]+meanflow[41]) / 4)
	OBmeanflow.append(meanmeanflow2 )
	meanmeanflow3 = ((meanflow[18]+meanflow[26]+meanflow[34]+meanflow[42]) / 4)
	OBmeanflow.append(meanmeanflow3 )
	meanmeanflow4 = ((meanflow[19]+meanflow[27]+meanflow[35]+meanflow[43]) / 4)
	OBmeanflow.append(meanmeanflow4 )
	meanmeanflow5 = ((meanflow[20]+meanflow[28]+meanflow[36]+meanflow[44]) / 4)
	OBmeanflow.append(meanmeanflow5 )
	meanmeanflow6 = ((meanflow[21]+meanflow[29]+meanflow[37]+meanflow[45]) / 4)
	OBmeanflow.append(meanmeanflow6)
	meanmeanflow7 = ((meanflow[22]+meanflow[30]+meanflow[38]+meanflow[46]) / 4)
	OBmeanflow.append(meanmeanflow7 )
	meanmeanflow8 = ((meanflow[23]+meanflow[31]+meanflow[39]+meanflow[47]) / 4)
	OBmeanflow.append(meanmeanflow8 )

	return OBmeanflow
	
@jit
def translationinmeters(tx,ptx,ty,pty,tz,ptz,rx,ry):
	xd, yd, zd = tx-ptx, ty-pty, tz-ptz
	zd = -zd
	translation = [np.sqrt(xd**2+yd**2+zd**2)*np.sin(np.arctan2(np.sqrt(xd**2+zd**2),yd)-rx)*np.cos(np.pi/2+np.arctan2(-xd,zd)+ry),
			np.sqrt(xd**2+yd**2+zd**2)*np.cos(np.arctan2(np.sqrt(xd**2+zd**2),yd)-rx),
			np.sqrt(xd**2+yd**2+zd**2)*np.sin(np.arctan2(np.sqrt(xd**2+zd**2),yd)-rx)*np.sin(np.pi/2+np.arctan2(-xd,zd)+ry)]
			
	return translation

	
def rotationinradius(rx,prx,ry,pry):
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
	
	return Rh, Ry ,Rx, RI

@jit	
def NormalizeFlow(flow):
	norFlow = [ normR / 5 for normR in flow ]
	
	return norFlow
	
	
	
	
	
	
	
	
