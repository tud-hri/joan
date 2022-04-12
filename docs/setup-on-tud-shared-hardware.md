# Working with JOAN and CARLA on shared TU Delft hardware

These instructions are specifically for students at TU Delft, but they may be useful for others too. 

If you are a student at the TUD, you will share hardware (computers, steering wheels) with your fellow students. To make sure we keep everything organized, you need to follow the next steps for every computer you want to install your project on.

---

## Step 1: preparations

- Log in with your TU Delft NetID.
- If correct, CARLA (see `C:\carla`), python 3.8.5 (64 bit; type `python` in a command terminal, you should see a python version > 3.8), and PyCharm are already installed. 

!!! Note
    If you need to do a fresh install (CARLA, python, PyCharm, ...) on the computer, follow the steps in both the [Build CARLA on Windows](setup-carla-windows.md) and [Install JOAN](setup-joan.md) pages. This needs to be done as an administrator to make CARLA, Python, and PyCharm available for everyone. Ask your supervisor first.

## Step 2: clone your JOAN project

You can run your JOAN and CARLA project on any TUD computer that we prepared for you. For each PC, you need to clone and set up your JOAN project. Follow the steps in [Install JOAN](setup-joan.md): do step 1 only when you first create your JOAN project, else, only do steps 2-5. 

## Step 3: setup your own CARLA map

You will probably need to build your own map with a road in CARLA for your project.

!!! Important
    Maps need to be in the `C:\carla` directory. You need to be very careful not to tamper with another student's CARLA project or the CARLA installation itself. Therefore, please be cautious when working in the `C:\carla` folder. __You can screw up your fellow students' projects if you do not!__

We prepared a template map (`DebugMap`), which you can find in `C:\carla\Unreal\CarlaUE4\Content\Carla\Maps`.

To create your own map: 

- Create a folder with the name `<YEAR>_<NETID>` in the directory `C:\carla\Unreal\CarlaUE4\Content\Research\` (create the folder `Research` if it does not exist).
- Download the template map [here](https://www.dropbox.com/s/34g6ln1up7azssp/120222_DebugMap.zip?dl=0){target="_blank"}, extract it, and copy the folder called `Maps` it in your
  own folder under `C:\carla\Unreal\CarlaUE4\Content\Research\<YEAR>_<NETID>\`.
- Open the Epic Game Launcher (you might need to log in; use your login of choice).
- Launch Unreal Engine, top-right corner (Unreal should be installed; if not, restart the Epic Game Launcher or reboot the computer, this normally works).
- In Unreal Engine, CarlaUE4 should be listed under 'Recent projects'. If not, open the `CarlaUE4` project (browse to `C:\carla\Unreal\CarlaUE4\` and open `CarlaUE4.uproject`). 
- The CarlaUE4 will now start; this may take a while if you start it for the first time.
- To open your own level, click `File` &rarr; `Open level` and select `DebugMap.umap` __in your folder__ (navigate to your 'Research' folder!)
- If you want, you can rename your map to a more descriptive name (right-click on the map in the editor &rarr; `rename`, for example, `<YEAR>_Map_<NAME>_<SHORT DESCRIPTION>`, or use `File` &rarr; `Save as`).
- Your level will load, but this may take some time.
- To run the Unreal Engine, hit the play button.
  
!!! Warning
    Make sure to load your own map, so double-check that you are in the right directory when opening your level!
    
## Reserving and sharing the TUD computers

We have limited hardware at the TUD for you to work on. Please share the PCs fairly with your fellow students. You can coordinate through Slack (joan-forum, for example).
