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

## <a name="using_hw_manager"></a>Using the Module
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

The settings in the dialog are quite self explanatory, besides maybe the `sensitivities` section. The higher
a sensitivity the faster it will react to you pushing the appropriate button.
You can set different keys by pressing the `Set Different Keys` button, the button you can change will then
light up green, see the GIF below:

![Keyboard settings gif](gifs/modules-hardwaremanager-keyboard-settings.gif)

!!! Note
    If you try to select the same button twice for a different function you will get notified of doing so. You will be able 
    continue, however it can lead to erratic behaviour.

### Joysticks
The second input you can choose from by default is the `Joystick` input. 

!!! Note 
    The nomenclature `Joystick` may be a bit confusing  since it does not necessarily need to be an actual joystick as 
    you would expect from for example flight simulator. A `Joystick` in JOAN constitutes nothing more than a HID 
    (Human Interface Device). For example, steering wheels by thrustmaster or logitech are also 'Joysticks'.

Whenever adding a Joystick device it will automatically open up the joystick settings dialog (if you do it from the `add hardware input` button):

![Joystick Settings](imgs/modules-hardwaremanager-joystick-settings.PNG)

In here the first thing you do is find your plugged in USB device in the list of `available HID devices`. In this example 
we have a Xbox Controller connected. 

### SensoDrives


## Adding to the Module
If there is any sort of input device or hardware you'd like to add to JOAN ofcourse you can! The method
of doing so is greatly similar to the adding of your own agents described in
[adding your own agent](modules-carlainterface.md#adding_own_agents),please use the same methodology.