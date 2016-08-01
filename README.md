# AirPiano - A Walabot Application

This is a simple Walabot game application that acts as an air piano.

* The code is written in Python and works on both Python 2 and Python 3.  
* The app was tested on Windows 10 and Ubuntu 16.04.  
* The app's using [PyGame](http://www.pygame.org) to play the sound files.
* Piano sound files are from [wav-piano-sound](https://github.com/pffy/wav-piano-sound).

##### What does the Walabot Do?

The app uses the Walabot sensor to detect a hand inside it's arena and mimic a piano.  
The X axis is used to determine if the hand is hovering the keys or pressing them.  
The Y axis is used to determine the exact key which will be pressed.  

### How to use

1. [Install the Walabot SDK.](http://api.walabot.com/_install.html)
2. Download and install [PyGame](http://www.pygame.org/download.shtml).
3. Position the Walabot as the image below.
4. Run `air-piano.py` and start playing! :musical_keyboard:

**IMPORTANT NOTE:** Current Walabot settings are for vMaker18.

##### Positioning the Walabot

![Positioning the Walabot](https://raw.githubusercontent.com/Walabot-Projects/Walabot-AirPiano/master/example.png)

### Editing the code

At the top of the code you can find variables that can be changed easily without dealing with the "heavy" part of the code.  
All those variables should vary between different Walabot boards, operating systems, operating machines, etc.  
'Walabot Settings' variables are necessary to set the Walabot arena.  
'App Settings' variables are required for a proper flow of the app.

##### Walabot Settings

* `R_MIN, R_MAX, R_RES`: Walabot [`SetArenaR`](http://api.walabot.com/_walabot_a_p_i_8h.html#aac6cafa27c4a7d069dd64c903964632c) parameters. Determines how low (from it's location) the Walabot will "see".
* `THETA_MIN, THETA_MAX, THETA_RES`:  Walabot [`SetArenaTheta`](http://api.walabot.com/_walabot_a_p_i_8h.html#a3832f1466248274faadd6c23127b998d) parameters. The theta axis is ignored in this app, those values should always be the "lowest" possible.
* `PHI_MIN, PHI_MAX, PHI_RES`: Walabot [`SetArenaPhi`]((http://api.walabot.com/_walabot_a_p_i_8h.html#a9afb632b5cce965eba63b323bc579557)) parameters. Used to set how "far" the Walabot will "see" (from it's location).
* `THRESHOLD`: Walabot [`SetThreshold`](http://api.walabot.com/_walabot_a_p_i_8h.html#a4a19aa1afc64d7012392c5c91e43da15) parameter. Lower this value if you wish to detect objects smaller the a man's head.

A comprehensive explanation about the Walabot imaging features can be found [here](http://api.walabot.com/_features.html).

##### App Settings

* `IMG_PATH`: Path to the piano images.
* `SOUND_PATH`: Path to the sound files.
* `APP_X, APP_Y`: (x, y) of left corner of the window (in pixels)
* `Y_SCALE`: determines the ratio of Y axis that counts as keys range. Used to ignore the edges of the Walabot's arena due to inconsistencies at the edges.
