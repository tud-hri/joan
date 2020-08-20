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


- Create a folder with name `<YEAR>_<NETID>` in the directory `C:\carla\Unreal\CarlaUE4\Content\Research\` (create the folder `Research` if it does not exist). 
- Download the template map [here](https://www.dropbox.com/s/qu8ejogahhre0el/Template_Maps_08_2020.zip?dl=0), extract it, and copy the folder called `Maps` it in your own folder under `C:\carla\Unreal\CarlaUE4\Content\Research\<YEAR>_<NETID>\`.
- Open the Epic Game Launcher (you might need to login (use your login of choice)).
- Launch Unreal Engine, top-right corner (Unreal should be installed).
- In Unreal Engine, CarlaUE4 should be listed under 'Recent projects'. If not, open the `CarlaUE4` project (browse to `C:\carla\Unreal\CarlaUE4\` and open `CarlaUE4.uproject`). 
- The CarlaUE4 will now start; this may take a while if you start it for the first time.
- To open your own level, click `File` &rarr; `Open level` and select `DebugMap.umap` __in your folder__ (navigate to your folder!)
- If you want, you can rename your map to a more descriptive name (right-click on the map in the editor &rarr; rename, for example <YEAR>_<NAME>_<SHORT DESCRIPTION>) or you can save the DebugMap as another name.
- Your level will load, but this may take some time.
- To run your map, hit the play button.
  


!!! Warning
    Make sure to load your own map, so double check that you are in the right directory when opening your level!