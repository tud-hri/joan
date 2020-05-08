# How to use JOAN
Here we will guide you through how the developers have thought up to use JOAN, this guide will consist of several different not completely related sections therefore it might be easier to just scroll to the part your interested in and read up on it instead of going through from beginning to the end.

## Adding your own Modules

As we have explained earlier, JOAN consists of modules, basically building blocks that have their own function in JOAN. The core idea of JOAN is that everyone can create and add their own modules.

A module consists of two classes: 

- an `action` class and
- an `dialog` class

The `action` class takes care of most of the module's functionality in the background, it does all the hard work. It executes the `do` function every timer time step, it handles any JOAN state changes and communicates with other modules through JOAN `News` channels. 

The `dialog` is the graphical user interface of the module and takes all the credit for the `action`'s hard work. Here you can add your custom user interface file (`.ui`) such that you can control the module and more.

!!! Important
    We set up the action and dialog division to keep functionality and UI separately. Please stick to this division. Do not do any calculations or other operations in the dialog that are not necessary there. Only use the dialog to connect to functions in the action class (like starting and stopping the module).

Of course you can change the modules that come shipped with JOAN to your liking, but perhaps you want to build your own module, for example to plot data in real-time. Go nuts! We will briefly explain how you can make your own module and include it. 

!!! Important
    We included a template module that you can use to create your own modules. Check it out and see if you understand it.

### Creating your own module

Creating your module consists of the following steps:

1. Copy the template and rename the module
2. Add the new module to `JOANModules.py`
3. Add the module to `JOANHQ`
4. Add all the functionality to your freshly made module

We will create a module called `joaniscool` which prints "JOAN is the best" every time step to illustrate this process. Of course, use your own module name. 

The name of your module is very important. Other programmers should immediately understand what your module is meant to do, so the name shouldn't be too generic. Abbreviations also tend to make reading difficult, so please avoid them too. 

Changing the name of your module once it is up and running can be very hard, since other people might rely on 
the old name in their code. If you want to know more about naming modules, functions and variables in code, we would
like to recommend chapter 2 of the book "clean code" by Robert C. Martin.

__Examples of bad names__

- controller - too generic
- htcfdbcnt - abbreviations are unreadable and unclear
- olgershapticfeedbackcontrollerforpedals - too long

__Example of a good name__

- hapticpedalcontroller
   
#### 1. Copy the template and rename the module

Copy the `template` folder in the modules folder.

- Rename the folder to your desired module name. Note, a module name should always be completely lowercase without any special characters 
(i.e. don't use a \_ or \-). Hence, we rename `template` to `joaniscool`
- go into your folder, go to the `action` folder, and rename `templateaction.py` to `joaniscoolaction.py`
- open `joaniscoolaction.py` and replace all 'Template' with 'JoanIsCool' (note, this is camelCase; words are capitalized in class names). You can use a replace function in PyCharm, but make sure to check that the case is matched. 
- do the same for 'TEMPLATE', replace it with your _capitalized_ module name.
- open the file `states.py` and perform the same two steps.
- now, go into the `dialog` folder, and rename `templatedialog.py` to `joaniscooldialog.py` and `templatewidget.ui` to `joaniscoolwidget.ui`. 
- open `joaniscooldialog.py` and replace all 'Template' and 'TEMPLATE', as we did in its `action` partner.

#### 2. Add the new module to JOANModules.py

This one is a lot of work, but be precise! One little forgotten comma will render everything unfunctional. In the `modules` folder you can find a file named `joanmodules.py`. This contains an `Enum` class which holds all available modules. This class servers multiple purposes. It serves a a unique key to reference a certain module in `dict`s. And it provides access to a module's `dialog` and `action` classes. This `Enum` also allows for easy iteration over all available JOAN  modules. Once you add your module here, it can be found by JOAN and it can be added to the main menu.

Make sure to provide links to the modules action and widget classes in the Enums action and widget property functions. 
Please also add your module to the \_\_\_str\_\_\_ function. This will return the string representation of your module,
i.e. the name of your module for titles and save files.

- open the file `joanmodules.py` in the `modules` folder
- add your new module to everything. Basically, copy every line with 'template' in it, paste it on the next line, and replace every 'template' in that new line with your module name
- check, double check and triple check if you copied every line with template in it.

#### 3. Add the module to JOANHQ
This step is easy! Add your new module to JOANHQ in `main.py`, this instantiates your module:

    JOANHQACTION.add_module(JOANMODULES.JOANISCOOL, millis=200)

Note that the parameter `millis=200` sets the timer interval in milliseconds.

Run JOAN; if everything works (you'll see error tracebacks in the terminal if it does not), you will see your own module in the JOANHQ module list!

!!! Note
    Make sure to commit and push your changes every once in a while, especially after you copied the template module, renamed it, and added it to JOANHQ. This way you have a point in time in which your module is clean. 

#### 4. Start coding in your module

 Now you can start adding your own code. For our example, for instance, we would add a line with 

```python
print("JOAN is the best")
```

in the `do` function. Once you hit the start button of the JOANISCOOL module, it will start printing this message at a frequency of 5 Hz.


## Workflow
In this section an overview of the workflow of JOAN is presented. 

!!! Note
    This document will only contain a workflow of the essential bare-bone modules (Carlainterface, Hardwaremanager) to drive a car around. This flow might change depending on your own implemented modules.

The workflow will be explained in several steps:

1. __Add modules in main.py__
2. __Start CARLA in unreal__
3. __Run Main__
4. __Setup Hardwaremanager__
5. __Run Hardwaremanager__
6. __Setup CarlaInterface__
7. __Run Carlainterface__
8. __Drive!__

### Step 1. Adding the modules in main.py
This step is easy, just add the following piece of code to the main.py file (or uncomment them):

    JOANHQACTION.add_module(JOANModules.CARLA_INTERFACE, millis=50)
    JOANHQACTION.add_module(JOANModules.HARDWARE_MANAGER, millis=5)

### Step 2. Start CARLA in unreal.
To do this select the map you'd like to drive in, the CARLA default map is town03. However (for now) the JOAN default map is 'Debugmap'. Starting the level is easy just press the play button on the top bar see the figure below:

![Carla Start](imgs/Carla_Default.png)

Make sure you also have 'vehicle spawnpoints' in your level. You can check this by checking out the world content manager in the topright corner. Another note about these spawnpoints is that you should place them above the ground a bit (in this example it is 75cm, cm is the default unit in unreal) so you wont have a collision at spawning.

### Step 3. Run Main
This is the exact same step as described in __[Setup and run your JOAN project](setup-run-joan.md)__ at 'Running JOAN'.

### Step 4. Setup Hardwaremanager
To do this in the JOAN main menu show the 'Hardwaremanager' module. Now click the 'add new hardware button', this will open a selection menu in which you can choose what sort of input you'd like to add. For now only Keyboard and Joystick work. In this guide we will add a keyboard input. 
So select keyboard, which will open a settings section of the keyboard. Default keys are:

* W = Throttle
* S = Brake
* A = Steer Left
* D = Steer Right
* R = Toggle Reverse
* K = Handbrake

The other settings pertain to whether the steering wheel will autocenter and how fast it does this. The sensitivities of braking and throttle can also be adjusted but we'll leave them as it is for now. These steps will look like this:


A flow-diagram is also available at the end of this page.


## Workflow flow diagram
![workflow](imgs/JOAN_Workflow.png)
