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

        #self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "datarecorder.ui"))
        #self.create_settings(module=self, file=os.path.join(os.path.dirname(os.path.realpath(__file__)), "datarecordersettings.json"))
        #self.settings = self.get_module_settings(module='modules.datarecorder.widget.datarecorder.DatarecorderWidget')

        #self.data = {}
        #self.write_news(channel=self, news=self.data)

        self.module_widget.btn_initialize.clicked.connect(self.module_action._clicked_btn_initialize)

        # set current data file name
        self.module_widget.lbl_data_filename.setText("< none >")

        # set message text
        self.module_widget.lbl_message_recorder.setText("not recording")
        self.module_widget.lbl_message_recorder.setStyleSheet('color: orange')

        # reads settings if available and expands the datarecorder widget
        self.module_action._editWidget(layout=self.module_widget.verticalLayout_items)


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
            self.state_widget.lbl_module_state.setText(state_as_state.name)
            self.module_widget.repaint()

            if state_as_state == DatarecorderStates.DATARECORDER.START:
                self.state_widget.btn_start.setStyleSheet("background-color: green")
            else:
                self.state_widget.btn_start.setStyleSheet("background-color: none")

        except Exception as inst:
            print(inst)
