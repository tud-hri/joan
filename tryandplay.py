# Why PyQt5
# see https://www.learnpyqt.com/blog/pyqt5-vs-pyside2/
# make userwindow, see https://www.codementor.io/@deepaksingh04/design-simple-dialog-using-pyqt5-designer-tool-ajskrd09n



# cd \Users\localadmin\AppData\Local\Programs\Python\Python38
# python.exe \Users\localadmin\source\repos\SharedContreolDrivingSim\tryandplay.py
import time
import sys
from PyQt5 import QtWidgets, uic
from hapticsimulator.states import States
from hapticsimulator.statehandler import StateHandler
from hapticsimulator.haptictrainer import HapticTrainer
from signals.pulsar import ActOnData

class Gui():
    def __init__(self, uiName):
        self._uiName = uiName
        self.haptictrainer = HapticTrainer()

    def getGui(self):
        '''
        return a Qwidget which can be shown
        '''
        try:
            return uic.loadUi(self._uiName)

        except Exception as inst:
            print('Error')
            print(inst)
            return None


if __name__ == '__main__':
    states = States()

    menuWidget = None
    def laad():
        pass

    def stateChanged(state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        
        stateAsState = states.getState(state) # ensure we have the State object (not the int)
        
        # update the state label
        menuWidget.lblState.setText(str(stateAsState))


    try:
        # lees widgets in van een directory
        # maak de widgets met Gui (en dus ook met haptichandler en states)
        # maak ActOnData(Pulsar) met widgets
        # maak SpreadData(Pulsar) met widgets 

        '''
        h1 = HapticTrainer(23,6, e='1')
        print (h1, h1.result())

        h2 = HapticTrainer(32,9, e="2")
        print (h2, h2.result())
        assert h1 == h2, "no singleton"
        '''
        app = QtWidgets.QApplication(sys.argv)
        
        menuWindow = Gui("menu.ui")
        print ('type:', type(menuWindow))
        menuWidget = menuWindow.getGui()
        menuWidget.btnQuit.clicked.connect(app.quit)
        h3 = HapticTrainer(gui=menuWidget)


        h3.statehandler.stateChanged.connect(stateChanged)
        print (h3.statehandler.state)
        h3.statehandler.stateChanged.emit(h3.statehandler.state)
        print (h3.statehandler.requestStateChange(h3.statehandler.state))


        menuWidget.show()
        
        #time.sleep(1)
        getData = ActOnData(millis=20)
        pollWindow = Gui("interfacewidget.ui")
        print ('type:', type(pollWindow))
        pollWidget = pollWindow.getGui()
        pollWidget.btnLoadInterface.clicked.connect(getData.startPulsar)
        h4 = HapticTrainer(gui=menuWidget)
        #pollWidget.btnLoadInterface.clicked.connect(laad)
        #h4.statehandler.stateChanged.emit(h4.statehandler.state)

        pollWidget.show()
        #time.sleep (1)
        
        print(sys.exit(app.exec()))
    except Exception as inst:
        print(inst)

