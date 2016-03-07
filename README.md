# Mouse Acceleration Control
A simple gui written in python2, pyqt4 for tweaking the various mouse acceleration settings avaiable on Xorg with xinput

## How it works
Simple enough, just select the device from the top dropdown menu. The current settings are automaticaly loaded.  
Start plaing with the sliders and the push the Apply button to test them.
If you like, you can save and restore setting as profiles.

## What those settings mean?
Try and guess, or check the documentation on
http://www.x.org/wiki/Development/Documentation/PointerAcceleration/

## Red sliders?
The lower set of slider can be disabled (red) if the device is not "drived" by xinput. Usually this mean that you have libinput installed. For fixing you should play with the Xorg conf file to force the use of xinput. Or uninstalling the related package (on arch is xf86-input-libinput)

## Apply on startup?
I can't provide a way to do it. Because you need to edit Xorg configuration as root, or with some autostart script, that can depend on desktop enviroment.

### The code is a mess!
Thanks :D

### Your english is awfull
Thanks again :D
