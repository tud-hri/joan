# Module: Hardware Manager
The HardwareManager module is quite an essential one, it does what you would expect it to do: it manages the hardware.
In the default version of the hardware manager it handles Hardware Inputs. Ofcourse you could implement any other 
code in python to link other sorts of devices to JOAN if you wish. However in this section we'l mainly focus on the 
3 main default inputs you can choose:

- Keyboard
- Joystick
- SensoDrive
 
In the image below the HardwareManager module is shown how it should look like if you open it up in the 
`STOPPED` state. (without default settings)

![Hwmanager in stopped state](imgs/modules-hardwaremanager-stopped-state.PNG)

## Using the Module
Using the module is quite similar to using other 'core' modules of JOAN. You can add/remove devices in the `STOPPED` 
state only. This will open up a dialog in which you can choose which input you want to add, which will then pop up in the 
hardware list, see the pictures below:

![Hwmanager input selection](imgs/modules-hardwaremanager-input-selection.PNG)
![Hwmanager added input](imgs/modules-hardwaremanager-added-input.PNG)

As mentioned earlier there are (by default) 3 input types you can choose from, in the sections below we'll go into more 
detail for each of them.

### Keyboards
Whenever adding a keyboard it will automatically open up the keyboard settings dialog (if you do it from the `add hardware input` button):

![keyboard settings](imgs/modules-hardwaremanager-keyboard-settings.PNG)

### Joysticks

### SensoDrives


## Adding to the Module
If there is any sort of input device or hardware you'd like to add to JOAN ofcourse you can! The method
of doing so is greatly similar to the adding of your own agents described in
[adding your own agent](modules-carlainterface.md#adding_own_agents),please use the same methodology.