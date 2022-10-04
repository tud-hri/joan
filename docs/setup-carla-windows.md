# Setting up CARLA for Windows
!!! Note
    If you are a TU Delft student, and are using one of the TUD computers with CARLA installed, you can skip these instructions. 
    Go to the [setup guide for installing on TUD shared hardware](setup-on-tud-shared-hardware.md).
    
First, to install JOAN on Windows, Carla must be installed. This installation procedure is fully explained in the documentation [to build CARLA 0.9.13 for windows](https://carla.readthedocs.io/en/0.9.13/build_windows/){target="_blank"} (the last version we tested JOAN with).
Below, some additional notes on the installation of Carla 0.9.13 are provided to help in the installation process. 
Make sure you have completed all the steps in the installation before moving on to the installation of JOAN!

!!! Note 
    It may also be a good idea to read some of the additional documentation of [CARLA 0.9.13](https://carla.readthedocs.io/en/0.9.13/){target="_blank"}. 



---

## Additional Notes

First of all, this installation is a game of patience. Assume that installing everything may take 1 full workday so make sure to provide yourself with some snacks and make sure you sit comfortable since this will take a while!

# Carla version while cloning
When you get to the step where you clone the `carla` git repository, make sure you clone the correct version (0.9.13) by using the following command:

```git clone -b 0.9.13```

The `-b 0.9.13` part ensures you clone the branch 0.9.13.

# Error while building the Carla Python API Client

(Tested in June 2022) When trying to run:
```commandline
make PythonAPI
``` 
and the following error occurs:

```commandline
-[Setup]: Installing zlib...
    -[install_zlib]: [Batch params]: --build-dir "C:\carla\Build\"
    -[install_zlib]: Retrieving zlib.
Exception calling "DownloadFile" with "2" argument(s): "The remote server returned an error: (404) Not Found."
At line:1 char:1
+ (New-Object System.Net.WebClient).DownloadFile('http://www.zlib.net/z ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [], MethodInvocationException
    + FullyQualifiedErrorId : WebException

    -[install_zlib]: Extracting zlib from "zlib-1.2.11.zip".
Expand-Archive : The path 'C:\carla\Build\zlib-1.2.11.zip' either does not exist or is not a valid file system path.
At line:1 char:1
+ Expand-Archive 'C:\carla\Build\zlib-1.2.11.zip' -DestinationPath 'C:\ ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidArgument: (C:\carla\Build\zlib-1.2.11.zip:String) [Expand-Archive], InvalidOperat
   ionException
    + FullyQualifiedErrorId : ArchiveCmdletPathNotFound,Expand-Archive

    -[install_zlib]: Removing "zlib-1.2.11.zip"
Could Not Find C:\carla\Build\zlib-1.2.11.zip
The system cannot find the file specified.
    -[install_zlib]: Creating "C:\carla\Build\zlib-source\build"
CMake Error: The source directory "C:/carla/Build/zlib-source" does not appear to contain CMakeLists.txt.
Specify --help for usage, or press the help button on the CMake GUI.

    -[install_zlib]: [CMAKE ERROR] An error ocurred while executing cmake command.
    -[install_zlib]: [CMAKE ERROR] Possible causes:
    -[install_zlib]:                - Make sure "CMake" is installed.
    -[install_zlib]:                - Make sure it is available on your Windows "path".
    -[install_zlib]:                - Make sure you have cmake 3.12.4 or higher installed.
    -[install_zlib]: Exiting with error...
```
 
This can be bypassed by altering one line in the file `<CARLA_ROOT_FOLDER>\Util\InstallersWin\install-zlib.bat` (where `<CARLA_ROOT_FOLDER>` is the location where you installed Carla). Change `set ZLIB_VERSION=1.2.11` on line 51 to `set ZLIB_VERSION=1.2.12`. Afterwards, delete the folder `<CARLA_ROOT_FOLDER>\Build`.  This should solve the [issue](https://github.com/carla-simulator/carla/issues/5304){target="_blank"}.

# Installing Carla's Python API

When you get the choice to install the Python IPA using the `*.egg` or `*.whl` file, use the `*.whl` file as the `egg` will not be found automatically by JOAN.
