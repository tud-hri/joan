from process import Control, State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from PyQt5 import QtCore
from modules.joanmodules import JOANModules
from modules.datarecorder.action.states import DatarecorderStates
from modules.datarecorder.action.datarecorderaction import DatarecorderAction
import os

# for editWidgets
from PyQt5 import QtWidgets, QtGui
from functools import partial

class DatarecorderDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(module=JOANModules.DATA_RECORDER, module_action=module_action, master_state_handler=master_state_handler, parent=parent)

        #self.module_action.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.NOTINITIALIZED)

        #self.module_widget.btn_initialize.clicked.connect(self.module_action._clicked_btn_initialize)

        #def __init__(self, *args, **kwargs):
        #kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 200
        #kwargs['callback'] = [self.do]  # method will run each given millis

        #Control.__init__(self, *args, **kwargs)

        #self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "datarecorder.ui"))
        #self.create_settings(module=self, file=os.path.join(os.path.dirname(os.path.realpath(__file__)), "datarecordersettings.json"))
        #self.settings = self.get_module_settings(module='modules.datarecorder.widget.datarecorder.DatarecorderWidget')

        #self.data = {}
        #self.write_news(channel=self, news=self.data)
        
        #self.millis = kwargs['millis']

        # creating a self.module_state_handler which also has the module_states in self.module_state_handler.states
        #self.define_module_state_handler(module=self, module_states=DatarecorderStates())
        #self.module_state_handler.state_changed.connect(self.handle_module_state)
        #self.master_state_handler.state_changed.connect(self.handle_master_state)

        #try:
        #    self.action = DatarecorderAction()
        #    #self.action = DatarecorderAction(self.settings)
        #except Exception as inst:
        #    print('De error bij de constructor van de widget is:    ', inst)

        self.module_widget.btn_initialize.clicked.connect(self.module_action._clicked_btn_initialize)

        # set current data file name
        self.module_widget.lbl_data_filename.setText("< none >")

        # set message text
        self.module_widget.lbl_message_recorder.setText("not recording")
        self.module_widget.lbl_message_recorder.setStyleSheet('color: orange')

        # reads settings if available and expands the datarecorder widget
        try:
            self.module_action._editWidget(layout=self.module_widget.verticalLayout_items)
        except Exception as inst:
            print(inst)

    def handle_module_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            state_as_state = self.module_action.module_state_handler.get_state(state)  # ensure we have the State object (not the int)

            if state_as_state == DatarecorderStates.DATARECORDER.INITIALIZED:
                self.state_widget.btn_start.setEnabled(True)
                self.module_widget.lbl_data_filename.setText(self.module_action.get_filename())

            if state_as_state == DatarecorderStates.DATARECORDER.NOTINITIALIZED:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(False)

            if state_as_state == DatarecorderStates.DATARECORDER.START:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(True)
                self.module_widget.btn_initialize.setEnabled(False)

                # set message text
                self.module_widget.lbl_message_recorder.setText("Busy Recording ...")
                self.module_widget.lbl_message_recorder.setStyleSheet('color: red')

            if state_as_state == DatarecorderStates.DATARECORDER.STOP:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(False)
                self.module_widget.btn_initialize.setEnabled(True)

                # set message text
                self.module_widget.lbl_message_recorder.setText("not recording")
                self.module_widget.lbl_message_recorder.setStyleSheet('color: orange')

            # update the state label
            self.state_widget.lb_module_state.setText(state_as_state.name)
            self.module_widget.repaint()

            if state_as_state == DatarecorderStates.DATARECORDER.START:
                self.state_widget.btn_start.setStyleSheet("background-color: green")
            else:
                self.state_widget.btn_start.setStyleSheet("background-color: none")

        except Exception as inst:
            print(inst)

    '''
    def show(self):
        self.module_widget.show()

        #self.window.show()
        #self.module_state_handler.request_state_change(self.module_states.DATARECORDER.NOTINITIALIZED)

        # connect buttons
        self.module_widget.btn_initialize.clicked.connect(self.module_action._clicked_btn_initialize)

        # set current data file name
        self.module_widget.lbl_data_filename.setText("< none >")

        # set message text
        self.module_widget.lbl_message_recorder.setText("not recording")
        self.module_widget.lbl_message_recorder.setStyleSheet('color: orange')

        # reads settings if available and expands the datarecorder widget
        try:
            self.module_widget.verticalLayout_items = self.module_action._editWidget(self.module_widget.verticalLayout_items)
            self.module_widget.adjustSize()
        except Exception as inst:
            print(inst)
    '''
    '''
    def do(self):
        # handling is done in the action part
        self.action.write()
    '''


    '''
    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except Exception:
            pass

    def show(self):
        #self.window.show()
        #self.module_state_handler.request_state_change(self.module_states.DATARECORDER.NOTINITIALIZED)

        # connect buttons
        self.widget.btn_initialize.clicked.connect(self._clicked_btn_initialize)

        # set current data file name
        self.widget.lbl_data_filename.setText("< none >")

        # set message text
        self.widget.lbl_message_recorder.setText("not recording")
        self.widget.lbl_message_recorder.setStyleSheet('color: orange')

        # reads settings if available and expands the datarecorder widget
        try:
            self.editWidget()
        except Exception as inst:
            print(inst)

    def start(self):
        print('start in datarecorder')
        if not self.window.isVisible():
            self._show()
        #self.module_state_handler.request_state_change(self.module_states.DATARECORDER.START)
        self.action.start()
        self.startPulsar()

    def stop(self):
        #self.module_state_handler.request_state_change(self.module_states.DATARECORDER.STOP)
        print('stop in datarecorder')
        self.stopPulsar()
        self.action.stop()

    def close(self):
        #self.module_state_handler.request_state_change(self.module_states.DATARECORDER.STOP)
        if self.window.isVisible():
            self.window.close()

    def handlemodulesettings(self, module_key, item):
        try:
            print('handlemodulesettings', item.text())
            item_dict = {}
            item_dict[item.text()] = item.isChecked()
            # self.get_available_news_channels() means only modules with news will be there in the datarecorder_settings file
            self.settings.write(groupKey=module_key, item=item_dict, filter=self.get_available_news_channels())
        except Exception as inst:
            print(inst)

    def handle_module_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            state_as_state = self.module_state_handler.get_state(state)  # ensure we have the State object (not the int)

            if state_as_state == self.module_states.DATARECORDER.INITIALIZED:
                self.state_widget.btn_start.setEnabled(True)
                self.widget.lbl_data_filename.setText(self.action.get_filename())

            if state_as_state == self.module_states.DATARECORDER.NOTINITIALIZED:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(False)

            if state_as_state == self.module_states.DATARECORDER.START:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(True)
                self.widget.btn_initialize.setEnabled(False)

                # set message text
                self.widget.lbl_message_recorder.setText("Busy Recording ...")
                self.widget.lbl_message_recorder.setStyleSheet('color: red')

            if state_as_state == self.module_states.DATARECORDER.STOP:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(False)
                self.widget.btn_initialize.setEnabled(True)

                # set message text
                self.widget.lbl_message_recorder.setText("not recording")
                self.widget.lbl_message_recorder.setStyleSheet('color: orange')

            # update the state label
            self.state_widget.lbl_module_state.setText(state_as_state.name)
            self.widget.repaint()

            if state_as_state == self.module_states.DATARECORDER.START:
                self.state_widget.btn_start.setStyleSheet("background-color: green")
            else:
                self.state_widget.btn_start.setStyleSheet("background-color: none")

        except Exception as inst:
            print(inst)

    def handle_master_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            state_as_state = self.master_state_handler.get_state(state)  # ensure we have the State object (not the int)

            # emergency stop
            if state_as_state == self.master_states.ERROR:
                self.stop()
                self.widget.btn_initialize.setEnabled(True)

            # update the state label
            self.state_widget.lbl_module_state.setText(state_as_state.name)
            self.widget.repaint()

        except Exception as inst:
            print(inst)
   
    def _clicked_btn_initialize(self):
        """initialize the data recorder (mainly setting the data directory and data file prefix"""
        self.module_action.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.INITIALIZING)
        if self.module_action.initialize_file():
            self.module_action.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.INITIALIZED)
    '''