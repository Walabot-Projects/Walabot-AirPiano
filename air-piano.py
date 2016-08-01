from __future__ import print_function # python2-python3 compatibility
from imp import load_source
from os.path import join, dirname
from sys import platform, argv
from math import sqrt, sin, cos, radians
from collections import deque
import pygame
try: import Tkinter as tk
except ImportError: import tkinter as tk

IMG_PATH = join(dirname(argv[0]), 'img')
ICON_PATH = join(IMG_PATH, 'icon.gif')
BLANK_KEYS_PATH = join(IMG_PATH, 'keys-blank.gif')
CONNECT_WALABOT_PATH = join(IMG_PATH, 'connect-device.gif')
HIGLGHT_PATH = lambda n: join(IMG_PATH, 'highlight-'+str(n)+'.gif')
PRESSED_PATH = lambda n: join(IMG_PATH, 'pressed-'+str(n)+'.gif')
SOUND_PATH = lambda n : join(dirname(argv[0]), 'sound2', 'piano-'+n+'.wav')
NOTES = {1: 'b', 2: 'a', 3: 'g', 4: 'f', 5: 'e', 6: 'd', 7: 'c'}
APP_X, APP_Y = 150, 50 # (x, y) of left corner of the window (in pixels)

R_MIN, R_MAX, R_RES = 2, 20, 5 # walabot SetArenaR values
THETA_MIN, THETA_MAX, THETA_RES = -25, 5, 2 # walabot SetArenaTheta values
PHI_MIN, PHI_MAX, PHI_RES = -75, 75, 2 # walabot SetArenaPhi values
TSHLD = 15 # walabot SetThreshold value
VELOCITY_THRESHOLD = 0.7 # captured vel bigger than that counts as key-press
Y_MAX = R_MAX * cos(radians(abs(THETA_MIN))) * sin(radians(PHI_MAX))

def getMedian(nums):
    """ Calculate median of a given set of values.
        Arguments:
            nums            An iterable of numbers.
        Returns:
            median          The median of the given values.
    """
    nums = sorted(nums)
    if len(nums) % 2 == 1:
        return nums[((len(nums)+1) / 2) - 1]
    else:
        return float(sum(nums[(len(nums)/2)-1:(len(nums)/2)+1])) / 2.0

def getVelocity(data):
    """ Calculate velocity of a given set of values using linear regression.
        Arguments:
            data            An iterable of numbers.
        Returns:
            velocity        The estimates slope.
    """
    sumY = sumXY = 0
    for x, y in enumerate(data):
        sumY, sumXY = sumY + y, sumXY + x*y
    if sumXY == 0: return 0 # no values / one values only / all values are 0
    sumX = x * (x+1) / 2 # Gauss's formula - sum of first x natural numbers
    sumXX = x * (x+1) * (2*x+1) / 6 # sum of sequence of squares
    return (sumXY - sumX*sumY/(x+1)) / (sumXX - sumX**2/(x+1))

def getKeyNum(y):
    """ Calculate key number (out of 7) given a y position.
        The keynumber is determined only by the Y axis of the walabot. The
        given Y is between -Y_MAX and Y_MAX. Thus the key can be calculated
        with a simple formula.
        Argumets:
            y               A value between -Y_MAX and Y_MAX.
        Returns:
            key             The key number (between 1 and 7).
    """
    key = int(7 * (y + Y_MAX) / (2 * Y_MAX)) + 1
    return 7 if key == 8 else key # due to arena inconsistencies

class MainGUI(tk.Label):

    def __init__(self, master):
        self.img = tk.PhotoImage(file=BLANK_KEYS_PATH)
        tk.Label.__init__(self, master, image=self.img)
        self.wlbt = Walabot(self) # init the Walabot SDK
        self.after(750, self.startWlbt) # necessary delay to open the window
        self.pygame = pygame # used to play piano sound
        self.pygame.init()
        self.playedLastTime = False
        self.highlightImages = [tk.PhotoImage(file=HIGLGHT_PATH(k+1))
            for k in range(7)]
        self.pressedImages = [tk.PhotoImage(file=PRESSED_PATH(k+1))
            for k in range(7)]
        self.lastTargets = deque([None] * 5)

    def startWlbt(self):
        if self.alertIfWalabotIsNotConnected():
            self.wlbt.setParametersAndStart()
            self.detectTargetAndReply()

    def alertIfWalabotIsNotConnected(self):
        if not self.wlbt.isConnected():
            self.img = tk.PhotoImage(file=CONNECT_WALABOT_PATH)
            self.configure(image=self.img)
            self.after_idle(self.startWlbt)
            return False
        self.img = tk.PhotoImage(file=BLANK_KEYS_PATH)
        self.configure(image=self.img)
        return True

    def detectTargetAndReply(self):
        self.after_idle(self.detectTargetAndReply)
        target = self.wlbt.getClosestTarget()
        self.lastTargets.popleft()
        self.lastTargets.append(target)
        if not target:
            self.configure(image=self.img)
            self.playedLastTime = False
            return
        median = getMedian(t.yPosCm for t in self.lastTargets if t is not None)
        vel = getVelocity(t.xPosCm for t in self.lastTargets if t is not None)
        key = getKeyNum(median)
        if target.zPosCm < R_MAX:
            if target.xPosCm >= 0 and vel > VELOCITY_THRESHOLD: # 'press' area
                self.pressAndPlayKey(key)
            else: # hand is at 'highlight' area
                self.configure(image=self.highlightImages[key-1])
                self.playedLastTime = False
        else: # hand is too far from the Walabot
            self.configure(image=self.img)
            self.playedLastTime = False

    def pressAndPlayKey(self, key):
        """ Given a key, change the piano image to one where the certain key
            is pressed. Play a piano sound corresponding to the key if in the
            last iteration no sound was played.
        """
        self.configure(image=self.pressedImages[key-1])
        if not self.playedLastTime:
            self.pygame.mixer.music.load(SOUND_PATH(NOTES[key]))
            self.pygame.mixer.music.play()
            self.playedLastTime = True

class Walabot:
    """ This class is designed to control Walabot device using the Walabot SDK.
    """

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

    def getClosestTarget(self):
        """ Trigger the Walabot and retrieve the recieved targets using
            GetSensorTargets(). Then calculate the closest target (to the
            walabot) and returns it.
            Returns:
                target      Of SensorTarget type. The closest one. May be
                            'None' if no targets where found.
        """
        self.wlbt.Trigger()
        targets = self.wlbt.GetSensorTargets()
        try:
            return max(targets, key=self.distance)
        except ValueError: # 'targets' is empty; no targets were found
            return None

def configureWindow(root):
    """ Set configurations for the GUI window, such as icon, title, etc.
    """
    root.title('Walabot - Piano Gestures')
    root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=ICON_PATH))
    root.geometry('+{}+{}'.format(APP_X, APP_Y))
    root.resizable(width=False, height=False)

def startApp():
    """ Main function. Create and init the MainGUI class, which runs the app.
    """
    root = tk.Tk()
    configureWindow(root)
    MainGUI(root).pack()
    root.mainloop()

if __name__ == '__main__':
    startApp()
