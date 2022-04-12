# Advanced - How to use JOAN
Here we will guide you through how the developers have thought up to use JOAN, this guide will consist of several different (not completely related) sections, therefore it might be easier to just scroll to the part you’re interested in and read up on it instead of going through from beginning to the end.

## Adding your own Modules

As we have explained earlier, JOAN consists of modules; basic building blocks that have their function in JOAN. The core idea of JOAN is that everyone can create and add their own modules.

A module typically consists of five classes: 

- a `module manager` class (essential)
- a `dialog` class (essential)
- a `shared variables` class
- a `process` class 
- a `settings` class 

Not for all modules, all classes are needed however every module will always need a `dialog` and a `module manager`.

The `dialog` is the graphical user interface of the module and takes all the credit for the rest of the class’s hard work. Here you can add your custom user interface file (`.ui`) such that you can control the module and more.

The `module manager` can be seen as a glorified accountant of the module, the manager keeps track of settings and shared variables, and will give the cue to start or stop the process.

The `settings` class holds all settable parameters of your module. Examples of such parameters are gains for controllers but also key mappings for hardware interfaces. These settings can be loaded and saved, but can also be stored and altered from experiment designs in the experiment manager.

The `shared variables` class holds all your variables, so this can contain information from your simulation, or the actual inputs from your hardware.

The `process` class will loop once JOAN is running, an important thing with the `process` class is that it inherits from 
`multiprocess.process`, meaning it is a multiprocess process. 



These classes in your new module inherit from an `manager` , `dialog`, `settings`, `sharedvariables` and `process` base class (if you're not sure what inheriting means, or you want to know more about it, check [this page](https://www.python-course.eu/python3_inheritance.php){target="_blank"} or [wikipedia](https://en.wikipedia.org/wiki/Inheritance_(object-oriented_programming) ){target="_blank"}). You can find these base classes in the `process` folder if you want to have a look. The base classes are designed to handle all basic functionality a module needs to function in Joan. 
By inheriting these base classes, you should be good to go for most applications. It is possible to override all methods but in most cases, it should not be necessary to do this to other methods than the examples in the `Template` module.  

!!! Important
    We set up the classes division with the dialog to keep functionality and UI separately. Please stick to this division. Do not do any calculations or other operations in the dialog that are not necessary there. Only use the dialog to connect to functions in the process class (like starting and stopping the module).

Of course, you can change the modules that come shipped with JOAN to your liking, but perhaps you want to build your own module. Go nuts! We will briefly explain how you can make your own module and include it. 

!!! Important
    We included a template module that you can use to create your own modules. Check it out and see if you understand it, this is a very important step since we will not go into all the nitty-gritty detail of the code down below. Rather make sure you have the template module next to this as you read it, read the comments in there, and make sure you understand what is going on! This will make your life of adding a module significantly easier!

## Creating your own module

Creating your module consists of the following steps:

1. Copy the template and rename the module
2. Add the new module to `JOANModules.py`
3. Add the module to `JOANHQ`
4. Add all the functionality to your freshly made module

We will create a module called `joaniscool` which prints "JOAN is the best" every time step to illustrate this process. Of course, use your module name. 

The name of your module is very important. Other programmers should immediately understand what your module is meant to do, so the name shouldn't be too generic. Abbreviations also tend to make reading difficult, so please avoid them too. 

Changing the name of your module once it is up and running can be very hard since other people might rely on 
the old name in their code. If you want to know more about naming modules, functions, and variables in code, we 
recommend chapter 2 of the book "clean code" by Robert C. Martin.

__Examples of bad names__

- controller - too generic
- htcfdbcnt - abbreviations are unreadable and unclear
- olgershapticfeedbackcontrollerforpedals - too long

__Example of a good name__

- hapticpedalcontroller
   
### 1. Copy the template and rename the module

Copy the `template` folder in the modules folder.

- Rename the folder to your desired module name. Note, a module name should always be completely lowercase without any special characters 
(i.e. don't use a \_ or \-). Hence, we rename `template` to `joaniscool`

!!! Tip
    PyCharm has a build-in renaming functionality that automatically renames all occurrences in your project. You can use it by selecting a variable, class, or method and pressing `shift + F6`, you can also rename files this way by right-clicking and going to the `refactor` tab.

An example, if you are using PyCharm:

- In your new `joaniscool` folder open `template_manager.py`. Put your cursor on TemplateManager (behind class) and press `shift+F6`. Now rename this class to JoanIsCoolManager, make sure the checkbox `rename containing file` is checked, and click refactor.  

If not, you'll have to do it manually. Note that you'll have to do this for all classes and files that you copied from the template.

### 2. Add the new module to JOANModules.py

This one is a lot of work, but be precise! One little forgotten comma will render everything unfunctional. In the `modules` folder, you can find a file named `joanmodules.py`. This contains an `Enum` class which holds all available modules. 
This class serves multiple purposes. It serves as a unique key to reference a certain module in `dict`s and it provides access to a module's classes.
This `Enum` also allows for easy iteration over all available JOAN  modules. Once you add your module here, it can be found by JOAN and it can be added to the main menu.

Make sure to provide links of your modules to the corresponding classes in the Enums property functions. 
Please also add your module to the \_\_\_str\_\_\_ function. This will return the string representation of your module,
i.e. the name of your module for titles and save files.

- open the file `joanmodules.py` in the `modules` folder
- add your new module to everything. Copy every line with 'template' in it, paste it on the next line, and replace every 'template' in that new line with your module name
- check, double-check and triple-check if you copied every line with ‘template’ in it.

### 3. Add the module to JOANHQ
This step is easy! Add your new module to JOANHQ in `main.py`, this instantiates your module:

    JOANHQACTION.add_module(JOANMODULES.JOANISCOOL, time_step_in_ms=200)

Note that the parameter `time_step_in_ms=200` sets the timer interval in milliseconds.

Run JOAN; if everything works (you'll see error tracebacks in the terminal if it does not), you will see your own module in the JOANHQ module list!

!!! Note
    Make sure to commit and push your changes every once in a while, especially after you copied the template module, renamed it, and added it to JOANHQ. This way you have a point in time in which your module is clean. 

### 4. Start coding in your module

 Now you can start adding your own code. For our example, for instance, we would add a line with 

```python
print("JOAN is the best")
```

in the `do_while_running` function of your JoanIsCoolProcess class. Once you transition to the running state from headquarters, it will start printing this message at a frequency of 5 Hz.

What follows is a summary of what happens in what class. Also, have a look at the comments in the Template module, they also indicate what to do where.

!!! Important
    These little sections should be seen as summaries and as a means to find the appropriate references, not as a full-fledged explanation of the classes. For 
    full understanding please also take a look at the several links included in these sections.

#### <a name="manager_class"></a>4.1 The Manager class

As mentioned earlier `Manager` class acts as a kind of bookkeeping mechanism for the module, its main purpose is to keep track of what classes should be created
and deleted. Furthermore the module's `Statemachine` is included in the module manager, which means you can set your state transition conditions for that particular
module in here, as well as link state-change handling to a particular function. More info about the workings of the state machine can be found in the [state machine documentation](advanced-state-machine.md)
One last thing that is important to mention regarding the `Manager` class is that has access to the `News`, which means that via the manager you can also
access other modules `Shared Variables` if they are available.

#### <a name="dialog_class"></a>4.2 The Dialog class

The only purpose of the dialog class is to display the state of your module and to let the user make changes to it. No calculations should be done here
. Other than this disclaimer; there is no recipe for what you should do here and how you should do it since all modules and their widgets differ too much. If you want to see some examples, just browse the existing modules.
 
 Please note that the definition of the Qt objects should be done in the `*.ui` file. To view and alter these files you'll need a program called Qt creator, you
  can download it [here](https://www.qt.io/offline-installers){target="_blank"} (click Qt creator on the left). The `*.ui` file that is linked to, from the JoanModules enum is
   automatically loaded in the dialog.
   
#### <a name="settings_class"></a>4.3 The Settings class

All attributes of the settings class can be saved or loaded from and to JSON files. This is not only used to save and load settings for your module, but also
 by the experiment manager to save and load sets of options for all modules. You can save and load settings by respectively calling the `save_to_file` and
  `load_from_file` methods. When you add an attribute to your settings class (this may be a base type or a custom class object), it will be saved and
   restored automatically. Loaded JSON files containing a subset of the attributes of the settings class will only alter those attributes and will not change
    other options. 
    
When adding attributes to your settings class, think about what should be a setting. Constants (like hard maximum limits for gains), will never change and
 should therefore not be stored in settings. But variables that do change a lot (like an object representing the connection to a piece of hardware or a
  trial ID number), should also not be stored in settings. A good rule of thumb is that an attribute of settings should not change on every boot of JOAN, but
   should vary between users and or experimental setups.
  
  In the example of the hardware connection; an address or id number for the piece of hardware which uniquely defines the connection object would be
   a good setting to save. This will not change on every startup but will vary between users. From this setting, the connection object can be reconstructed
    on every boot.

#### <a name="shared_variables_class"></a>4.4 The Shared Variables Class

 The class itself is just a collection of getters and setters of the particular variables that have been defined. If you want to use a variable you'll need to define a getter and setter here, another thing about the shared variables is that we convert them to `c-types`, this is needed because 
if you do not use `serializable` or `pickleable` variables you will not be able to share them over multiple processes. You can find more on 
`Python object serialization` [here](https://docs.python.org/3/library/pickle.html?highlight=pickle#module-pickle){target="_blank"}. The last thing we'd
like to say about the Shared Variable class is quite essential:

Whenever you want to do something with a Shared Variable value in a module do the following:

1. First create a copy of the variable to a newly defined variable:
   
        my_new_variable = self.shared_variables.my_variable
   
2. Then do whatever you want to calculate with this newly created `my_new_variable` for example:
        
        my_new_variable = (my_new_variable * my_new_variable) * 2
        
   
3. As a last step (if you've changed something to the variable) set the actual shared variable again so:
   
        self.shared_variables.my_variable = my_new_variable

!!! Important
    The above is very important because this makes sure we only get and set the actual shared variable once. If we keep using the actual shared variable
    this means we have to access this variable every single time, and whenever you access this variable it gets `locked` for a tiny amount of time.
    This usually isn’t a problem but if we start doing this every loop and a lot of times per loop, we could get into trouble due to the variable 
    being locked. On top of that, it could happen that somewhere else a module needs the same variable, and we cannot guarantee that it is not one of the
    intermediate value assignments that are being used there. If we just set and get it once, it is either the value at the beginning of the loop or the one 
    in the end, this makes things a lot easier to grasp.

#### <a name="process_class"></a>4.5 The Process class

The last thing that 'almost' every module contains is a Process Class, it says 'almost' because a separate process is not always necessary, for example
the `DataPloter` module does not run its own process. However, a Process class is nearly a must when you want to do some (heavy) computational stuff for example making 
a model predictive controller. You might ask why this should be run in its own process, the main advantage is that we can run our modules in parallel rather than sequentially.
Just to be a bit more clear let’s think of an example, you might have 3 modules running; `Hardware Manager`, `Haptic Controller Manager`, and `Carla Interface`. 
Imagine that you have made a beautiful controller that does some heavy calculations but outputs the best haptic feedback you could think of. If JOAN
runs sequentially this means the following could happen:

1. You get your car data from CARLA
2. You calculate your epic torque that goes to the hardware
3. You set the torque.

Now imagine that step 2 here takes about 500ms, this will hold up the rest of the program, worst-case scenario: the Hardware shuts off because it didn’t
get a message in time, meaning the watchdog turned on.

Our solution to this problem is `Multiprocesses` meaning we run all the above steps in parallel! For more information about multiprocessing
please consult the very extensive and elaborate documentation [here](https://docs.python.org/3/library/multiprocessing.html){target="_blank"}
