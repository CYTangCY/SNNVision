import cv2

class VideoPreprocessor:

    def __init__(self, videoHeight, videoWidth):
        self.frameHW = (videoHeight, videoWidth)
        self.targetFrameSize = (160, 120)

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

