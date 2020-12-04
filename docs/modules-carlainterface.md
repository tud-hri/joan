# Module: CARLA Interface

Depending on whether you want to use the CARLA simulation environment with JOAN, the carla interface module is one of the core modules. If you want 
to do anything with CARLA it is advised to use this module.
An example screenshot of the module dialog layout in the READY state is shown below:

![carlainterface_dialog](imgs/modules-carlainterface-dialog_ready.PNG)

In this section we'll cover 3 main things; the connection to CARLA, adding agents to simulation and creating your own agent class to add.

## Carla Connection
Whenever you have included CarlaInterface in your modules, JOAN will try to connect to CARLA at start up. If this process fails you will see the following
dialog:

![Carla interface connection exception](imgs/modules-carlainterface-connection-exception.PNG)

This could happen if you did not start up CARLA in Unreal yet or there are some other connection issues. If connection failed at startup this is not a problem,
via the main JOAN window you can still connect to carla by pressing the connect button, shown below:

![Carla Interface Tab](imgs/modules-carlainterface-tab-in-main.PNG)

If JOAN is already connected the connect button will not be available but the disconnect button is enabled. One last thing remains to be said about the carla connection.
Due to the fact that we use multiprocessing we need to connect to Carla again when the module process is created (this is done after clicking 'get ready'). This makes sure
we have acces to our carla pythonapi function within this process. There is however a big note to this:

!!! Important
    Whenever you are already in the 'READY' state, and you stop CARLA from the unreal side, this will lead to erratic behaviour in JOAN. So never stop your
    experiments via the quit button in Unreal. Ideally you use the 'play' button in unreal once before starting up JOAN and stop it again after you quit JOAN.
    
## Adding Agents
As with most modules it is only possible to add, remove or change settings in the STOPPED state:

![Carla interface dialog stopped](imgs/modules-carlainterface-dialog_stopped.PNG)

So whenever pressing the 'add agent' button a dialog will pop-up prompting you to choose what sort of agent you'd like to add. In the default JOAN only 1 agent is 
available, namely an 'ego_vehicle'.

![Carla interface agent select dialog](imgs/modules-carlainterface-agentselectdialog.PNG)

Clicking OK wil open the settings of this particular Ego Vehicle.

![Ego Agent Settings](imgs/modules-carlainterface-ego-agent-settings.PNG)

As can be seen in the image above we need to set some settings before we can actually do anything with the ego vehicle. The options for input/and haptic controller will 
only be available if these have been added in that particular module. Spawnpoints and CarType are directly communicated from CARLA, therefore if you have no connection to carla
these will be empty (another hint that you should connect to carla first).
If you add 2 vehicles and they have the same spawnpoint an message will pop-up saying that there is a spawnpoint conflict and the spawnpoint will reset to 'None':

![Double spawnpoint message](imgs/modules-carlainterface-double-spawnpoint.PNG)