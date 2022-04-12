# Module: DataPlotter
The DataPlotter module was created for debugging purposes. It can provide live insight into what is going on, without having to log all data and then plotting it after. For data analysis, we do recommend using the data recorder and plotting the data afterward. This module automatically has access to all variables stored in the News channels of all active modules. If you want to plot a variable here, the only thing you have to do is make sure it is shared on the News channel. Some things have to be kept in mind when using this module, but before we go into that, the module is shown below as it should look like in the `STOPPED` state:
 
![DataPlotter](imgs/modules-dataplotter-stopped.PNG)
 
## Using the Module
 The main big difference between the data plotter and the other modules is that it is adjustable during the `RUNNING` and `READY`
 states. This is because the shared variables only become available after the rest is in `READY`. This means that we only see
 the variables we can plot after we've reached the `READY` state as shown below:
 
  ![DataPlotter Ready](imgs/modules-dataplotter-ready.PNG)
 
 In the image above we have only included a keyboard input in the `Hardware Manager`. We can also immediately see that the HardwareManager 
 is the only included module besides the data plotter.
 
 If we now check or uncheck these items we can see what the value was over the last 5 seconds, in the graph on the right. The GIF below
 will nicely show what is happening. Also notice that the legend is updated automatically. 

!!! Note
    It is not shown in the gif below, but we can also delete and add plots during the `running` state! :)
 
 ![DataPlotter GIF](gifs/modules-dataplotter.gif)
 
!!! Note
    If you plot CarlaInterface variables keep in mind that the data you receive from Carla is always from the last applied frame. This means that
    there will always be a bit of a delay between the data from for example the brake in hardware manager w.r.t. the applied input in CARLA.
