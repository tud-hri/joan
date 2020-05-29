from process import Control, State, translate
from PyQt5 import QtCore
import os, glob
from modules.trajectoryrecorder.action.trajectoryrecorder import TrajectoryrecorderAction
from modules.trajectoryrecorder.action.states import TrajectoryrecorderStates
import numpy as np

class TrajectoryrecorderWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 500
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"trajectoryrecorder.ui"))
        
        self.data = {}
        self.write_news(channel=self, news=self.data)
        self.counter = 0


        self.define_module_state_handler(module=self, module_states=TrajectoryrecorderStates())
        self.module_state_handler.state_changed.connect(self.handle_module_state)
        #self.master_state_handler.state_changed.connect(self.handle_master_state)

        try:
            self.action = TrajectoryrecorderAction(module_states = self.module_states,
                                          module_state_handler = self.module_state_handler)
        except Exception as inst:
            print('De error bij de constructor van de widget is:    ', inst)

        self.Siminterface = self.get_module_state_package('modules.siminterface.widget.siminterface.SiminterfaceWidget')
        
        self.widget.btn_startrecord.setEnabled(True)
        self.widget.btn_stoprecord.setEnabled(False)
        self.widget.btnSavetrajectory.setEnabled(False)
        self.widget.lineTrajectoryname.setEnabled(False)

        self.widget.btn_startrecord.clicked.connect(self.start)
        self.widget.btn_stoprecord.clicked.connect(self.stop)
        self.widget.btnSavetrajectory.clicked.connect(self.savefiles)
        self.widget.lineTrajectoryname.textEdited.connect(self.checkfilename)
        

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data = self.read_news('modules.siminterface.widget.siminterface.SiminterfaceWidget')
        #self.action.process(self.data)
        pass

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        if(self.Siminterface['module_state_handler'].state == self.Siminterface['module_states'].SIMULATION.RUNNING): 
            self.window.show()
        



    def start(self):
        if(self.Siminterface['module_state_handler'].state == self.Siminterface['module_states'].SIMULATION.RUNNING): 
            self.startPulsar()
            self.widget.btn_startrecord.setEnabled(False)
            self.widget.btnSavetrajectory.setEnabled(False)
            self.widget.lineTrajectoryname.setEnabled(False)
            self.widget.btn_stoprecord.setEnabled(True)


    def stop(self):
            self.stopPulsar()
            self.widget.btn_stoprecord.setEnabled(False)
            self.Trajectory = self.action.generate()
            self.widget.lineTrajectoryname.setEnabled(True)
            self.widget.lbl_module_state.setText('Please enter a valid Filename for Trajectory')

    def checkfilename(self):
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        HCRPath = os.path.join(path,'feedbackcontroller/action/HCRTrajectories/*.csv')  #Dit moet handiger kunnen
        
        self.TrajectoryName = self.widget.lineTrajectoryname.text()
        

        for fname in glob.glob(HCRPath):
            if (self.TrajectoryName == (os.path.basename(fname)[:-4]) or self.TrajectoryName == ''):
                self.widget.lbl_module_state.setText('Filename Invalid! (empty or already exists)')
                self.widget.btnSavetrajectory.setEnabled(False)
                break
            else:
                self.widget.btnSavetrajectory.setEnabled(True)
                self.widget.lbl_module_state.setText('Will save file as: '+ self.TrajectoryName + '.csv')




    def savefiles(self):
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        HCRPath = os.path.join(path,'feedbackcontroller/action/HCRTrajectories/')  #Dit moet handiger kunnen

        	
        # Save 2D numpy array to csv file
        try:
            np.savetxt(HCRPath + self.TrajectoryName + '.csv', self.Trajectory, delimiter=',', fmt='%d')
            self.widget.lbl_module_state.setText('Saved trajectory as: '+ self.TrajectoryName + '.csv')
            self.widget.lineTrajectoryname.clear()
            self.widget.lineTrajectoryname.setEnabled(False)
            self.widget.btnSavetrajectory.setEnabled(False)
            self.widget.btn_startrecord.setEnabled(True)
        except:
            self.widget.lbl_module_state.setText('Could not save File please try again')
            self.widget.btnSavetrajectory.setEnabled(True)
            self.widget.btn_startrecord.setEnabled(False)





        


    def _close(self):
        if(self.Siminterface['module_state_handler'].state != self.Siminterface['module_states'].SIMULATION.RUNNING): 
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
            self.widget.lbl_state.setText(str(state_as_state))

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
            self.widget.lbl_module_state.setText(str(state_as_state.name))

        except Exception as inst:
            print (inst)
