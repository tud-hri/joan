## Structure of main JOAN components

JOAN components are used in modules that you can add.
<br>
They are loaded through the Main window as they are defined in JOANModules.py.
<br><br>
Your modules, which should consist of an action- and a dialog-part inherit JOAN components to make building and using modules easier for you.
<br>
Using the JOANModuleAction let your module work with:
<ul>
<li>Status, containing the State and the StateMachine</li>
<li>News, your module may write to it's own news-channel using a time interval</li>
<li>Settings, containing settings in json format</li>
<li>performance monitor (optional) on the current module</li>
</ul>

Using the JOANModuleDialog gives your module a base dialog window with buttons:
<ul>
<li>Start</li>
<li>Stop</li>
<li>Initialize</li>
</ul>
It also has an input field for setting a timer interval used when writing news (=latest data).

## Schematic overview
```mermaid
graph TD
   A((Main))-->|starts|B(JOANModules)
   B-->|define|C(your module)
   C-->D{consist of}
   D-->|action|G(Action class)
   D-->|dialog|H(Dialog class)
   G-->|inherits from|E(JOANModuleAction<br>- Status<br>- News<br> -Settings)
   H-->|inherits from|F(JOANModuleDialog<br>- Dialog base)
```