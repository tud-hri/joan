from process import Control, State, translate
from PyQt5 import QtCore, uic
from modules.hardwarecommunication.action.states import HardwarecommunicationStates
from modules.hardwarecommunication.action.hardwarecommunication import HardwarecommunicationAction, BaseInput
import os

class HardwarecommunicationWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 2
        kwargs['callback'] = [self.do]  # method will run each given millis
        Control.__init__(self, *args, **kwargs)
        
        self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremanager_ui.ui"))
        self._input_data = {}
        self._inputlist = {}
        self.counter = 0
        # creating a self.module_state_handler which also has the module_states in self.module_state_handler.states
        self.define_module_state_handler(module=self, module_states=HardwarecommunicationStates())
        self.module_state_handler.state_changed.connect(self.handle_module_state)
        self.master_state_handler.state_changed.connect(self.handle_master_state)
        
        # use Action with state handling, using only this widgets state changes
        try:
            self.action = HardwarecommunicationAction()
            self.action.widget = self
        except Exception as inst:
            print(inst)
        
        self._input_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/inputtype_ui.ui"))
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.action.selected_input)
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.do)
        self.widget.btn_add_hardware.setEnabled(False)
        self.widget.btn_add_hardware.clicked.connect(self._input_type_dialog.show)

        self._inputlist = self.action.input_devices_classes

        self._input = BaseInput(self, self.action)
        
        self.write_news(channel=self, news=self._input_data)

        self.installEventFilter(self)

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self._inputlist = self.action.input_devices_classes
        self._input_data.clear()
        
        for key in self._inputlist:
            try:
                self._input_data[key] = self._inputlist[key].process()
                self.write_news(channel=self, news=self._input_data)
            except Exception as inst:
                    print("Error in Do of hardware comm is:", inst)
                    pass
            


    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.window.show()
        module_states_dict = self.module_states.get_states()
        for state in module_states_dict:
            print('in HardwarecommunicationStates bij show', state, module_states_dict[state])


    def start(self):
        self.widget.btn_add_hardware.setEnabled(True)
        if not self.window.isVisible():
            self._show()
        self.module_state_handler.request_state_change(self.module_states.HARDWARECOMMUNICATION.RUNNING)
        self.startPulsar()

    def stop(self):
        self.widget.btn_add_hardware.setEnabled(False)
        self.module_state_handler.request_state_change(self.module_states.HARDWARECOMMUNICATION.STOPPED)
        self.stopPulsar()

    def _close(self):
        self.window.close()

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
                self._stop()

            # update the state label
            self.widget.lblState.setText(str(state_as_state))
            self.widget.repaint()

        except Exception as inst:
            print (inst)

    def handle_module_state(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #state_as_state = self.states.get_state(state) # ensure we have the State object (not the int)
            state_as_state = self.module_state_handler.get_state(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if state_as_state == self.module_states.ERROR:
                self._stop()

            # update the state label
            self.state_widget.lblModuleState.setText(str(state_as_state.name))
            self.state_widget.repaint()

            if state_as_state == self.module_states.HARDWARECOMMUNICATION.RUNNING:
                self.state_widget.btn_start.setStyleSheet("background-color: green")
            else:
                self.state_widget.btn_start.setStyleSheet("background-color: none")

        except Exception as inst:
            print (inst)
