
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
        class moduleAction
        class moduleStates

        MasterStates "1" ..|> "*" State : Realization
        Status ..|> MasterStates : Realization of singleton
        Status ..|> StateHandler : Realization
        QObject --|> StateHandler : Inheritance
        QThread --|> Pulsar : Inheritance
        Pulsar --|> Control : Inheritance
        Control ..|> Status : Realization
        Control ..|> News : Realization

        Control --|> moduleAction : Inheritance
        Control  --|> MainModuleWidget : Inheritance
        MasterStates --|> moduleStates : Inheritance
        moduleStates "1" ..|> "*" State : Realization
```