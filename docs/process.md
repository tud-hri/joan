
## Classes
Status is a singleton class <br>
News is a singleton class <br>
Control(Pulsar) <br>
StateHandler(QtCore.QObject) <br>
State <br>
MasterStates <br>
Pulsar(QtCore.QThread) <br>
MainModuleWidget(Control) <br>

# Main process class diagram

```mermaid
    classDiagram
        class Status
        class News
        class State
        class MasterStates
        class StateHandler
        class Pulsar
        class QObject
        class QThread
        class MainModuleWidget
        class moduleWidget
        class moduleAction
        class module_states

        MasterStates "1" ..|> "*" State : Realization
        Status ..|> MasterStates : Realization of singleton
        Status ..|> StateHandler : Realization
        QObject --|> StateHandler : Inheritance
        QThread --|> Pulsar : Inheritance
        Pulsar --|> Control : Inheritance
        Control ..|> Status : Realization
        Control ..|> News : Realization
        Control --|> moduleWidget : Inheritance
        Control --|> moduleAction : Inheritance
        Control  --|> MainModuleWidget : Inheritance
        MasterStates --|> module_states : Inheritance
        module_states "1" ..|> "*" State : Realization
```