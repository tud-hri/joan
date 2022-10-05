# Some extra remarks

This page contains some additional notes 


## Editing and packaging maps
!!! Note 
    To prevent the weather settings to be missing while playing the editor, when adding your map to the maps folder, also add your map to `BP_Weather`. 
    This can be done by opening `BP_Weather` in the folder `/Carla/Blueprints/Weather`. In the `Get Town` function, click on the `Default Weathers` block. Now click the plus (Add elements) and add the name of your map.


!!! Note 
    (Tested in June 2022) When trying to package your project, some reference errors with the API may occur. Make sure that the following steps are followed.
    Go to Project Settings in Unreal. Then move over to `Project > Packaging`. In the `Packaging` tab, click on `Show advanced` and under `Directories to never cook` add `/Game/Carla/Blueprints/Lights`. 
