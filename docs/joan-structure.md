## Structure of main JOAN components

JOAN components are used in modules that you can add.

They are loaded through the Main window as they are defined in `JOANModules.py`.

Your modules, which should consist of an action- and a dialog-part inherit JOAN components to make building and using modules easier for you.

Using the `JOANModuleAction` let your module work with:

- `Status`, containing the State and the StateMachine
- `News`, your module may write to it's own news-channel using a time interval
- `Settings`, containing settings in json format
- `performance monitor` (optional) on the current module

Using the `JOANModuleDialog` gives your module a base dialog window with buttons (see picture below):

- `Start`
- `Stop`
- `Initialize`

And a menu bar with the options:

- `File`
- `Settings`

It also has an input field for setting a timer interval used when writing news (= latest data).

![alt text](imgs/joan-structure-template-dialog.png "Template Dialog")


## Main Components of JOAN
This schematic shows the overall structure of JOAN as it is at the moment of writing (11/08/2020):

!!! Note
    JOAN will work with only 1 module as well or as many as you like. The structure shown here is a 'barebones' version of driving
    a car around and recording some data. 
    

![alt text](imgs/joan-structure-schematic.png "Modules Schematic")

As shown in the figure the main modules you'll probably always use are 'carlainterface', 'hardwaremanager' and the 'datarecorder'. 
These module titles sort of giveaway what they do however I will also attempt to give a short explanation of each of these modules, why they are there
and what they accomplish. 

!!! Note
    This explanation will only scratch the surface of how exactly these modules work, we have tried to document the code itself really well
    so if you want to know the knitty gritty of what exactly happens in the modules please have a look at the individual code and especially
    the docstrings/comments! :)
    
