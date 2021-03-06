from threading import Thread

import cv2
import platform

import ImageProcessing

class VideoStreamMono:

    def __init__(self, src=0, usePiCamera=False, resolution=(640, 480), framerate=50):
        if usePiCamera:
            from PiOnly import PiVideoStreamMono
            self.stream = PiVideoStreamMono(resolution=resolution, framerate=framerate)
        elif src != 0:
            self.stream = FileVideoStreamCroppedMono(src = src)
        else:
            if platform.system() == "Linux":
                src = 0 + cv2.CAP_V4L2
            self.stream = WebcamVideoStreamCroppedMono(src = src)

    def start(self):
        return self.stream.start()

    def update(self):
        self.stream.update()

    def read(self):
        return self.stream.read()

    def stop(self):
        self.stream.stop()


class WebcamVideoStreamCroppedMono:

    def __init__(self, src = 0):
        self.stream = cv2.VideoCapture(src)
        #(self.grabbed, self.rawframe) = self.stream.read()
        self.grabbed = False
        self.frame = None
        self.monoFrame = None
        self.stopped = False
        fwidth = int( self.stream.get(cv2.CAP_PROP_FRAME_WIDTH) )
        fheight = int( self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT) )
        self.preprocessor = ImageProcessing.VideoPreprocessor(fheight, fwidth)

    def start(self):
        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            (self.grabbed, self.rawframe) = self.stream.read()
            if not self.grabbed:
                self.stop()
                return

            self.rawframe = self.preprocessor.FrameInput(self.rawframe)
            self.frame = cv2.resize(self.rawframe, (160, 120), cv2.INTER_AREA)
            self.monoFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def read(self):
        return self.grabbed, self.rawframe, self.frame, self.monoFrame

    def stop(self):
        self.stopped = True


class FileVideoStreamCroppedMono:

    def __init__(self, src = 0):
        self.stream = cv2.VideoCapture(src)
        #(self.grabbed, self.rawframe) = self.stream.read()
        self.grabbed = False
        self.rawframe = None
        self.frame = None
        self.monoFrame = None
        self.stopped = False
        fwidth = int( self.stream.get(cv2.CAP_PROP_FRAME_WIDTH) )
        fheight = int( self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT) )
        self.fwidth = int(fwidth)
        self.fheight = int(fheight)
        self.preprocessor = ImageProcessing.VideoPreprocessor(fheight, fwidth)
        
    def getwidth(self):
        return self.fwidth
        
    def getheight(self):
        return self.fheight

    def start(self):
        return self

    def read(self):
        (self.grabbed, self.rawframe) = self.stream.read()
        if not self.grabbed:
            return False, None, None, None
        self.rawframe = self.preprocessor.FrameInput(self.rawframe)
        self.frame = cv2.resize(self.rawframe, (640, 480), cv2.INTER_AREA)
        self.monoFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        return True, self.rawframe, self.frame, self.monoFrame

    def stop(self):
        self.stopped = True


