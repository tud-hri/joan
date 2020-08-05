
# datarecorder class diagram
Datarecorder consist of a moduleWidget called DatarecorderWidget and a moduleAction called Datarecorderaction

DataRecorderWidget(Control) 
moduleWidget(Control) 
moduleAction(Control) 
module_states(MasterStates)

```mermaid
    classDiagram
        class QThread
        class moduleWidget
        class moduleAction
        class module_states
        class DatarecorderStates
        class DatarecorderWidget
        class DatarecorderAction
        class DataWriter
        class DatarecorderSettings
        class State

        QThread --|> DataWriter : Inheritance
        moduleWidget --> DatarecorderWidget
        moduleAction --> DatarecorderAction
        module_states --> State : Realization
        DatarecorderWidget ..|> DatarecorderStates : Realization
        DatarecorderWidget ..|> DatarecorderAction : Realization
        DatarecorderAction ..|> DataWriter : Realization
        DatarecorderWidget ..|> DatarecorderSettings : Realization
        DataWriter ..|> DatarecorderSettings : Realization
```


# feedbackcontroller class diagram
CarlainterfaceWidget(Control) 
FeedbackcontrollerWidget(Control) 
SteeringcommunicationWidget(Control)
Basecontroller
Arbitrarycontroller(Basecontroller)


```mermaid
    classDiagram
        class FeedbackcontrollerWidget
        class Basecontroller
        class Arbitrarycontroller
        class CarlainterfaceWidget
        class SteeringcommunicationWidget

        Control --|> FeedbackcontrollerWidget: Inheritance
        Control --|> SteeringcommunicationWidget: Inheritance
        Control --|> CarlainterfaceWidget: Inheritance

        FeedbackcontrollerWidget ..|> Basecontroller: Instance of
        Basecontroller --|> Arbitrarycontroller: Inheritance

        SteeringcommunicationWidget <|..|> FeedbackcontrollerWidget : Torque Data
        CarlainterfaceWidget <|..|> FeedbackcontrollerWidget: Sim Data
```
