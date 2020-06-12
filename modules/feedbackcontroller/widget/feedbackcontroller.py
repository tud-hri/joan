from process import State, translate
from PyQt5 import QtCore, QtWidgets, uic
from modules.feedbackcontroller.action.states import FeedbackcontrollerStates
# from PyQt5.QtWidgets import QWidget
import os
from modules.feedbackcontroller.action.feedbackcontroller import *


class FeedbackcontrollerWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 200
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "feedbackcontroller.ui"))

        self.data = {}
        self.data['SteeringWheelAngle'] = 0
        self.data['Throttle'] = 0

        self.write_news(channel=self, news=self.data)
        self.counter = 0

        self.define_module_state_handler(module=self, module_states=FeedbackcontrollerStates())
        self.module_state_handler.state_changed.connect(self.handle_module_state)
        #self.master_state_handler.state_changed.connect(self.handle_master_state)

        try:
            self.action = FeedbackcontrollerAction()
        except Exception as e:
            print('De error bij de constructor van de widget is: ', e)

        # Initiate the different classes (controllers) you want:
        self._controller = Basecontroller(self)

        # self.Controllers = {}
        self.Controllers = dict([("Manual", Manualcontrol(self)), ("FDCA", FDCAcontrol(self)), ("PD", PDcontrol(self))])

        # initialize controller with first one in the dict
        self._controller = self.Controllers["Manual"]

        self.widget.tabWidget.currentChanged.connect(self.changedControl)

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        # SWangle = self._controller.process()
        # self.counter = self.counter + 1
        # self.data['SteeringWheelAngle'] = SWangle
        # self.data['Throttle'] = 0.5
        # self.write_news(channel=self, news=self.data)
        #print(self.counter)
        joe = self._controller.process()
        print(joe)

    def changedControl(self):
        self._controller = self.Controllers[self.widget.tabWidget.currentWidget().windowTitle()]

        print('control changed!')

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        print(millis)
        try:
            millis = int(millis)
            assert millis > 0, 'QTimer tick interval needs to be larger than 0'
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.window.show()

    def start(self):
        if not self.window.isVisible():
            self._show()
        self.startPulsar()
        self.module_state_handler.request_state_change(self.module_states.FEEDBACKCONTROLLER.RUNNING)

    def stop(self):
        self.module_state_handler.request_state_change(self.module_states.FEEDBACKCONTROLLER.STOPPED)
        self.stopPulsar()

    def _close(self):
        self.window.close()

    def handle_master_state(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            # state_as_state = self.states.get_state(state) # ensure we have the State object (not the int)
            state_as_state = self.master_state_handler.get_state(state)  # ensure we have the State object (not the int)

            # emergency stop
            if state_as_state == self.module_states.ERROR:
                self._stop()

            # update the state label
            self.widget.lbl_state.setText(str(state_as_state))

        except Exception as e:
            print(e)

    def handle_module_state(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            # state_as_state = self.states.get_state(state) # ensure we have the State object (not the int)
            state_as_state = self.module_state_handler.get_state(state)  # ensure we have the State object (not the int)

            # emergency stop
            if state_as_state == self.module_states.ERROR:
                self._stop()

            # update the state label
            self.state_widget.lbl_module_state.setText(str(state_as_state.name))

            if state_as_state == self.module_states.FEEDBACKCONTROLLER.RUNNING:
                self.state_widget.btn_start.setStyleSheet("background-color: green")
            else:
                self.state_widget.btn_start.setStyleSheet("background-color: none")

        except Exception as e:
            print(e)
