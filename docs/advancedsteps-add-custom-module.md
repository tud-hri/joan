# How to use JOAN
Here we will guide you through how the developers have thought up to use JOAN, this guide will consist of several different not completely related sections therefore it might be easier to just scroll to the part your interested in and read up on it instead of going through from beginning to the end.

## Adding your own Modules

As we have explained earlier, JOAN consists of modules, basically building blocks that have their own function in JOAN. The core idea of JOAN is that everyone can create and add their own modules.

A module consists of two or three classes: 

- an `action` class
- a `dialog` class
- optionally, a `settings` class

The `action` class takes care of most of the module's functionality in the background, it does all the hard work. It executes the `do` function every timer time step, it handles any JOAN state changes and communicates with other modules through JOAN `News` channels. 

The `dialog` is the graphical user interface of the module and takes all the credit for the `action`'s hard work. Here you can add your custom user interface file (`.ui`) such that you can control the module and more.

The `settings` class is optional, and holds all settable parameters of your module. Examples of such parameters are gains for controllers but also key mappings for hardware interfaces. These settings can be loaded and saved, but can also be stored and altered from experiment designs in the experiment manager.

These classes in your new module inherit from an `action`, `dialog` and `settings` base class (if you're not sure what inheriting means, or you want to know more about it, check [this page](https://www.python-course.eu/python3_inheritance.php){target="_blank"} or [wikipedia](https://en.wikipedia.org/wiki/Inheritance_(object-oriented_programming) ){target="_blank"}). You can find these base classes in the `process` folder, if you want to have a look. The base classes are designed to handle all basic functionality a module needs to function in Joan. 
By inheriting these base classes, you should be good to go for most applications. It is possible to override all methods but in most cases it should not be necessary to do this to other methods than the examples in the `Template` module.  

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

!!! Tip
    PyCharm has a build in renaming functionality that automatically renames all occurrences in your project. You can use it by selecting a variable, class or method and pressing `shift + F6`.

So, if you are using PyCharm:

- In your new `joaniscool` folder open `action` and then open the file `templateaction.py`. Put your cursor on TemplateAction (behind class) and press `shift+F6`. Now rename this class to JoanIsCoolAction, make sure the checkbox `rename containing file` is checked, and click refactor.  
- Open `states.py` and use `shift+F6` to rename the class `TemplateStates` to `JoanIsCoolStates` and the variable `TEMPLATE` to `JOAN_IS_COOL`. (Notice that with the last oke, you've changed the whole list of variables at once. How cool is that!)
- Open  `templatedialog.py` in `joaniscool\dialog` and use `shift+F6` to rename the class `TemplateDialog` to `JoanIsCoolDialog`
- Finally rename the file `templatewidget.ui` to `joaniscoolwidget.ui`, if you do this using PyCharm please deselect the checkbox `search for references`. PyCharm can not distinguish between this file and the original `templatewidget.ui` because it is referenced to from strings, so it will mess up the old references.

If not, you'll have to do it manually: 

- go into your folder, go to the `action` folder, and rename `templateaction.py` to `joaniscoolaction.py`
- open `joaniscoolaction.py` and replace all 'Template' with 'JoanIsCool' (note, this is camelCase; words are capitalized in class names). You can use a replace function in PyCharm, but make sure to check that the case is matched. 
- do the same for 'TEMPLATE', replace it with your _capitalized_ module name.
- open the file `states.py` and perform the same two steps.
- now, go into the `dialog` folder, and rename `templatedialog.py` to `joaniscooldialog.py` and `templatewidget.ui` to `joaniscoolwidget.ui`. If you do this using PyCharm please deselect the checkbox `search for references`. PyCharm can not distinguish between this file and the original `templatewidget.ui` because it is referenced to from strings, so it will mess up the old references.
- open `joaniscooldialog.py` and replace all 'Template' and 'TEMPLATE', as we did in its `action` partner.

#### 2. Add the new module to JOANModules.py

This one is a lot of work, but be precise! One little forgotten comma will render everything unfunctional. In the `modules` folder you can find a file named `joanmodules.py`. This contains an `Enum` class which holds all available modules. This class serves multiple purposes. It serves a a unique key to reference a certain module in `dict`s. And it provides access to a module's `dialog` and `action` classes. This `Enum` also allows for easy iteration over all available JOAN  modules. Once you add your module here, it can be found by JOAN and it can be added to the main menu.

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

in the `do` function of your JoanIsCoolAction class. Once you hit the start button of the JoanIsCool module, it will start printing this message at a frequency of 5 Hz.

What follows is a summary on what you should do in which class. Also have a look at the comments in the Template module, they also indicate what to do where.

#### 4.1 the action class

All calculations for your module should be done in the action class. The action class has 4 methods you should override. As explained above, the `do` method is 
called every time step and is the place to do you main calculations. The `initialze` method is called once when the method transitions to the initialized state. 
This is the place to do calculations that are only needed before starting the module. Like copying settings or opening a new file to write data to. The `start`
 and `stop` methods start and stop the loops. If you want to override them (to do something just before you start or just before you stop) please make sure
  to call the super method when you're done. This is what actually starts and stops the timers.

#### 4.2 the dialog class

The only purpose of the dialog class is to display the state of your module, and to let the user make changes to it. No calculations should be done here
. Other than this disclaimer; there is no recipe for what you should do here and how you should do it since all modules and their widgets differ too much. If
 you want to see some examples, just browse the existing modules.
 
 Please note that the definition of the Qt objects should be done in the `*.ui` file. To view and alter these files you'll need a program called Qt creator, you
  can download it [here](https://www.qt.io/offline-installers) (click Qt creator on the left). The `*.ui` file that is linked to, from the JoanModules enum is
   automatically loaded in the dialog.
   
#### 4.3 the settings class

All attributes of the settings class can be saved or loaded from and to JSON files. This is not only used to save and load settings for your module, but also
 by the experiment manager to save and load sets of options for all modules. You can save and load settings by respectively calling the `save_to_file` and
  `load_from_file` methods. When you add an attribute to your settings class (this may be a base type or a custom class object), it will be saved and
   restored automatically. Loaded JSON files containing a subset of the attributes of the settings class will only alter those attributes and will not change
    other options. 
    
When adding attributes to your settings class, think about what should be a setting. Constants (like hard maximum limits for gains), will never change and
 should therefore not be stored in settings. But variables that do change a lot (like an object representing the connection to a piece of hardware or a
  trial ID number), should also not be stored in settings. A good rule of thumb is that an attribute of settings should not change on every boot of joan, but
   should vary between users and or experimental setups.
  
  In the example of the hardware connection; an address or id number for the piece of hardware which uniquely defines the connection object would be
   a good setting to save. This will not change on every startup but will vary between users. From this setting, the connection object can be reconstructed
    on every boot.
