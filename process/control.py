from signals import Pulsar
from .statehandler import StateHandler, States
from PyQt5 import uic, QtCore
#from queue import Queue

import os 

class Recent:
    '''
    The Recent class is a singleton that holds all most recent status data
    Every class has its own writing area; the key of the class
    Oll other classes may read the value
    '''
    instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.instance:
            klass.instance = object.__new__(Recent)
            klass.recent = {}
            klass.availableKeys = klass.recent.keys()
        return klass.instance

    def __init__(self, recentDataDict, *args, **kwargs):
        self.recent.update(recentDataDict)


class Status:
    '''
    The Status class is a singleton that handles all states as defined in the States class
    To change states the StateHandler class is used
    '''
    instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.instance:
            klass.instance = object.__new__(Status)
            klass.gui = {}
            klass.statehandler = StateHandler()
            klass.states = States()
        return klass.instance

    def __init__(self, guiDict, *args, **kwargs):
        # TODO find out if self.gui is necessary, also see klass.gui
        self.gui.update(guiDict)


class Control(Pulsar):

    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = 'callback' in kwargs.keys() and kwargs['callback'] or []
        Pulsar.__init__(self, *args, **kwargs)

        # start gui and status stuff
        self.ui = 'ui' in kwargs.keys() and kwargs['ui'] or ''
        assert self.ui != '', 'keyword argument should contain key "ui" with a PyQt ui file as value (e.g. ui=<absolute path>menu.ui)' 
        self.widget = self._getGui()
        assert self.widget != None, 'could not create a widget, is %s the correct filename?' % self.ui

        uiKey = os.path.basename(os.path.realpath(self.ui))
        # put widgets in SingletonStatus object for setting state of widgets 
        self.singletonStatus = Status({uiKey: self.widget})
        # end gui and status stuff

        # start queue stuff
        self.queueKey = 'queue' in kwargs.keys() and kwargs['queue'] or ''
        self.singletonQueue = SQueue({self.queueKey: Queue()})
        # end queue stuff


        self.statehandler = self.singletonStatus.statehandler
        self.states = self.singletonStatus.states

        #self.singletonStatus.gui[self.ui] = self.widget
        self.gui = self.singletonStatus.gui

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

    def getAllGui(self):
        return self.singletonStatus.gui

    def getAllQueus(self):
        return self.singletonQueue.queues
