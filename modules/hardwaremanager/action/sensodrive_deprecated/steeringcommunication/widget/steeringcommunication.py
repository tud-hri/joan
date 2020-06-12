from PyQt5 import QtCore
import os
from modules.steeringcommunication.action.states import SteeringcommunicationStates
from modules.steeringcommunication.action.steeringcommunication import SteeringcommunicationAction

class SteeringcommunicationWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"steeringcommunication.ui"))
        self.data = {}
        self.data['throttle'] = 0
        self.data['damping'] = 0
        self.write_news(channel=self, news=self.data)

        # creating a self.module_state_handler which also has the module_states in self.module_state_handler.states
        self.define_module_state_handler(module=self, module_states=SteeringcommunicationStates())
        self.module_state_handler.state_changed.connect(self.handle_module_state)
        #self.master_state_handler.state_changed.connect(self.handle_master_state)

        try:
            self.action = SteeringcommunicationAction()
        except Exception as inst:
            print('De error bij de constructor van de widget is:   ', inst)
        self.i = 0

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.i  = self.i + 1

        self.data['throttle'] = self.i
        self.data['damping'] = 0
        self.write_news(channel=self, news=self.data)

        if(self.module_state_handler._state is self.module_states.STEERINGWHEEL.ON):
            print(self.master_state_handler._state)
            print(self.i)
        pass

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.widget.show()
        self.widget.btn_initialize.clicked.connect(self.action.initialize)
        self.widget.btn_start.clicked.connect(self.action.start)
        self.widget.btn_stop.clicked.connect(self.action.stop)
        #self.action.initialize()
        

    def start(self):
        if not self.widget.isVisible():
            self._show()
        self.startPulsar()

    def stop(self):
        self.stopPulsar()

    def _close(self):
        self.widget.close()

    def handle_module_state(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #state_as_state = self.states.get_state(state) # ensure we have the State object (not the int)
            state_as_state = self.module_state_handler.get_state(state) # ensure we have the State object (not the int)
            
            # Start if the system is initialized
            if state_as_state == self.module_states.STEERINGWHEEL.INITIALIZED:
                self.start()

            # Reinitialize available if exception
            if state_as_state == self.module_states.STEERINGWHEEL.ERROR.INIT:
                self.widget.btn_initialize.setEnabled(True)
            else:
                self.widget.btn_initialize.setEnabled(False)


            # emergency stop
            if state_as_state == self.module_states.ERROR:
                self.stop()

            # update the state label
            self.widget.lbl_state.setText(state_as_state.name)
            self.widget.repaint()

        except Exception as inst:
            print (inst)

    def handle_master_state(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #state_as_state = self.states.get_state(state) # ensure we have the State object (not the int)
            state_as_state = self.master_state_handler.get_state(state) # ensure we have the State object (not the int)
            
           # emergency stop
            if state_as_state == self.module_states.ERROR:
                self.stop()

            # update the state label
            self.widget.lbl_state.setText(state_as_state.name)
            self.widget.repaint()


        except Exception as inst:
            print (inst)
