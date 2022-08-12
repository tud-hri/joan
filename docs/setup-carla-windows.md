# Setting up CARLA for Windows

!!! Note 
    Make sure to use [the windows build version CARLA 0.9.13](https://carla.readthedocs.io/en/0.9.13/build_windows){target="_blank"}. 
    
First, to install JOAN on Windows, Carla must be installed. This installation procedure is fully explained in the documentation [to build CARLA 0.9.13 for windows](https://carla.readthedocs.io/en/0.9.13/build_windows/){target="_blank"} (the last version we tested JOAN with).
Below, some additional notes on the installation of Carla 0.9.13 are provided to help in the installation process. 
Make sure you have completed all the steps in the installation before moving on to the installation of JOAN!
!!! Note 
    It may also be a good idea to read some of the additional documentation of [CARLA 0.9.13](https://carla.readthedocs.io/en/0.9.13/){target="_blank"}. 



---

## Additional Notes

First of all, this installation is a game of patience. Assume that installing everything may take 1 full workday so make sure to provide yourself with some snacks and make sure you sit comfortable since this will take a while!


# 1. Compile the Python API Client
!!! Note 
    (Tested in June 2022) When trying to run:
    ```commandline
    make PythonAPI
    ``` 
    an error occurs. This can be bypassed by searching in the file `<CARLA_ROOT_FOLDER>\Util\InstallersWin\install-zib.bat` (where `<CARLA_ROOT_FOLDER>` is the location where you installed Carla) for `zlib-1.2.11.zip`. Replace this by `zlib-1.2.12.zip` and this should solve the [issue](https://github.com/carla-simulator/carla/issues/5304){target="_blank"}.

To install Carla, please make sure to use the `.whl` file (since the JOAN code assumes you do). This file is built after running the `make PythonAPI` command is successfully executed. 
As the Carla documentation describes, make sure to locate this `.whl` file. and then install carla using:
```commandline
pip install <path/to/wheel>.whl
``` 

One error that may occur during compilation of you map