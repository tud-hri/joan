# JOAN state machine

All JOAN modules have a state machine. There are five possible states: Stopped, Initialized, Ready, Running, and Error.

Besides these states, the state machine can also handle state messages. These messages can be used to incorporate module-specific messages. Please use these
messages if you want to convey information to the user, do not add extra states since this will affect all state machines of all modules.

State changes can be requested at the state machine by calling the `request_state_change` function with the desired target state and an optional message. If the
state change fails or is illegal, the module will automatically move to the Error state.

The legality of state changes can be customized per module by passing a callable to the state machine (`set_state_transition_condition`) that will evaluate to
True or False. An example of how this works can be found in the template module (`template_manager.py`). All states can have an entry and exit action. These are
also callable's that will be called on entry or exit of a state.

The state machine also supports automatic transitions, these will be executed if a state is entered and the condition for the transition is met.
