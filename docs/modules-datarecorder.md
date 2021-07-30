# Module: DataRecorder

The data recorder module can be used to record the data of your experiment. It automatically sees all shared variables from all other modules. You can select 
which variables to store and where you want them to be stored. below is a screen shot of the data recorder dialog, the next section explains how to use the 
data recorder.

![Data recorder in stopped state](imgs/modules-datarecorder-initialized.png)

## Using the Module
Because the data recorder needs access to the shared variable objects of all other modules, the workflow of the data recorder is fixed. First, in the stopped 
state a save path needs to be set. If no save path is specified, the data recorder will go to error state if you try to transition to initialized. If you do 
not wish to use the data recoder then remove it from JOAN in main.py. The checkbox "Append timestamp to filename" is checked by default, but you can uncheck it 
to save to the actual path you provided.   

!!! Important
    The data recorder will clear any existing files with the same name and overwrite them with new data once you transition to the ready state. Keeping the 
    "Append timestamp" checkbox check will prevent you from loosing data because it will make every filename unique.
    
After specifying a file path where the data is stored, you can transition to the initialized state. In this state all other modules have their settings fixed,
this means the data recorder has access to the final shared variable objects. Now you can define which variables you want to store by checking the appropriate 
boxes in the tree menu. This selection and the save file path specified earlier are saved in the settings of the data recorder. This means use can include them 
in an experiment condition in the experiment manager. Please see the notes about including the data recorder in your experiment on the page about the experiment
 manager.
 
There are some important things to consider when selecting variables to save, please read the block below carefully.  

!!! Important
    Some notes on recording variables with the data recorder   
    
    1. Think carefully about what data you'll need in the future and what you need to save, anything omitted here can not be reconstructed afterwards. Run 
        test experiments and do the full data analysis you plan to do on the real experiment to verify if you have all necessary data.
    
    2. Do **not** simply store everything. Some data objects in the shared variable objects are quite big, if you write them to a file at ≈10 Hz the files will 
        get big quickly and the data recorder might clog up. The carla interface shares array's with road boundaries for example, there are almost no situations
        in which you need to store them. If you do add them to your data recorder, the data files can grow in the order of Mb's/second of recorded data.
    
    3. Since all modules run in parallel and are unsynchronized, the data points you store on a single row might not be taken at exactly the same time. To 
        prevent issues when analysing your data, store the `time` variable for every module that you store data from. These timestamps indicate the precise time
        of that modules data. Also keep in might that for the same reason a data point from a slow running module might be stored in two consecutive rows by the 
        data recorder. This is no error, nor does it indicate that a module is running jerky, even though it might look like it from the stored data.    


### storing trajectories with the data recoder
The data recorder can also store trajectories of ego vehicle 1 when carla interface is used. These trajectories are for use with the haptic controllers only and should not be used as general logging of an experiment. The trajectory saving is a beta feature and you should manually verify that the stored trajectory is actually correct before you use it for anything.    
