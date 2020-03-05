from signals import Pulsar
from .statehandler import StateHandler, States
from PyQt5 import uic, QtCore

import os 

class Status():
    '''
    The Status class is a singleton that handles all states as defined in the States class
    To change states the StateHandler class is used
    '''
    __instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.__instance:
            klass.__instance = object.__new__(Status)
            klass.gui = {}
            klass.statehandler = StateHandler()
            klass.states = States()
        return klass.__instance

    def __init__(self, guiDict, *args, **kwargs):
        # TODO find out if self.gui is necessary, also see klass.gui
        self.gui.update(guiDict)
        


class Control(Pulsar):

    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = 'callback' in kwargs.keys() and kwargs['callback'] or []
        Pulsar.__init__(self, *args, **kwargs)

        self.ui = 'ui' in kwargs.keys() and kwargs['ui'] or ''
        assert self.ui != '', 'keyword argument should contain key "ui" with a PyQt ui file as value (e.g. ui=<absolute path>menu.ui)' 
        self.widget = self._getGui()
        assert self.widget != None, 'could not create a widget, is %s the correct filename?' % self.ui
        
        
        uiKey = os.path.basename(os.path.realpath(self.ui))
        # put widgets in SingletonControl object for setting state of widgets 
        self.singletonControl = Status({uiKey: self.widget})
        self.statehandler = self.singletonControl.statehandler
        self.states = self.singletonControl.states

        #self.singletonControl.gui[self.ui] = self.widget
        self.gui = self.singletonControl.gui

        print('\n',self.gui,'\n')
   
    def _getGui(self):
        '''
        return a Qwidget which can be shown
        '''
        try:
            print (os.path.dirname(os.path.realpath(__file__)))
            return uic.loadUi(self.ui)

        except Exception as inst:
            print('Error')
            print(inst)
            return None


