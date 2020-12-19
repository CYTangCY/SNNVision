import numpy as np
import cv2
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

class Demo():


    def __init__(self):
        upArrow = np.array([ ( (87, 300), (87, 50) ), ( (174, 300), (174, 50) ), ( (261, 300), (261, 50) ) ])
        downArrow = np.array([ ( (87, 400), (87, 650) ), ( (174, 400), (174, 650) ), ( (261, 400), (261, 650) ) ])
        rightArrow = np.array([ ( (1000, 437), (750, 437) ), ( (1000, 524), (750, 524) ), ( (1000, 611), (750, 611) ) ])
        leftArrow = np.array([ ( (750, 87), (1000, 87) ), ( (750, 174), (1000, 174) ), ( (750, 261), (1000, 261) ) ])
        zoominArrow = np.array([ ( (500, 150), (400, 50) ), ( (500, 200), (400, 300) ), ( (550, 150), (650, 50) ), ( (550, 200), (650, 300) ), ( (500, 175), (375, 175) ), ( (550, 175), (675, 175) ), ( (525, 150), (525, 25) ), ( (525, 200), (525, 325) ) ])
        zoomoutArrow = np.array([ ( (400, 400), (475, 475) ), ( (400, 650), (475, 575) ), ( (650, 400), (575, 475) ), ( (650, 650), (575, 575) ), ( (375, 525), (475, 525) ), ( (675, 525), (575, 525) ), ( (525, 375), (525, 475) ), ( (525, 675), (525, 575) ) ])
        cwArrow = np.array( [ (0, 0), (0, 0) ] )
        ccwArrow = np.array( [ (0, 0), (0, 0) ] )
        frontSide = np.array([ ( (0, 0), (249, 50) ) ])
        rearSide = np.array([ ( (249, 249), (0, 200) ) ])
        leftSide = np.array([ ( (0, 50), (50, 200) ) ])
        rightSide = np.array([ ( (200, 50), (249, 200) ) ])
        #label =  "CW  FWD DWN RT CCW  BWD  UP  LFT oUP oLFT oRT oDWN mUP mLFT mRT mDWN iUP iLFT iRT iDWN C"
        #self.arrows = [ccwArrow, cwArrow, zoominArrow, zoomoutArrow, upArrow, downArrow, rightArrow, leftArrow, frontSide, rearSide, leftSide, rightSide]
        self.arrows = [cwArrow, zoominArrow, downArrow, rightArrow, ccwArrow, zoomoutArrow, upArrow, leftArrow, frontSide, rearSide, leftSide, rightSide]
        self.inactiveColor = (80, 80, 80)
        self.activeColor = (255, 255, 255)
        self.obstacleColor = (20, 200, 250)
        self.canvas = cv2.imread("assets/MotionBackground.jpg")
        self.blank = cv2.imread("assets/ObstacleBackground.jpg")

    def mountWindowAt(self, x, y):
        cv2.imshow("Motion", self.canvas)
        cv2.moveWindow("Motion", x, y)

    def drawArrows(self, image, positions, color):
        for index in range(positions.shape[0]):
            cv2.arrowedLine(image, tuple(positions[index][0]), tuple(positions[index][1]), color, thickness=20)
        return image

    def drawObstacles(self, image, locations, color):
        for index in range(locations.shape[0]):
            cv2.rectangle(image, tuple(locations[index][0]), tuple(locations[index][1]), color, thickness=cv2.FILLED)
        return image

    # front, rear, left, right
    def displayConfig(self, thresholds, config):
        motion = self.canvas.copy()

        for index, value  in enumerate(config):
            if index == 0:
                if value > thresholds[0]:
                    cv2.circle(canvas, (1225, 175), 125, inactiveColor, thickness=20)
                    cv2.drawMarker(canvas, (1100, 175), inactiveColor, markerType=cv2.MARKER_TRIANGLE_UP, markerSize=45, thickness=20)
                    cv2.drawMarker(canvas, (1350, 175), inactiveColor, markerType=cv2.MARKER_TRIANGLE_DOWN, markerSize=45, thickness=20)
            elif index == 4:
                if value > thresholds[0]:
                    cv2.circle(canvas, (1225, 525), 125, inactiveColor, thickness=20)
                    cv2.drawMarker(canvas, (1100, 525), inactiveColor, markerType=cv2.MARKER_TRIANGLE_DOWN, markerSize=45, thickness=20)
                    cv2.drawMarker(canvas, (1350, 525), inactiveColor, markerType=cv2.MARKER_TRIANGLE_UP, markerSize=45, thickness=20)
            elif index < 8:
                if value > thresholds[0]:
                    motion = self.drawArrows(motion, self.arrows[index], self.activeColor)

        cv2.imshow("Motion", motion)


class Flow():

    def __init__(self):
        None

    def display(self, frame, flow, fps):
        showFrame = frame.copy()
        showFrame = cv2.resize(showFrame, (512, 512))
        flow = flow.reshape(8, 8, 2)
        flow = cv2.resize(flow, (512, 512), cv2.INTER_NEAREST)
        for y in range(32, 512, 64):
            for x in range(32, 512, 64):
                cv2.line(showFrame, (x, y), (x+int(5*flow[y][x][0]), y+int(5*flow[y][x][1])), (255, 255, 255), 3)
        cv2.putText(showFrame, "FPS={:.1f}".format(fps), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (5, 255, 5))
        cv2.imshow("Flow", showFrame)

class Dot():

    def __init__(self):
        None

    def display(self, frame, label, flow, fps):
        showFrame = frame.copy()
        showFrame = cv2.resize(showFrame, (512, 512))
        interval = 40
        cv2.putText(showFrame, label[0:33], (15, 350), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
        cv2.putText(showFrame, "FPS={:.1f}".format(fps), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (5, 255, 5))
        for loc, val in enumerate(flow):
            cv2.line(showFrame, (25+loc*interval, 300), (25+loc*interval, 300-int(val*2)), color=(255, 55, 255), thickness=20)
        cv2.imshow("Dotted", showFrame)


class Neuron():

    def __init__(self):
        None

    def display(self, frame, label, fps, activity):
        showFrame = frame.copy()
        showFrame = cv2.resize(showFrame, (512, 512))
        interval = 40
        cv2.putText(showFrame, label[0:32], (15, 480), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
        cv2.putText(showFrame, "FPS={:.1f}".format(fps), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (5, 255, 5))
        for loc, val in enumerate(activity):
            cv2.line(showFrame, (25+(loc%8)*interval, 512-(62*(1+loc//8))), (25+(loc%8)*interval, 512-(62*(1+loc//8))-int(val)*20), color=(255, 255, 55), thickness=15)
        cv2.imshow("Neuron", showFrame)

class Potential():

    def __init__(self, numNeurons):
        potentialY = np.full(500, 255)
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle('Potentials')
        self.curvePotentials = [0] * numNeurons
        for index in range(numNeurons):
            if index % 4 == 0:
                self.win.nextRow()
            self.plotPotentials = self.win.addPlot()
            self.plotPotentials.setYRange(-10, 260, padding=0)
            self.curvePotentials[index] = self.plotPotentials.plot(potentialY)

    def display(self, potentials, numNeurons):
        npPotentials = np.zeros(500 * numNeurons)
        npPotentials[-len(potentials):] = np.array(potentials)
        npPotentials = npPotentials.reshape(500, numNeurons)
        for index in range(numNeurons):
            self.curvePotentials[index].setData(npPotentials[:, index])

class Obstacle():

    def __init__(self, threshold1, threshold2, saver=None):
        self.saver = saver
        self.boxes = []
        box1 = np.array([[0,0],[64,0],[64,64],[0,64]], np.int)
        box1 = box1.reshape((-1, 1, 2))
        self.boxes.append(box1)
        box2 = np.array([[64,0],[128,0],[128,64],[64,64]], np.int)
        box2 = box2.reshape((-1, 1, 2))
        self.boxes.append(box2)
        box3 = np.array([[128,0],[192,0],[192,64],[128,64]], np.int)
        box3 = box3.reshape((-1, 1, 2))
        self.boxes.append(box3)
        box4 = np.array([[192,0],[256,0],[256,64],[192,64]], np.int)
        box4 = box4.reshape((-1, 1, 2))
        self.boxes.append(box4)
        box5 = np.array([[256,0],[320,0],[320,64],[256,64]], np.int)
        box5 = box5.reshape((-1, 1, 2))
        self.boxes.append(box5)
        box6 = np.array([[320,0],[384,0],[384,64],[320,64]], np.int)
        box6 = box6.reshape((-1, 1, 2))
        self.boxes.append(box6)
        box7 = np.array([[384,0],[448,0],[448,64],[384,64]], np.int)
        box7 = box7.reshape((-1, 1, 2))
        self.boxes.append(box7)
        box8 = np.array([[448,0],[512,0],[512,64],[448,64]], np.int)
        box8 = box8.reshape((-1, 1, 2))
        self.boxes.append(box8)
        box9 = np.array([[0,64],[64,64],[64,128],[0,128]], np.int)
        box9 = box9.reshape((-1, 1, 2))
        self.boxes.append(box9)
        box10 = np.array([[64,64],[128,64],[128,128],[64,128]], np.int)
        box10 = box10.reshape((-1, 1, 2))
        self.boxes.append(box10)
        box11 = np.array([[128,64],[192,64],[192,128],[128,128]], np.int)
        box11 = box11.reshape((-1, 1, 2))
        self.boxes.append(box11)
        box12 = np.array([[192,64],[256,64],[256,128],[192,128]], np.int)
        box12 = box12.reshape((-1, 1, 2))
        self.boxes.append(box12)
        box13 = np.array([[256,64],[320,64],[320,128],[256,128]], np.int)
        box13 = box13.reshape((-1, 1, 2))
        self.boxes.append(box13)
        box14 = np.array([[320,64],[384,64],[384,128],[320,128]], np.int)
        box14 = box14.reshape((-1, 1, 2))
        self.boxes.append(box14)
        box15 = np.array([[384,64],[448,64],[448,128],[384,128]], np.int)
        box15 = box15.reshape((-1, 1, 2))
        self.boxes.append(box15)
        box16 = np.array([[448,64],[512,64],[512,128],[448,128]], np.int)
        box16 = box16.reshape((-1, 1, 2))
        self.boxes.append(box16)
        box17 = np.array([[0,128],[64,128],[64,192],[0,192]], np.int)
        box17 = box17.reshape((-1, 1, 2))
        self.boxes.append(box17)
        box18 = np.array([[64,128],[128,128],[128,192],[64,192]], np.int)
        box18 = box18.reshape((-1, 1, 2))
        self.boxes.append(box18)
        box19 = np.array([[128,128],[192,128],[192,192],[128,192]], np.int)
        box19 = box19.reshape((-1, 1, 2))
        self.boxes.append(box19)
        box20 = np.array([[192,128],[256,128],[256,192],[192,192]], np.int)
        box20 = box20.reshape((-1, 1, 2))
        self.boxes.append(box20)
        box21 = np.array([[256,128],[320,128],[320,192],[256,192]], np.int)
        box21 = box21.reshape((-1, 1, 2))
        self.boxes.append(box21)
        box22 = np.array([[320,128],[384,128],[384,192],[320,192]], np.int)
        box22 = box22.reshape((-1, 1, 2))
        self.boxes.append(box22)
        box23 = np.array([[384,128],[448,128],[448,192],[384,192]], np.int)
        box23 = box23.reshape((-1, 1, 2))
        self.boxes.append(box23)
        box24 = np.array([[448,128],[512,128],[512,192],[448,192]], np.int)
        box24 = box24.reshape((-1, 1, 2))
        self.boxes.append(box24)
        box25 = np.array([[0,192],[64,192],[64,256],[0,256]], np.int)
        box25 = box25.reshape((-1, 1, 2))
        self.boxes.append(box25)
        box26 = np.array([[64,192],[128,192],[128,256],[64,256]], np.int)
        box26 = box26.reshape((-1, 1, 2))
        self.boxes.append(box26)
        box27 = np.array([[128,192],[192,192],[192,256],[128,256]], np.int)
        box27 = box27.reshape((-1, 1, 2))
        self.boxes.append(box27)
        box28 = np.array([[192,192],[256,192],[256,256],[192,256]], np.int)
        box28 = box28.reshape((-1, 1, 2))
        self.boxes.append(box28)
        box29 = np.array([[256,192],[320,192],[320,256],[256,256]], np.int)
        box29 = box29.reshape((-1, 1, 2))
        self.boxes.append(box29)
        box30 = np.array([[320,192],[384,192],[384,256],[320,256]], np.int)
        box30 = box30.reshape((-1, 1, 2))
        self.boxes.append(box30)
        box31 = np.array([[384,192],[448,192],[448,256],[384,256]], np.int)
        box31 = box31.reshape((-1, 1, 2))
        self.boxes.append(box31)
        box32 = np.array([[448,192],[512,192],[512,256],[448,256]], np.int)
        box32 = box32.reshape((-1, 1, 2))
        self.boxes.append(box32)
        box33 = np.array([[0,256],[64,256],[64,320],[0,320]], np.int)
        box33 = box33.reshape((-1, 1, 2))
        self.boxes.append(box33)
        box34 = np.array([[64,256],[128,256],[128,320],[64,320]], np.int)
        box34 = box34.reshape((-1, 1, 2))
        self.boxes.append(box34)
        box35 = np.array([[128,256],[192,256],[192,320],[128,320]], np.int)
        box35 = box35.reshape((-1, 1, 2))
        self.boxes.append(box35)
        box36 = np.array([[192,256],[256,256],[256,320],[192,320]], np.int)
        box36 = box36.reshape((-1, 1, 2))
        self.boxes.append(box36)
        box37 = np.array([[256,256],[320,256],[320,320],[256,320]], np.int)
        box37 = box37.reshape((-1, 1, 2))
        self.boxes.append(box37)
        box38 = np.array([[320,256],[384,256],[384,320],[320,320]], np.int)
        box38 = box38.reshape((-1, 1, 2))
        self.boxes.append(box38)
        box39 = np.array([[384,256],[448,256],[448,320],[384,320]], np.int)
        box39 = box39.reshape((-1, 1, 2))
        self.boxes.append(box39)
        box40 = np.array([[448,256],[512,256],[512,320],[448,320]], np.int)
        box40 = box40.reshape((-1, 1, 2))
        self.boxes.append(box40)
        box41 = np.array([[0,320],[64,320],[64,384],[0,384]], np.int)
        box41 = box41.reshape((-1, 1, 2))
        self.boxes.append(box41)
        box42 = np.array([[64,320],[128,320],[128,384],[64,384]], np.int)
        box42 = box42.reshape((-1, 1, 2))
        self.boxes.append(box42)
        box43 = np.array([[128,320],[192,320],[192,384],[128,384]], np.int)
        box43 = box43.reshape((-1, 1, 2))
        self.boxes.append(box43)
        box44 = np.array([[192,320],[256,320],[256,384],[192,384]], np.int)
        box44 = box44.reshape((-1, 1, 2))
        self.boxes.append(box44)
        box45 = np.array([[256,320],[320,320],[320,384],[256,384]], np.int)
        box45 = box45.reshape((-1, 1, 2))
        self.boxes.append(box45)
        box46 = np.array([[320,320],[384,320],[384,384],[320,384]], np.int)
        box46 = box46.reshape((-1, 1, 2))
        self.boxes.append(box46)
        box47 = np.array([[384,320],[448,320],[448,384],[384,384]], np.int)
        box47 = box47.reshape((-1, 1, 2))
        self.boxes.append(box47)
        box48 = np.array([[448,320],[512,320],[512,384],[448,384]], np.int)
        box48 = box48.reshape((-1, 1, 2))
        self.boxes.append(box48)
        box49 = np.array([[0,384],[64,384],[64,448],[0,448]], np.int)
        box49 = box49.reshape((-1, 1, 2))
        self.boxes.append(box49)
        box50 = np.array([[64,384],[128,384],[128,448],[64,448]], np.int)
        box50 = box50.reshape((-1, 1, 2))
        self.boxes.append(box50)
        box51 = np.array([[128,384],[192,384],[192,448],[128,448]], np.int)
        box51 = box51.reshape((-1, 1, 2))
        self.boxes.append(box51)
        box52 = np.array([[192,384],[256,384],[256,448],[192,448]], np.int)
        box52 = box52.reshape((-1, 1, 2))
        self.boxes.append(box52)
        box53 = np.array([[256,384],[320,384],[320,448],[256,448]], np.int)
        box53 = box53.reshape((-1, 1, 2))
        self.boxes.append(box53)
        box54 = np.array([[320,384],[384,384],[384,448],[320,448]], np.int)
        box54 = box54.reshape((-1, 1, 2))
        self.boxes.append(box54)
        box55 = np.array([[384,384],[448,384],[448,448],[384,448]], np.int)
        box55 = box55.reshape((-1, 1, 2))
        self.boxes.append(box55)
        box56 = np.array([[448,384],[512,384],[512,448],[448,448]], np.int)
        box56 = box56.reshape((-1, 1, 2))
        self.boxes.append(box56)
        box57 = np.array([[0,448],[64,448],[64,512],[0,512]], np.int)
        box57 = box57.reshape((-1, 1, 2))
        self.boxes.append(box57)
        box58 = np.array([[64,448],[128,448],[128,512],[64,512]], np.int)
        box58 = box58.reshape((-1, 1, 2))
        self.boxes.append(box58)
        box59 = np.array([[128,448],[192,448],[192,512],[128,512]], np.int)
        box59 = box59.reshape((-1, 1, 2))
        self.boxes.append(box59)
        box60 = np.array([[192,448],[256,448],[256,512],[192,512]], np.int)
        box60 = box60.reshape((-1, 1, 2))
        self.boxes.append(box60)
        box61 = np.array([[256,448],[320,448],[320,512],[256,512]], np.int)
        box61 = box61.reshape((-1, 1, 2))
        self.boxes.append(box61)
        box62 = np.array([[320,448],[384,448],[384,512],[320,512]], np.int)
        box62 = box62.reshape((-1, 1, 2))
        self.boxes.append(box62)
        box63 = np.array([[384,448],[448,448],[448,512],[384,512]], np.int)
        box63 = box63.reshape((-1, 1, 2))
        self.boxes.append(box63)
        box64 = np.array([[448,448],[512,448],[512,512],[448,512]], np.int)
        box64 = box64.reshape((-1, 1, 2))
        self.boxes.append(box64)
        
        self.threshold1 = threshold1
        self.threshold2 = threshold2

    def display(self, frame, activity, fps):
        showFrame = frame.copy()
        showFrame = cv2.resize(showFrame, (512, 512))
        
        cv2.line(showFrame, (0, 0), (0, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (64, 0), (64, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (128, 0), (128, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (192, 0), (192, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (256, 0), (256, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (320, 0), (320, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (384, 0), (384, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (448, 0), (448, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (512, 0), (512, 512), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 0), (512, 0), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 64), (512, 64), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 128), (512, 128), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 192), (512, 192), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 256), (512, 256), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 320), (512, 320), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 384), (512, 384), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 448), (512, 448), (0, 0, 0), 2)
        cv2.line(showFrame, (0, 512), (512, 512), (0, 0, 0), 2)
               
        for loc, val in enumerate(self.boxes):
            if activity[loc + 192] > self.threshold1:
                cv2.polylines(showFrame, [val], True, (255, 215, 0), 12)
            if activity[loc + 192] > self.threshold2:
                cv2.polylines(showFrame, [val], True, (244, 121, 131), 12)

        if self.saver is not None:
            self.saver.write(showFrame)
        else:
            cv2.putText(showFrame, "FPS={:.1f}".format(fps), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (5, 255, 5))
        cv2.imshow("Obstacles", showFrame)

