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
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"trajectoryrecorder.ui"))
        
        self.data = {}
        self.writeNews(channel=self, news=self.data)
        self.counter = 0


        self.defineModuleStateHandler(module=self, moduleStates=TrajectoryrecorderStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)

        try:
            self.action = TrajectoryrecorderAction(moduleStates = self.moduleStates,
                                          moduleStateHandler = self.moduleStateHandler)
        except Exception as inst:
            print('De error bij de constructor van de widget is:    ', inst)

        self.Siminterface = self.getModuleStatePackage('modules.siminterface.widget.siminterface.SiminterfaceWidget')
        
        self.widget.btnStartrecord.setEnabled(True)
        self.widget.btnStoprecord.setEnabled(False)
        self.widget.btnSavetrajectory.setEnabled(False)
        self.widget.lineTrajectoryname.setEnabled(False)

        self.widget.btnStartrecord.clicked.connect(self.start)
        self.widget.btnStoprecord.clicked.connect(self.stop)
        self.widget.btnSavetrajectory.clicked.connect(self.savefiles)
        self.widget.lineTrajectoryname.textEdited.connect(self.checkfilename)
        

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data = self.readNews('modules.siminterface.widget.siminterface.SiminterfaceWidget')
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
        if(self.Siminterface['moduleStateHandler'].state == self.Siminterface['moduleStates'].SIMULATION.RUNNING): 
            self.mainwidget.show()
        



    def start(self):
        if(self.Siminterface['moduleStateHandler'].state == self.Siminterface['moduleStates'].SIMULATION.RUNNING): 
            self.startPulsar()
            self.widget.btnStartrecord.setEnabled(False)
            self.widget.btnSavetrajectory.setEnabled(False)
            self.widget.lineTrajectoryname.setEnabled(False)
            self.widget.btnStoprecord.setEnabled(True)


    def stop(self):
            self.stopPulsar()
            self.widget.btnStoprecord.setEnabled(False)
            self.Trajectory = self.action.generate()
            self.widget.lineTrajectoryname.setEnabled(True)
            self.widget.lblModulestate.setText('Please enter a valid Filename for Trajectory')

    def checkfilename(self):
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        HCRPath = os.path.join(path,'feedbackcontroller/action/HCRTrajectories/*.csv')  #Dit moet handiger kunnen
        
        self.TrajectoryName = self.widget.lineTrajectoryname.text()
        

        for fname in glob.glob(HCRPath):
            if (self.TrajectoryName == (os.path.basename(fname)[:-4]) or self.TrajectoryName == ''):
                self.widget.lblModulestate.setText('Filename Invalid! (empty or already exists)')
                self.widget.btnSavetrajectory.setEnabled(False)
                break
            else:
                self.widget.btnSavetrajectory.setEnabled(True)
                self.widget.lblModulestate.setText('Will save file as: '+ self.TrajectoryName + '.csv')




    def savefiles(self):
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        HCRPath = os.path.join(path,'feedbackcontroller/action/HCRTrajectories/')  #Dit moet handiger kunnen

        	
        # Save 2D numpy array to csv file
        try:
            np.savetxt(HCRPath + self.TrajectoryName + '.csv', self.Trajectory, delimiter=',', fmt='%d')
            self.widget.lblModulestate.setText('Saved trajectory as: '+ self.TrajectoryName + '.csv')
            self.widget.lineTrajectoryname.clear()
            self.widget.lineTrajectoryname.setEnabled(False)
            self.widget.btnSavetrajectory.setEnabled(False)
            self.widget.btnStartrecord.setEnabled(True)
        except:
            self.widget.lblModulestate.setText('Could not save File please try again')
            self.widget.btnSavetrajectory.setEnabled(True)
            self.widget.btnStartrecord.setEnabled(False)





        


    def _close(self):
        if(self.Siminterface['moduleStateHandler'].state != self.Siminterface['moduleStates'].SIMULATION.RUNNING): 
            self.mainwidget.close()

    def handlemasterstate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.masterStateHandler.getState(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self._stop()

            # update the state label
            self.widget.lblState.setText(str(stateAsState))

        except Exception as inst:
            print (inst)

    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.moduleStateHandler.getState(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self._stop()

            # update the state label
            self.widget.lblModulestate.setText(str(stateAsState.name))

        except Exception as inst:
            print (inst)
