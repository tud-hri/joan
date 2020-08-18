# Working with JOAN and CARLA on shared TU Delft hardware

You will most likely create your own project (a map) on a shared computer. To make sure we keep everything organized, you need to follow the following steps precisely. Follow these steps for every computer you want to install your project on.

## How to install your project on a shared computer

- Login with your TU Delft NETID. 

!!! Important
    When you log in to a computer for the first time, the computer needs to be connected with a LAN cable to the TU Delft network.

- If correct, CARLA (see `c:\carla`), Python 3.8.5 (64 bit) and PyCharm are already installed. If not, follow the CARLA build steps ([here](setup-carla-windows.md)) and install the community version of PyCharm. If CARLA is already present, then you obviously do not need to rebuild. Also, you should not have to reinstall Python.

!!! Note
    If CARLA needs rebuilding (for example because we upgraded Python version), this needs to be done using the administrator's account. Ask your supervisor.

### Steps to setup JOAN

You can run your JOAN and CARLA project on any TUD computer that we prepared for you. For each PC, you need to clone and setup your JOAN project. Follow all the steps in the [setting up JOAN guide](setup-joan.md) (step 1 only when you first create your JOAN project, else, only do steps 2-5). 


### Steps to setup your own CARLA map

You will probably need to build your own map with a road in CARLA for your own project.

!!! Important
    You need to be very careful not to tamper with another student's CARLA project or the CARLA installation itself. Therefore, please be cautious when working in the `c:\carla` folder. __You can screw up your fellow students' projects if you don't.__

We prepared a map for you as a template/starting point called `DebugMap`, which you can find in `C:\carla\Unreal\CarlaUE4\Content\Carla\Maps`.


- Create a folder with name `<YEAR>_<NETID>` in the directory `C:\carla\Unreal\CarlaUE4\Content\Developers\`. 
- Download the 
- Open the Epic Game Launcher, you need to login (use your login of choice)

!!! Warning
    UNDER CONSTRUCTION
    
    - In this new folder, create a folder `Maps`. 
    - __Copy__ the folder `DebugMap` and file `DebugMap.umap` and `DebugMap_BuiltData.uasset` to the folder you just created.
    - Create a folder `OpenDrive`
    - Copy `DebugMap.xodr` to this folder