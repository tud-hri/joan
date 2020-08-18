# SensoDrive Explanation
The SensoDrive is a powerful/professional actuated steering wheel for simulation purposes, it communicates over CAN bus and 
can be used with JOAN. This section of the documentation mainly explains how to set and get parameters from the wheel
and what has been done in JOAN to make it work.

!!! Note
    Please be careful if you are going to work with the SensoDrive, it can deliver upto 20Nm of torque, which is quite a lot
    if you are testing with it ALWAYS KEEP YOUR THUMBS OUT OF THE WHEEL!
    
## Hardware
The SensoDrive's hardware mainly consists of three necessary parts.

- `SensoWheel` This is the biggest part, where the BLDC motor is attached to on the frame
- `Steering wheel` Self explanatory, can be removed and switched for other wheels
- `PCAN USB Dongle` This is the bridge between the internal controller of the sensodrive and your PC

## Setting up your PC for a sensodrive
Before you can plug and play the SensoDrive with JOAN (on a new PC, all pc's that we use on the university are already 
prepared) you need to get:

1. The drivers for the PEAK systems PCAN USB. You can find them here: [link](https://www.peak-system.com/PCAN-USB.199.0.html?&L=1)
2. The DLL's (Dynamic Linker Libraries) for PCAN-Basic-API. These can also be found here:  [link](https://www.peak-system.com/PCAN-USB.199.0.html?&L=1)

!!! Note
    Make sure you copy the appropriate DLL's to your windows system folders. So for the 32 bit version put it in System32 for the 64 bit version
    put it in Syswow64.

Now you should be all set to use the PCAN-Basic API with the SensoDrive. 

## Software Explanation
This section will describe how the current communication with the SensoDrive with PCAN is done. If you really want
to know all about CAN communication protocols and how the PCAN API works please read the extensive documentation
provided by PEAK Systems. (Same link as the drivers)

The main document of reference for this section is the 'Software manual Version 3.10.0 SENSO-wheel' by the SensoDrive company
itself. (FIX LINK HERE) This explains all relevant info regarding the messages you can send and receive and what the messages
should look like that you send. For the rest of this section we will explain different things you can do and how you would implement this 
in python.