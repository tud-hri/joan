# JOAN settings

## Default settings

!!! Important
Default settings will save you a lot of clicking

You can save your default JOAN setup per module as follows. Configure each module as you prefer (e.g. add and configure input devices, agents, etc). Then, click the Settings menu in the module, followed by 'Save settings'. In the save dialog, nam your settings `default_settings`. Next time you start JOAN, each module will try to load the default settings, if they are present.

## How to work with settings, code your own settings, and more
All JOAN modules have their own settings object. This is the place where settings are saved. The contents of this settings object can be saved in, and loaded
from, JSON files. The conversion between these files and the object is handled in the top level JoanModuleSettings object. All setting objects should enherit
this top level object.

It is possible to store all Python base type data in a settings object. But it is also possible to use dicts, lists and custom class objects. They will be
automatically stored and loaded from JSON files.

!!! Warning  
    Multiple levels of custom objects cannot be rebuild from a `json` file (e.g. SettingsObject -> ChildObject -> GrandChildObject is not supported). Limit the data
    stored in a custom child objects to Python base type data.

The settings object is usually directly referenced when a setting is needed. If, for example, the settings object holds a limit it is oke to write:
`if value > self.settings.limit: self.stop()` in your `do()` loop. If you want to prevent the value from being changed while the module is running, you could
copy the value from the settings object to the module action in the initialize function. In this case please make sure to communicate this clearly to the user.

The saving and loading of settings JSON files is backwards compatible by default since only the values that are present in the JSON file are overwritten. All
other values in the settings object are not altered when loading a JSON file. This also means that the `__init__` function of your settings class holds the
default settings.

The settings objects of all modules are shared through the settings singleton which can be found in all modules actions objects. The settings are shared for
reading purposes only, please do not alter settings of other modules from your own module. You can for example deny requested state changes of your module
depending on the settings of other modules. This will force the user to change the settings manually before running.
