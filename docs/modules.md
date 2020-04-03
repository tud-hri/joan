
# datarecorder class diagram
Datarecorder consist of a moduleWidget called DatarecorderWidget and a moduleAction called Datarecorderaction

DataRecorderWidget(Control) <br>
moduleWidget(Control) <br>
moduleAction(Control) <br>
moduleStates(MasterStates)<br><br>

```mermaid
    classDiagram
        class QThread
        class moduleWidget
        class moduleAction
        class DatarecorderWidget
        class DatarecorderAction
        class DataWriter

        QThread --|> DataWriter : Inheritance
        moduleWidget --> DatarecorderWidget
        moduleAction --> DatarecorderAction
        DatarecorderWidget ..|> DatarecorderAction : Realization
        DatarecorderAction ..|> DataWriter : Realization
```


# feedbackcontroller class diagram
CarlainterfaceWidget(Control) <br>
FeedbackcontrollerWidget(Control) <br>
SteeringcommunicationWidget(Control)<br>
Basecontroller<br>
Arbitrarycontroller(Basecontroller)<br><br>


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
