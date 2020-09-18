# JOAN experiment manager

To run experiments, you need to define your conditions and run them in the order you want. To make your life a bit easier, we built an Experiment Manager module, in which you can:

- create or modify an experiment,
- add conditions to the experiment,
- select the conditions you actually want to run in your experiment,
- set the order of the conditions, and
- customize each transition between conditions (such as respawning cars and traffic)

The experiment manager has two main components: __conditions__ and __transitions__. We will describe how to use them below.

---

## How does the experiment manager work?

The experiment manager stores and sets the [settings of all modules](joan-settings.md) that are relevant for your experiment. Each modules has its own settings. For example, the settings of the steering wheel controller module contain the current values of the controller gains. 

When running and experiment, per condition, you want to change these settings. The experiment manager checks the current settings of the controller module and sets the value that corresponds to the condition you want to activate and run next in your experiment. 

The opposite happens when you are defining your experiment: you change the settings of each module that you want to change for each condition. The experiment manager recognized which settings you changed and stores these changes. 

The experiments are stored in a `json` file, which you can open in any text editor to check whether your experiment and conditions are to your liking.

---

## How do I use the experiment manager?

