from __future__ import print_function
from imp import load_source
from os.path import join, dirname
from sys import platform, argv
try: import Tkinter as tk
except: import tkinter as tk

APP_X, APP_Y = 100, 100
CANVAS_WIDTH, CANVAS_HEIGHT = 500, 500
IMAGE_PATH = join(dirname(argv[0]), 'piano-keys.gif')

class MainGUI(tk.Label):
    def __init__(self, master):
        self.image = tk.PhotoImage(file=IMAGE_PATH)
        tk.Label.__init__(self, master, image=self.image)
        #self.wlbt = Walabot(self)

class Walabot:
    def __init__(self, master):
        self.master = master
        if platform == 'win32': # for windows
            path = join('C:/', 'Program Files', 'Walabot', 'WalabotSDK',
                'python')
        else: # for linux, raspberry pi, etc.
            path = join('/usr', 'share', 'walabot', 'python')
        self.wlbt = load_source('WalabotAPI', join(path, 'WalabotAPI.py'))
        self.wlbt.Init()
        self.wlbt.SetSettingsFolder()
    def isConnected(self):
        try:
            self.wlbt.ConnectAny()
        except self.wlbt.WalabotError as err:
            if err.code == 19: # 'WALABOT_INSTRUMENT_NOT_FOUND'
                return False
        return True
    def setParams(self, rParams, thetaParams, phiParams, thld, mtiMode):
        self.wlbt.SetProfile(self.wlbt.PROF_SENSOR)
        try:
            self.wlbt.SetArenaR(*tuple(map(float, rParams)))
            self.wlbt.SetArenaTheta(*tuple(map(float, thetaParams)))
            self.wlbt.SetArenaPhi(*tuple(map(float, phiParams)))
            self.wlbt.SetThreshold(float(thld))
        except self.wlbt.WalabotError as err:
            self.master.controlGUI.errorVar.set(str(err))
        if mtiMode == '0':
            self.wlbt.SetDynamicImageFilter(self.wlbt.FILTER_TYPE_MTI)
        else:
            self.wlbt.SetDynamicImageFilter(self.wlbt.FILTER_TYPE_NONE)
        self.wlbt.Start()
    def getArenaParams(self):
        rParams = self.wlbt.GetArenaR()
        thetaParams = self.wlbt.GetArenaTheta()
        phiParams = self.wlbt.GetArenaPhi()
        threshold = self.wlbt.GetThreshold()
        return rParams, thetaParams, phiParams, threshold
    def calibrate(self):
        self.wlbt.StartCalibration()
        while self.wlbt.GetStatus()[0] == self.wlbt.STATUS_CALIBRATING:
            self.wlbt.Trigger()
    def getRawImageSliceDimensions(self):
        return self.wlbt.GetRawImageSlice()[1:3]
    def triggerAndGetRawImageSlice(self):
        self.wlbt.Trigger()
        return self.wlbt.GetRawImageSlice()[0]
    def getFps(self):
        return int(self.wlbt.GetAdvancedParameter('FrameRate'))

def configureWindow(root):
    root.title('Walabot - Piano Gestures')
    iconPath = join(dirname(argv[0]), 'walabot-icon.png')
    iconFile = tk.PhotoImage(file=iconPath)
    root.tk.call('wm', 'iconphoto', root._w, iconFile) # set app icon
    root.geometry('+{}+{}'.format(APP_X, APP_Y))
    root.resizable(width=False, height=False)
    root.option_add('*Font', 'TkFixedFont')

def startApp():
    root = tk.Tk()
    configureWindow(root)
    MainGUI(root).pack()
    root.mainloop()

if __name__ == '__main__':
    startApp()
