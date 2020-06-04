from process import Control, State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from PyQt5 import QtCore
from modules.joanmodules import JOANModules
from modules.datarecorder.action.states import DatarecorderStates
from modules.datarecorder.action.datarecorderaction import DatarecorderAction
import os
import glob
import numpy as np

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

        self.module_widget.btn_initialize.clicked.connect(self.initialize)

        # set current data file name
        self.module_widget.lbl_data_filename.setText("< none >")

        # set message text
        self.module_widget.lbl_message_recorder.setText("not recording")
        self.module_widget.lbl_message_recorder.setStyleSheet('color: orange')

        # set trajectory buttons functionality
        self.module_widget.btn_save.setEnabled(False)
        self.module_widget.btn_discard.setEnabled(False)
        self.module_widget.line_trajectory_title.setEnabled(False)
        self.module_widget.check_trajectory.setEnabled(False)
        self.module_widget.btn_save.clicked.connect(self.save_trajectory)
        self.module_widget.btn_discard.clicked.connect(self.discard_trajectory)
        self.module_widget.check_trajectory.stateChanged.connect(self.check_trajectory_checkbox)
        self.module_widget.line_trajectory_title.textEdited.connect(self.check_trajectory_filename)

    def check_trajectory_checkbox(self):
        self.module_action.trajectory_recorder.trajectory_record_boolean(self.module_widget.check_trajectory.isChecked())


    def check_trajectory_filename(self):
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        hcr_path = os.path.join(path,'steeringwheelcontrol/action/swcontrollers/trajectories/*.csv')  #Dit moet handiger kunnen
        
        self.trajectory_title = self.module_widget.line_trajectory_title.text()

        for fname in glob.glob(hcr_path):
            if (self.trajectory_title == (os.path.basename(fname)[:-4]) or self.trajectory_title == ''):
                self.module_widget.label_trajectory_filename.setText('Filename Invalid! (empty or already exists)')
                self.module_widget.btn_save.setEnabled(False)
                break
            else:
                self.module_widget.btn_save.setEnabled(True)
                self.module_widget.label_trajectory_filename.setText('Will save file as: '+ self.trajectory_title + '.csv')


    def initialize(self):
        self.module_action._clicked_btn_initialize()
                # reads settings if available and expands the datarecorder widget
        try:
            self.module_action._editWidget(layout=self.module_widget.verticalLayout_items)
        except Exception as inst:
            print(inst)

    def save_trajectory(self):
        self.trajectory_data = self.module_action.trajectory_recorder.generate_trajectory()
        self.trajectory_data_visual = self.trajectory_data[0:len(self.trajectory_data):5]
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        hcr_path = os.path.join(path,'steeringwheelcontrol/action/swcontrollers/trajectories/')  #Dit moet handiger kunnen
        	
        # Save 2D numpy array to csv file
        try:
            np.savetxt(hcr_path + self.trajectory_title + '.csv', self.trajectory_data, delimiter=',', fmt='%i, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f')
            np.savetxt(hcr_path + self.trajectory_title + '_VISUAL.csv', self.trajectory_data_visual, delimiter=',', fmt='%i, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f', header="Row Name,PosX,PosY,SteeringAngle,Throttle,Brake,Psi", comments='')
            self.module_widget.label_trajectory_filename.setText('Saved file as: '+ self.trajectory_title + '.csv')
            self.module_widget.line_trajectory_title.clear()
            self.module_widget.btn_save.setEnabled(False)
            self.module_widget.btn_discard.setEnabled(False)
            self.module_widget.line_trajectory_title.setEnabled(False)
            self.module_widget.check_trajectory.setEnabled(False)
            self.module_widget.check_trajectory.setChecked(False)
        except Exception as inst:
            print(inst)
            self.module_widget.label_trajectory_filename.setText('Could not save File please try again')
            self.module_widget.btn_save.setEnabled(True)
            self.module_widget.btn_discard.setEnabled(True)
            self.module_widget.line_trajectory_title.setEnabled(True)
            self.module_widget.check_trajectory.setEnabled(True)
            self.module_widget.check_trajectory.setChecked(True)

        

    def discard_trajectory(self):
        self.module_action.trajectory_recorder.discard_current_trajectory()
        self.module_widget.label_trajectory_filename.setText('Discarded trajectory')
        self.module_widget.line_trajectory_title.clear()
        self.module_widget.btn_save.setEnabled(False)
        self.module_widget.btn_discard.setEnabled(False)
        self.module_widget.line_trajectory_title.setEnabled(False)
        self.module_widget.check_trajectory.setEnabled(False)
        self.module_widget.check_trajectory.setChecked(False)


    def handle_module_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            state_as_state = self.module_action.module_state_handler.get_state(state)  # ensure we have the State object (not the int)

            if state_as_state == DatarecorderStates.DATARECORDER.INITIALIZED:
                self.state_widget.btn_start.setEnabled(True)
                self.module_widget.check_trajectory.setEnabled(True)
                self.module_widget.lbl_data_filename.setText(self.module_action.get_filename())
                self.module_widget.label_trajectory_filename.setText('')
                if self.module_widget.check_trajectory.isChecked() is False:
                    self.module_widget.btn_save.setEnabled(False)
                    self.module_widget.btn_discard.setEnabled(False)
                    self.module_widget.line_trajectory_title.setEnabled(False)

            if state_as_state == DatarecorderStates.DATARECORDER.NOTINITIALIZED:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(False)
                self.module_widget.check_trajectory.setEnabled(False)
                self.module_widget.btn_save.setEnabled(False)
                self.module_widget.btn_discard.setEnabled(False)
                self.module_widget.line_trajectory_title.setEnabled(False)

            if state_as_state == DatarecorderStates.DATARECORDER.START:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(True)
                self.module_widget.btn_initialize.setEnabled(False)
                self.module_widget.check_trajectory.setEnabled(False)
                self.module_widget.btn_save.setEnabled(False)
                self.module_widget.btn_discard.setEnabled(False)
                self.module_widget.line_trajectory_title.setEnabled(False)

                # set message text
                self.module_widget.lbl_message_recorder.setText("Busy Recording ...")
                self.module_widget.lbl_message_recorder.setStyleSheet('color: red')

            if state_as_state == DatarecorderStates.DATARECORDER.STOP:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(False)
                self.module_widget.btn_initialize.setEnabled(True)
                if self.module_widget.check_trajectory.isChecked():
                    self.module_widget.btn_save.setEnabled(True)
                    self.module_widget.btn_discard.setEnabled(True)
                    self.module_widget.line_trajectory_title.setEnabled(True)
                    self.check_trajectory_filename()

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
