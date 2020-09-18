# Introduction

JOAN is a human-automated vehicle simulator specifically built to enable human-in-the-loop experiments. We build JOAN on top of CARLA, a simulator developed for autonomous driving research. JOAN's main goal is to provide researchers with an customizable framework and easy to use interface for setting up experiments that involve driving simulation. 

CARLA provides us with a realistic virtual driving simulator, in which the user can create complex and realistic traffic simulations. CARLA takes care of the physics computations, updates of the world and the actors in the world and much more. JOAN plug into this by providing you with means to control an actor through a steering wheel and pedals, create experiments, log data, code and test haptic feedback on the steering wheel, etc.

JOAN mainly consists of modules, which communicate with each other through a News channel. The main modules are:

- CARLA interface
- Hardware Manager
- Data recorder
- Steering Wheel Controller
- Experiment Manager

See [JOAN overview](firststeps-joan-overview.md) for more information, or read the module-specific documentation.

This documentation will help you in setting up CARLA and JOAN, guide you through your first steps, and provide more in depth information in how JOAN works and how you can tweak it to your preferences (which is highly encouraged!).

Have fun!

