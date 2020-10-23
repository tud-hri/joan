# JOAN state machine

All JOAN modules have there own state machine. There are four possible states: Idle, Ready, Running and Error. All modules are initialized in the Idle state,
they can transfer to the Ready state when the module is initialized. And to the Running state when the module is started. If an error occurs the module should
transfer to the Error state.

Besides these states, the state machine can also handle state messages. These messages can be used to incorporate module specific messages. Please use these
messages if you want to convey information to the user, do_while_running not add extra states since this will effect all state machines of all modules.

State changes can be requested at the state machine by calling the `request_state_change` function with the desired target state and an optional message. If the
state change fails or is illegal, the module will automatically move to the Error state.

The legality of state changes can be customized per module by passing a callable to the state machine (`set_state_transition_condition`) that will evaluate to
True or False. An example of how this works can be found in the template module (`templateaction.py`). All states can have an entry and exit action. This are
also callable's that will be called on entry or exit of a state.

The state machine also supports automatic transitions, these will be executed if a state is entered and the condition for the transition is met. An example of
this can be found in the template module.
