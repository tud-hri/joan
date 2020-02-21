# Why PyQt5
# see https://www.learnpyqt.com/blog/pyqt5-vs-pyside2/
# make userwindow, see https://www.codementor.io/@deepaksingh04/design-simple-dialog-using-pyqt5-designer-tool-ajskrd09n



# cd \Users\localadmin\AppData\Local\Programs\Python\Python38
# python.exe \Users\localadmin\source\repos\SharedContreolDrivingSim\tryandplay.py
import time
import sys
from PyQt5 import QtWidgets, uic
from hapticsimulator.states import States
from hapticsimulator.haptictrainer import HapticTrainer

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
    try:
        h1 = HapticTrainer(23,6, e='1')
        print (h1, h1.result())

        h2 = HapticTrainer(32,9, e="2")
        print (h2, h2.result())
        assert h1 == h2, "no singleton"

        app = QtWidgets.QApplication(sys.argv)
        
        menuWindow = Gui("menu.ui")
        print (type(menuWindow))
        menuWidget = menuWindow.getGui()
        menuWidget.show()
        
        time.sleep(3)
        pollWindow = Gui("interfacewidget.ui")
        pollWidget = pollWindow.getGui()
        pollWidget.show()
        time.sleep (3)
        
        print(sys.exit(app.exec()))
    except Exception as inst:
        print(inst)

