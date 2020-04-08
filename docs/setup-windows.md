# Setting up the simulator for Windows Documentation

## Introduction
In order to properly setup the simulation software on Windows several packages and steps are required, which will be elaborated upon in this section.
!!! Note
    This setup guide is extensive, if you are familiar with building software and installing new libraries etc it might be easier to just scan through this guide instead of going through it thoroughly. However, if you don't, please follow the guide step by step.
## Hardware Requirements
* __x64 system.__ The simulator should run in any 64 bits Windows system.  
* __50GB disk space.__ Installing all the software needed and CARLA will require quite a lot of space. Make sure to have about 50gb of space (especially since you will also need a visual studio 2017 install)
* __An adequate GPU.__ CARLA aims for realistic simulations, so the server needs at least a 4GB GPU. If VR is required a turing based GPU (for example the RTX branch of NVIDIA is highly recommended!)
* __Two TCP ports and good internet connection.__ 2000 and 2001 by default. Be sure neither the firewall nor any other application are blocking these. 


## Required Software 
### Minor Building Dependencies
Please make sure you have the following programs installed before continuing. If you will be installing them now, please read the instructions below carefully to prevent problems later on in the installation process.

* __[CMake](https://cmake.org/download/)__ *A small software package to make the CARLA build can compile C-code.* Please follow the link, scroll down and download the "Windows win64-x64 Installer" (there is no need to download the source). When installing select the option "Add CMake to the system PATH for all users"
* __[Git](https://git-scm.com/downloads/win)__ *Ensures version control of both the python software and CARLA64-bit Git for Windows Setup.* Please follow the link and download the "64-bit Git for Windows Setup.". During installation you can keep all the default settings but especially make sure to select the (default) option "Use Git from the Windows command prompt".
* __[Make](http://gnuwin32.sourceforge.net/packages/make.htm)__ *Generates the executables.* Please follow the link and download the "Complete package, except sources" setup. Install it and after installing add the binary folder (C:\Program Files (x86)\GnuWin32\bin by default) the the system PATH variable. follow the link in the info box below if you're not sure how to do this.

!!! Important
    When you already have installed versions of the above mentioned software please make sure that the binary folders are added to the system's PATH variable! If you don't know how to do so, please click this link: [Adding to System Variables](/sysPath). If you have followed the instructions above, only make has to be added to the PATH manually.

### Visual Studio 2017
[Visual studio 2017](https://visualstudio.microsoft.com/vs/older-downloads/) is used as main building tool for the CARLA simulator. Make sure to use the 2017 version, newer or older version will not work. 

#### Build tools
For building Carla only the vs 2017 and .NET build tools are required. Only installing the build tools requires significantly less disk space then a full version of Visual Studio.
 The build tools can be downloaded and installed by following the link above, please make sure to download the "Build Tools for Visual Studio 2017" executable. Finding them will require creating an account and scrolling down in the extensive list of downloads. When installing, select the "vs 2017 build tools" and ".NET build tools" checkboxes in the left pane of the visual studio installer and select all the default options plus "Windows 8.1 SDK" in the column on the right. 

#### Visual Studio community edition
Alternatively, you can install the full Visual Studio community edition, this is a complete code editor but it will require some disk space. Download the Visual Studio Community edition installer by following the link above, again this will require creating an account and navigation the extensive downloads list. 
When installing please make sure you install it with the following properties:

* __Windows 8.1 SDK.__ You can select this from the installation details tab
* __x64 Visual C++ Toolset__ Choose the __Desktop development with C++__, enabling a x64 command prompt that will be needed. To access this prompt type in x64 in the search bar of windows 10. If properly installed it should show up like this:
![alt text](Images/commandPrompt.png "x64 Command prompt")

### Unreal Engine 4.24
Go to __[Unreal Engine](https://www.unrealengine.com/download)__ and download the Epic Games Launcher. You will have to create an epic games account before you are able to download the epic games launcher. In the epic games launcher go to 'unreal engine' in the left menu bar and then to 'library' and you should see something like this:
![alt text](Images/epicGamesMenu.png "Epic Games Menu")
Download Unreal Engine 4.24.x. Make sure to run it in order to check that everything was properly installed.

### Python3 x64
 Install python 3 and __make sure you get the x64 version__ else it will not work, there is even some speculation that if you have a x32 version installed it can cause conflicts so its best to only have x64. At the time of writing this guide the working version of python is __[Python 3.8.2](https://www.python.org/downloads/release/python-382/)__

To check if we can run Python from the command line. And if the python command links to the correct version of Python, it might not if you have multiple versions of Python installed. Open a command line window and type:

    python

This should give a response similar to the one below. Please make sure that you are running the Python version you have just installed.

    Python 3.8.2 (tags/v3.8.2:7b3ab59, Feb 25 2020, 23:03:10) [MSC v.1916 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    
If Python does not start or if a different version is shown, you should make sure that the folder of your Python installation is in your PATH variables. Please check the bit on build dependencies above if you need help. If python opens Python 2.x but you also have Python 3.x installed, usually typing python3 will open the python 3.x version. Another known issue on Windows 10 is Windows opening the app store, please check [this page](https://superuser.com/questions/1437590/typing-python-on-windows-10-version-1903-command-prompt-opens-microsoft-stor) if that happens.

Please not the >>> symbols indicating that you are now within a python environment. To close Python again type:

    >>> exit() 

!!! Important
    Really do use python 3, do not try and use python 2 it will just not work.

### Visual Code (Optional)
Of course you are free to use any IDE you are comfortable with (pycharm, spyder, anaconda), however the authors and creators of the JOAN simulator have consistently used __[Visual Studio Code](https://code.visualstudio.com/)__ due to easy source control functionality.

## Building and installing CARLA & the CARLA PythonAPI
Before we start putting in commands in the recently setup x64 VS command prompt it is important to double check if you have all necessary software, and have it installed properly before you read on.
The build and install of the bare bones CARLA simulator can be divided in the following steps:

1. __Clone the repository__
2. __Get the latest CARLA assets__
3. __Get specific JOAN assets__
4. __Build PythonAPI__
5. __Build & Launch CARLA__
6. __Wait and pray that your PC is fast enough to compile all the shaders in Unreal in a reasonable amount of time__
7. __Adding JOAN Assets inside Unreal__

The steps will be explained 1 step at the time with screenshots and command line commands you can easily copy paste.
### Step 1, Cloning the repository
To clone the repository either go to this link and download the zip, copy the link and clone it with git the way you prefer, or type in the following command in the command line:

    #Clone the CARLA repository (will clone in the folder you are currently in in your terminal)
    git clone https://github.com/carla-simulator/carla

!!! Important 
    The build will fail if the path to carla contains spaces, so please clone carla to a folder without spaces in the path. If in doubt; use C:\carla. To do this navigate to C:\ in a command window and call git clone from there, the carla folder will be created automatically. 

After cloning verify that you have actually cloned the repository, it should look like this:
![alt text](Images/gitClone.png "cloned repository")

### Step 2, getting latest CARLA assets
To get the latest CARLA assets open up the folder 'Utils' in the 'carla' folder that you have just created in step 1, and open the file 'contentversions.txt', see below:
![alt text](Images/utilScreenshot.png "cloned repository")

This text file contains the instructions of what to do to download the latest assets, for now get the 0.9.8 version, you can also click this link: 
__[Carla Assets Link](http://carla-assets.s3.amazonaws.com/20200306_06b6cb1.tar.gz)__

Unpack these assets in \carla\Unreal\CarlaUE4\Content\Carla

### Step 3, get speficic JOAN Assets
To have a nice car interior which also turns the wheel if you turn it some extra assets are required. You can download them from this link: __[Dropboxlink](https://www.dropbox.com/s/7cboucrb81sdlxq/JOAN_Assets.zip?dl=0)__ It contains:

* JOAN_Blueprints 
* JOAN_Static
* JOAN_Map

Please copy the contents of JOAN_Blueprints to __..\carla\Unreal\CarlaUE4\Content\Carla\Blueprints__ to be neat copy the vehicles in the vehicles blueprint map.

Copy the contents of JOAN_Static (only cars) to the __..\carla\Unreal\CarlaUE4\Content\Carla\Static\Vehicles\4Wheeled__ folder.

Lastly copy the contents of JOAN_Map to the __..\carla\Unreal\CarlaUE4\Content\Carla\Maps__ folder. 

!!! Note
    Copy the .xodr file into the opendrive folder

### Step 4, build the PythonAPI
In order to build the python API open the 'x64 Native Tools Command Prompt for VS 2017' terminal. 

!!! Important
    Make sure you open the terminal as __Administrator__!

Navigate to the directory where you cloned carla and run the following (if you don't know how to use the "cd" command to navigate in a terminal, check out [this page](https://www.computerhope.com/issues/chusedos.htm) first):

    make PythonAPI

You can see what should happen below:
![alt text](gifs/makePythonAPI.gif "Making PythonAPI")

If everything was succesful the carla.egg file should be in __..\carla\PythonAPI\carla\dist__ :

![alt text](Images/eggfile.png "eggfile")

### Step 5, building and launching CARLA
Essentially the steps here are exactly the same as the PythonAPI build, however as a precaution it is a good idea to do the following:

![alt text](Images/genVis.png "genVisfiles")

!!! Note
    If you dont see this option of 'Generate Visual Studio Project Files', you probably have not selected the right engine version. Try and run the 'UnrealSelectEngine' version in: __C:\Program Files\Epic Games\UE_4.24\Engine\Binaries\Win64__
    If this program is not present it is possible it is located in: __C:\Program Files (x86)\Epic Games\Launcher\Engine\Binaries\Win64__. Just copy the 'UnrealSelectEngine' program to the first mentioned folder. It should now associate the engine with VS.

Now open a Terminal the same way as in step 4, go to the carla folder and run the following command:

    make launch

This will try and build carla, and eventually will launch the unreal editor. 


### Step 6, Unreal compiling

!!! Note
    The only important step here (if everything went well) is to remain patient, Unreal will have to compile all shaders which is CPU heavy and can take up to 2 hours.

### Step 7, adding vehicle assets to CARLA in Unreal
After the unreal editor has been launched and compiled the shaders from step 6 go to the content browser and search for __'vehicle factory'__:

![alt text](Images/vehfac.png "Vehicle Factory")

Open up this 'Blueprint' and then click on the array variable 'vehicles'. Now add to the array and select the vehicle blueprints you have selected. Give it a name you want to call it as from the pythonAPI, as a default use the ones shown here:

![alt text](Images/addvehicles.png "Adding Audi")

If all of the steps succeeded than congrats! You have successfully built CARLA, the basis of the JOAN simulator! Please proceed to the setting up of JOAN.

## Setting up JOAN
Please follow the following steps:

1. __Cloning JOAN__
1. __Setting up a Python Virtual Environment__
2. __Getting the python libraries__
3. __Run main.py__

### Cloning JOAN
Open a command window and navigate to the folder where you would like to clone the JOAN repository, remember that the clone command will create a new folder there to put the project in. 
Clone the repository with the following code:

    ## clone repo
    git clone https://gitlab.tudelft.nl/delft-haptics-lab/vrsim/SharedControlDrivingSim.git

### Setting up a Python Virtual Environment
We will now create a Python virtual environment, this will help keeping your JOAN project separated from your other projects. If you are interested and would like more information on virtual environments, please read [this](https://docs.python.org/3/tutorial/venv.html). But for now you can also just follow these steps.

To create the virtual environment, navigate to the JOAN project folder you've just cloned. Now type:

    python -m venv venv

This will create a folder called venv containing a new and clean virtual environment. To start working in this environment, we have to activate it first. To do this type:

    venv\Scripts\activate.bat 

If this succeeded, (venv) should have appeared in your command line trailing your current location. This indicates that the python command points to the virtual environment.
How to select this newly created virtual environment as the project interpreter in your IDE, depend on which IDE you are using. Pycharm should automatically detect the virtual environment and use it, for VS code please check [this link](https://stackoverflow.com/questions/54106071/how-to-setup-virtual-environment-for-python-in-vs-code). For other IDE's please use google.  

### Getting necessary python3 libraries
To get JOAN to work together with CARLA you will need several python packages (and if you want to use a sensodrive wheel with CAN interface also a specific DLL). The list of required pip installs is saved in the requirements.txt file.
To install all requirements from the command prompt, mak sure you are in the project folder and have the virtual environment activated. Now type: 

    pip install -r requirements.txt 

The only dependency not in the requirements.txt is the CARLA PythonAPI which we build earlier. To install this dependency navigate to your carla folder, to carla\PythonAPI\carla\dist. Make sure you still have the virtual environment activated. Now type:

    pip install  carla.whl
    
!!! Note
    Please note that the file name of the *.egg file might be slightly different in your case, it depends on the Python version.

## Running JOAN
Either open up the folder you cloned the repository in your preferred IDE and run via that or type in the following in the terminal from your cloned directory.
In both cases make sure you use the virtual environment as the python interpreter.

    python main.py

What should be happening is the following:

![alt text](gifs/JOAN.gif "Starting JOAN")