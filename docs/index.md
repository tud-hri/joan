# JOAN simulator documentation

Welcome to the JOAN Simulator documentation. In this 'readthedocs' the ins and outs of the JOAN Simulator will be elaborated upon.  We would also strongly recommend you to check out the CARLA documentation on which this simulator is heavily based:
[CARLA Documentation](https://carla.readthedocs.io/en/latest/). 

You can find the public repository [here][repolink]. Note that JOAN is still under development, so core functionality may change over time. We'll post releases as soon as we think we are ready :-)

[repolink]: https://gitlab.tudelft.nl/tud-cor-hri/joan-framework/joan

<iframe width="560" height="315" src="https://www.youtube.com/embed/TLLw48isYJU" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

JOAN is developed by members of the [Human-Robot Interaction group](https://delfthapticslab.nl) at Cognitive Robotics of Delft University of Technology. This home-page serves as the table of contents of this document, a little bit below an overview is given with a short description of the sections and what they contain. 

## Setup
* __[Setup your JOAN and CARLA project on TUD hardware](setup-on-tud-shared-hardware.md)__ - guide on how to install your project on TUD shared hardware (probably your first step)
* __[Setup on Windows](setup-carla-windows.md)__ - Guide on how to setup CARLA and JOAN on Windows OS
* __[Setup on Linux](setup-carla-linux.md)__ - Guide on how to setup CARLA and JOAN on Linux OS (Not documented yet)
* __[Setup JOAN](setup-joan.md)__ - Guide on how to setup your own JOAN project

## How to work with JOAN
* __[JOAN structure](joan-structure.md)__ - Overview of JOAN's structure (main components, etc.)
* __[Run JOAN](joan-run.md)__ - Quick start on how to execute JOAN
* __[How to work with JOAN](joan-workflow.md)__ - Guide on how to setup and run JOAN (connect to CARLA, setup the modules, ...)
* __[How to create a custom JOAN module](joan-add-module.md)__ - Guide on how to create your own JOAN modules
* __[Info on JOAN's settings structure](joan-settings.md)__ - JOAN uses `Settings` to save you to set up every module after you run JOAN; read more about them here.
* __[Info on JOAN's state machine](joan-state-machine.md)__ - Info on JOAN's state machine
* __[Info on JOAN's experiment manager](joan-experiment-manager.md)__ - How to use the experiment manager


## Other documentation
* __[Quick start CARLA Unreal Engine](other-carle-ue4.md)__ - Quick start guide with Unreal Editor for CARLA and JOAN (under construction)
* __[Quick start source Control (git)](other-git.md)__ - Quick start guide for source control with GIT
* __[SensoDrive Explanation](other-sensodrive.md)__ - Some remarks/explanation and 'best practices' for working with a SensoDrive (mainly TUDelft Students)

## Contributing
* __[Guidelines](contributing-guidelines.md)__ - Short explanation of guidelines if you want to add to JOAN
* __[Coding Standard](contributing-coding-standard.md)__ - Brief explanation of the coding standard of JOAN
