# SharedControlDrivingSim

A start to combine classes in a lego-like way to make a driving simulator.<br>
Inspired by mis-haptic-trainer
<br><br>
Editor:<br>
Visual Studio Code

notation of methods is camelCase to conform the already existing code

## Software<br>
* PyQt5-5.13.2<br>
* Python 3.8.1 64-bit<br>

Use PyQt5 and NOT PySide2 because PyQt5 is (more) platform independent.<br>

## Classes
Status is a singleton class <br>
New is a singleton class <br>
Control(Pulsar) <br>
StateHandler(QtCore.QObject) <br>
State <br>
States <br>
Pulsar(QtCore.QThread) <br>
DataRecorderWidget(Control) <br>
MenuWidget(Control) <br>
FeedbackcontrollerWidget(Control) <br>
SteeringcommunicationWidget(Control)<br>
Basecontroller<br>
Arbitrarycontroller(Basecontroller)<br><br>

```mermaid
    classDiagram
        class Status
        class News
        class State
        class States
        class StateHandler
        class Pulsar
        class QObject
        class QThread
        class MenuWidget
        class DataRecorderWidget
        class FeedbackcontrollerWidget
        class Basecontroller
        class Arbitrarycontroller
        class CarlainterfaceWidget

        States "1" ..|> "*" State : Realization
        Status ..|> States : Realization of singleton
        Status ..|> StateHandler : Realization
        QObject --|> StateHandler : Inheritance
        QThread --|> Pulsar : Inheritance
        Pulsar --|> Control : Inheritance
        Control ..|> Status : Realization
        Control ..|> News : Realization
        Control --|> MenuWidget : Inheritance
        Control  --|> DataRecorderWidget : Inheritance
        Control --|> FeedbackcontrollerWidget: Inheritance
        Control --|> SteeringcommunicationWidget: Inheritance
        Control --|> CarlainterfaceWidget: Inheritance

        FeedbackcontrollerWidget ..|> Basecontroller: Instance of
        Basecontroller --|> Arbitrarycontroller: Inheritance

        SteeringcommunicationWidget <|..|> FeedbackcontrollerWidget : Torque Data
        CarlainterfaceWidget <|..|> FeedbackcontrollerWidget: Sim Data

```
## Directories

## process

* control.py <br>
holds the Control class that takes care of loading widgets<br>
holds the singleton News class<br>
holds the singleton Status class
* statehandler.py <br>
handles the available states as part of the Status class
* states.py <br>
holds the available states as part of the Status class

## signals

* pulsar.py <br>
purpose is to use 2 threads, beside the main process.<br>
It turns out that the QTimer object are running in seperate threads but the methods (acting as 'pyqSlots') that should do something (depending on the widget), are part of the main thread. This is something to look at if this is turns out to be a problem.
1. communication with input devices (Sensodrive Steering wheel through PCAN) (as fast as possible, hopefully 1 msec)
2. spread data around to whatever module want to listen; datarecorder, plotter, GUI (200msec or so)

## modules
### modules.datarecorder.widget.datarecorder.py
reads the corresponding .ui file and does all the action needed for this widget
### modules.datarecorder.widget.datarecorder.ui
definition of the gui
### modules.datarecorder.action.datarecorder.py
does all the action needed, like getting and writing data (not yet implemented)

### modules.menu.widget.menu.py
reads the corresponding .ui file and does all the action needed for this widget
### modules.menu.widget.menu.ui
definition of the gui

### modules.interface.widget.interface.py (not used yet)
reads the corresponding .ui file and does all the action needed for this widget
For now this widget is a 'testing' widget to see whether communication between
modules works properly
### modules.interface.widget.interface.ui
definition of the gui

### modules.template.widget.template.py
Template to create other widgets, has predefined connection with the Control class
reads the corresponding .ui file and does all the action needed for this widget
### modules.template.widget.template.ui
definition of the gui

### modules.template.widget.steeringcommunication.py
Widget that handles all communication with the sensodrive wheel, utilizes the PCANBasic
library made by PEAK-SYSTEMS. Widget also shows current state of the wheel.
### modules.template.widget.steeringcommunication.ui
definition of the gui

### modules.template.widget.feedbackcontroller.py
Widget that contains the different controllers that can be used for the car in the carsimulation,
communicates with steeringcommunication the torques that should be inputted on the wheel.
Has an empty 'Basecontroller' class of which added arbitratry controllers will inherit.
This makes sure that we always calculate the selected controller values and send these to 
steeringcommunication.

### modules.template.widget.feedbackcontroller.ui
definition of the gui

<br>
For now main.py is an early versions of how the program might work. <br>
