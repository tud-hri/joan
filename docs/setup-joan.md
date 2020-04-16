# Setting up JOAN
Please follow the following steps:

1. __Cloning JOAN__
1. __Setting up a Python Virtual Environment__
2. __Getting the python libraries__
3. __Run main.py__

## Cloning JOAN
Open a command window and navigate to the folder where you would like to clone the JOAN repository, remember that the clone command will create a new folder there to put the project in. 
Clone the repository with the following code:

    ## clone repo
    git clone https://gitlab.tudelft.nl/delft-haptics-lab/vrsim/SharedControlDrivingSim.git

---
## Setting up a Python Virtual Environment
We will now create a Python virtual environment, this will help keeping your JOAN project separated from your other projects. If you are interested and would like more information on virtual environments, please read [this](https://docs.python.org/3/tutorial/venv.html). But for now you can also just follow these steps.

To create the virtual environment, navigate to the JOAN project folder you've just cloned. Now type:

    python -m venv venv

This will create a folder called `venv` containing a new and clean virtual environment. To start working in this environment, we have to activate it first. To do this type:

    venv\Scripts\activate.bat 

If this succeeded, (`venv`) should have appeared in your command line trailing your current location. This indicates that the python command points to the virtual environment.
How to select this newly created virtual environment as the project interpreter in your IDE, depend on which IDE you are using. PyCharm should automatically detect the virtual environment and use it, for VS Code please check [this link](https://stackoverflow.com/questions/54106071/how-to-setup-virtual-environment-for-python-in-vs-code). For other IDE's please use the internet.  

---
## Getting necessary python3 libraries
To get JOAN to work together with CARLA you will need several python packages (and if you want to use a SensoDrive steering wheel with CAN interface also a specific DLL). The list of required pip installs is saved in the requirements.txt file.
To install all requirements from the command prompt, make sure you are in the project folder and have the virtual environment activated. Now type: 

    pip install -r requirements.txt 

The only dependency not in the requirements.txt is the CARLA PythonAPI which we build earlier. To install this dependency navigate to your CARLA folder, to `carla\PythonAPI\carla\dist`. Make sure you still have the virtual environment activated. Now type:

    pip install  carla.whl
    
!!! Note
    Please note that the file name of the `*.egg` file might be slightly different in your case, it depends on the Python version.

---
## Running JOAN
Either open up the folder you cloned the repository in your preferred IDE and run via that or type in the following in the terminal from your cloned directory.
In both cases make sure you use the virtual environment as the python interpreter.

    python main.py

What should be happening is the following:

![alt text](gifs/JOAN.gif "Starting JOAN")