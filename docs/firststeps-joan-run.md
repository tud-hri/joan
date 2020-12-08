# Running JOAN and CARLA

These are the steps required from executing JOAN to driving your vehicle in CARLA. This quick guide will include a lot of 
references to more detailed documentation for the modules themselves. If you cannot seem to grasp what is going on in the GIFS
below then please look at that documentation. Other than that the text descriptions in this section will be minimal, and mostly
GIFs and pictures! :)

### 1. Run JOAN and CARLA

Out-of-the-box, JOAN has a couple of modules included (for example CarlaInterface, HardwareManager, DataRecorder, Haptic Controller Manager , DataPlotter and  the Experiment Manager). These should show up in JOAN HQ, JOAN's headquarters.

- To run JOAN, either execute (in a terminal):
```
    python main.py
```
    
Make sure that your virtual environment is activated (each line should start with `(venv)`).

Or, if you use PyCharm, click the green play button or right-click on `main.py` and click on `Run main`.

- To start CARLA, open the CarlaUE4, and open your map in CarlaUE4. 

- Hit the big play button in CarlaUE4

See below the GIF for step 1 :
[ ![](gifs/joan-run-firststep.gif) ](gifs/joan-run-firststep.gif)

### 2. Add an input device
Hit the `add hardware button` select your input, put in the appropriate settings and save. (For more details please
go to [using the hardware manager](modules-hardwaremanager.md#using_hw_manager).

In the example below we use a Keyboard.
[ ![](gifs/joan-run-add-input.gif) ](gifs/joan-run-add-input.gif)

### 3. Add a vehicle

### 5. Initialize

### 6. Setup the variables you'd like to record and where to save them 

### 7. Get Ready

### 8. Run and Drive!




---

