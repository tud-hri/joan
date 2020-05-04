# Adding your own Modules
All JOAN modules consist of an action and a widget part. The widget manages all UI interaction while the action is the 
backend. When you are creating a new JOAN module, please adhere to this structure. Please read all instructions below
before starting on your own module.

## Setting up the bare basics
The first step is creating a folder under modules. This folder should have the same name as your module and contain an
action and widget folder. A module name should always be completely lowercase without any special characters 
(i.e. don't use a \_ or \-) 

The name of your module is very important. Other programmers should immediately understand
what your module is meant to do, so the name shouldn't be to generic. But long names are hard to read and make importing
the right class difficult, so your name shouldn't be to long either (please note that this does not hold for variable 
names). Abbreviations also tend to make reading difficult, so please avoid them to. 

Changing the name of your module once it is up and running can be very hard, since other people might rely on 
the old name in their code. If you want to know more about naming modules, functions and variables in code, we would
like to recommend chapter 2 of the book "clean code" by Robert C. Martin.

#### Examples of bad names
* controller - to generic
* htcfdbcnt - abbreviations are unreadable and unclear
* olgershapticfeedbackcontrollerforpedels - to long 

    
#### Example of a good name
* hapticpedalcontroller
  
## Adding your module to the modules enum
In the modules folder you can find a file named joanmodules.py. This contains an Enum class which holds all available 
modules. This class servers multiple purposes. It serves a a unique key to reference a certain module in dicts. And it 
provides access to a modules widget and action class. This Enum also allows for easy iteration over all available JOAN 
modules. Once you add your module here, it can be found by JOAN and it can be added to the main menu.

Make sure to provide links to the modules action and widget classes in the Enums action and widget property functions. 
Please also add your module to the \_\_\_str\_\_\_ function. This will return the string representation of your module,
i.e. the name of your module for titles and save files.    
   