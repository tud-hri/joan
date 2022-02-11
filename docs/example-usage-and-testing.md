# Example usage and testing

To test the functionality of JOAN, we provide an example experiment and a checklist. We tested JOAN with Carla version 0.9.10.

## Testing JOAN without Carla

Installing and building Carla costs a lot of time. In order to test whether JOAN works without Carla:

- Comment out the line `JOANHQACTION.add_module(JOANModules.CARLA_INTERFACE, time_step_in_ms=10)` in `main.py`.
- Run `main.py`

You should see dialogs pop up

The necessary map and experiment files can be downloaded [here]().

Checklist:

- Download the example experiment map [(link)](https://www.dropbox.com/s/kfjuueduzs7df8m/110222-ExampleExpMap.zip?dl=0) and unpack in Carla's Maps folder (for
  us `C:\carla\Unreal\CarlaUE4\Content\Maps\`)
- Download the example experiment setting files [(link)]
- [ ] item
