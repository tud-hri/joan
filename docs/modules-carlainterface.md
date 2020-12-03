# Module: CARLA Interface

Depending on whether you want to use the CARLA simulation environment with JOAN, the carla interface module is one of the core modules. If you want 
to do anything with CARLA it is advised to use this module.
An example screenshot of the module dialog layout in the initial STOPPED state is shown below:

![carlainterface_dialog](imgs/modules-carlainterface-dialog_stopped.PNG)

In this section we'll cover 3 main things; the connection to CARLA, adding agents to simulation and creating your own agent class to add.

## Carla Connection
Whenever you have included CarlaInterface in your modules, JOAN will try to connect to CARLA at start up. If this process fails you will see the following
dialog:

![carlainterface_dialog](imgs/modules-carlainterface-connection-exception.PNG)

This could happen if you did not start up CARLA in Unreal yet or there are some other connection issues. If connection failed at startup this is not a problem,
via the main JOAN window you can still connect to carla by pressing the connect button, shown below:

![carlainterface_dialog](imgs/modules-carlainterface-tab-in-main.PNG)

If JOAN is already connected the connect button will not be available but the disconnect button is enabled.