from __future__ import print_function # python2-python3 compatibility
from imp import load_source
from os.path import join, dirname
from sys import platform, argv
from math import sqrt, sin, cos, radians
try: import Tkinter as tk
except: import tkinter as tk
from os import system
import pygame

IMG_PATH = join(dirname(argv[0]), 'img')
ICON_PATH = join(IMG_PATH, 'icon.png')
BLANK_KEYS_PATH = join(IMG_PATH, 'keys-blank.gif')
HIGLGHT_PATH = lambda n: join(IMG_PATH, 'highlight-'+n+'.gif')
PRESSED_PATH = lambda n: join(IMG_PATH, 'pressed-'+n+'.gif')
CONNECT_WALABOT_PATH = join(dirname(argv[0]), 'connect-walabot.gif')
SOUND_PATH = lambda n : join(dirname(argv[0]), 'sound', 'piano-'+n+'.wav')
NOTES = {1: 'b', 2: 'a', 3: 'g', 4: 'f', 5: 'e', 6: 'd', 7: 'c'}
APP_X, APP_Y = 150, 50 # (x, y) of left corner of the window (in pixels)
R_MIN, R_MAX, R_RES = 2, 25, 5 # walabot SetArenaR values
THETA_MIN, THETA_MAX, THETA_RES = -45, 45, 5 # walabot SetArenaTheta values
PHI_MIN, PHI_MAX, PHI_RES = -60, 60, 5 # walabot SetArenaPhi values
TSHLD = 15 # walabot SetThreshold value
X_MAX = R_MAX * sin(radians(THETA_MAX))
Y_MAX = R_MAX * cos(radians(THETA_MAX)) * sin(radians(PHI_MAX))
Z_MAX = R_MAX * cos(radians(THETA_MAX)) * cos(radians(PHI_MAX))

class MainGUI(tk.Label):
    def __init__(self, master):
        self.img = tk.PhotoImage(file=BLANK_KEYS_PATH)
        tk.Label.__init__(self, master, image=self.img)
        self.wlbt = Walabot(self)
        self.after(500, self.startWlbt)
        self.keyNum = lambda y: int(7 * (y + Y_MAX) / (2 * Y_MAX)) + 1
        self.pygame = pygame
        self.pygame.init()
        self.playedLastTime = False
    def startWlbt(self):
        self.alertIfWalabotIsNotConnected(self)
        self.wlbt.setParametersAndStart()
        self.lastKeyPressed = 0
        self.detectTargetAndReply()
    def alertIfWalabotIsNotConnected(self, master):
        """
        connectWalabotImage = tk.PhotoImage(file=CONNECT_WALABOT_PATH)
        connectWalabotLabel = tk.Label(master, image=connectWalabotImage)
        if not self.wlbt.isConnected():
            connectWalabotLabel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.update_idletasks()
        """
        while not self.wlbt.isConnected():
            print('not connected')
    def detectTargetAndReply(self):
        self.after_idle(self.detectTargetAndReply)
        coordinates = self.wlbt.getClosestTargetCoordinates()
        system('clear')
        if not coordinates: # no targets were found
            self.resetPianoImage()
            self.playedLastTime = False
            return
        xValue, yValue, zValue = coordinates[0], coordinates[1], coordinates[2]
        key = self.keyNum(yValue) # key number according to y target value
        key = 7 if key == 8 else key # due to arena inconsistencies
        if zValue < R_MAX and key == self.lastKeyPressed:
            if abs(xValue) < X_MAX / 2: # hand is at 'press' area
                self.pressAndPlayKey(key)
            else: # hand is at 'highlight' area
                self.highlightKey(key)
                self.playedLastTime = False
        else: # hand is too far from the Walabot
            self.resetPianoImage()
            self.playedLastTime = False
        self.lastKeyPressed = key
    def pressAndPlayKey(self, key):
        # TODO: play sound
        print('Press:', int(key))
        self.img = tk.PhotoImage(file=PRESSED_PATH(str(key)))
        self.configure(image=self.img)
        if not self.playedLastTime:
            self.pygame.mixer.music.load(SOUND_PATH(NOTES[key]))
            self.pygame.mixer.music.play()
            self.playedLastTime = True
    def highlightKey(self, key):
        print('Highlight:', int(key))
        self.img = tk.PhotoImage(file=HIGLGHT_PATH(str(key)))
        self.configure(image=self.img)
    def resetPianoImage(self):
        print('Too far')
        self.img = tk.PhotoImage(file=BLANK_KEYS_PATH)
        self.configure(image=self.img)

class Walabot:
    def __init__(self, master):
        """ Initialize the Walabot SDK, importing the Walabot module,
            set the settings folder path and declare the 'distance' lambda
            function which calculates the distance of a 3D point from the
            origin of axes.
        """
        self.master = master
        if platform == 'win32': # for windows
            path = join('C:/', 'Program Files', 'Walabot', 'WalabotSDK',
                'python')
        else: # for linux, raspberry pi, etc.
            path = join('/usr', 'share', 'walabot', 'python')
        self.wlbt = load_source('WalabotAPI', join(path, 'WalabotAPI.py'))
        self.wlbt.Init()
        self.wlbt.SetSettingsFolder()
        self.distance = lambda t: sqrt(t.xPosCm**2 + t.yPosCm**2 + t.zPosCm**2)
    def isConnected(self):
        """ Connect the Walabot, return True/False according to the result.
            Returns:
                isConnected     'True' if connected, 'False' if not
        """
        try:
            self.wlbt.ConnectAny()
        except self.wlbt.WalabotError as err:
            if err.code == 19: # 'WALABOT_INSTRUMENT_NOT_FOUND'
                return False
        return True
    def setParametersAndStart(self):
        """ Set the Walabot's profile, arena parameters, and filter type. Then
            start the walabot using Start() function.
        """
        self.wlbt.SetProfile(self.wlbt.PROF_SENSOR)
        self.wlbt.SetArenaR(R_MIN, R_MAX, R_RES)
        self.wlbt.SetArenaTheta(THETA_MIN, THETA_MAX, THETA_RES)
        self.wlbt.SetArenaPhi(PHI_MIN, PHI_MAX, PHI_RES)
        self.wlbt.SetThreshold(TSHLD)
        self.wlbt.SetDynamicImageFilter(self.wlbt.FILTER_TYPE_MTI)
        self.wlbt.Start()
    def getClosestTargetCoordinates(self):
        """ Trigger the Walabot and retrieve the recieved targets using
            GetSensorTargets(). Then calculate the closest target (to the
            walabot) and return it's coordinates.
            Returns:
                x, y, z     Coordinates of closest target, 'None' (at each
                            coordinate if no targets were found)
        """
        self.wlbt.Trigger()
        targets = self.wlbt.GetSensorTargets()
        if targets:
            target = max(targets, key=self.distance)
            return target.xPosCm, target.yPosCm, target.zPosCm

def configureWindow(root):
    """ Set configurations for the GUI window, such as icon, title, etc.
    """
    root.title('Walabot - Piano Gestures')
    root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=ICON_PATH))
    root.geometry('+{}+{}'.format(APP_X, APP_Y))
    root.resizable(width=False, height=False)

def startApp():
    """ Main function.
    """ # TODO: add func documentation.
    root = tk.Tk()
    configureWindow(root)
    MainGUI(root).pack()
    root.mainloop()

if __name__ == '__main__':
    startApp()
