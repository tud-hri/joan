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

Using PyCharm, open the terminal again (in PyCharm), check if the directory is still correct (of your repository) and type:

    python -m venv venv

!!! Note
    If you don't use PyCharm, just use any other terminal to do these steps.

This will create a folder called `venv` containing a new and clean virtual environment. To start working in this environment, we have to activate it first. To do this type:

    venv\Scripts\activate

If this succeeded, (`venv`) should have appeared in your command line trailing your current location. This indicates that the python command points to the virtual environment. 

If you are using PyCharm, you might need to add your freshly created virtual environment as a Python interpreter. Click on the interpreter widget (it should say something with interpreter) and click `Add interpreter`. It should automatically select the `venv` Python interpreter. Confirm everything and wait for a bit. PyCharm needs some time to set everything up.

---
## Getting necessary python3 libraries
To get JOAN to work together with CARLA you will need several python packages (and if you want to use a SensoDrive steering wheel with CAN interface also a specific DLL). The list of required pip installs is saved in the requirements.txt file.
To install all requirements from the command prompt, make sure you are in the project folder and have the virtual environment activated. Now type: 

    pip install -r requirements.txt 

The only dependency not in the requirements.txt is the CARLA PythonAPI which we build earlier. To use this dependency copy the `*.egg` file to the empty folder `carla_pythonapi` in your JOAN project folder. If you have not done this step you will get an error message whenever you start JOAN.
    
!!! Note
    Please note that the file name of the `*.egg` file might be slightly different in your case, it depends on the Python version. Make sure that the filename in `carlainterfaceaction.py` matches the name of your own `*.egg` file. 

---
## Running JOAN

### Using PyCharm
Once you've selected the correct Python interpreter (in our case `venv`), you can run JOAN by either clicking `Run` and `Run 'main'` or right-click on `main.py` and select `Run 'main'`.

![pycharm-run-main](gifs/pycharm-run-main.gif)

### Using VS Code
Visual Studio Code will ask you which Python interpreter you want to use. Make sure to use the `venv` virtual environment you just created. Open the `main.py` file and run it (green triangle in the top-right corner).

![vscode-run-main](gifs/vscode-run-joan.gif)

### Using any other terminal
Navigate to your repository folder. Make sure the `venv` environment is activated as your Python interpreter.

    python main.py

What should be happening is the following:

![alt text](gifs/JOAN.gif "Starting JOAN")

!!! Warning
    Doesn't work? Hmm, are you sure you followed all the steps? Please double-check. Else, check with a fellow student who got it up and running, or talk to your supervisor.