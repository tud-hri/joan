from process import Control
import os
from PyQt5 import QtCore
from modules.datarecorder.action.states import DatarecorderStates
from modules.datarecorder.action.datarecorder import DatarecorderAction
from modules.datarecorder.action.datarecordersettings import DatarecorderSettings

# for editWidgets
from PyQt5 import QtWidgets, QtGui
from functools import partial


class DatarecorderWidget(Control):
    """
    DatarecorderWidget
    """

    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 200
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)

        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "datarecorder.ui"))
        self.data = {}
        self.writeNews(channel=self, news=self.data)

        self.millis = kwargs['millis']

        # creating a self.moduleStateHandler which also has the moduleStates in self.moduleStateHandler.states
        self.defineModuleStateHandler(module=self, moduleStates=DatarecorderStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)

        try:
            self.action = DatarecorderAction()
        except Exception as inst:
            print('De error bij de constructor van de widget is:    ', inst)

        self.settings = DatarecorderSettings()

    def do(self):
        # handling is done in the action part
        self.action.write()

    def editWidget(self):
        currentSettings = self.settings.read()
        try:
            layout = self.widget.verticalLayout_items

            content = QtWidgets.QWidget()
            vlay = QtWidgets.QVBoxLayout(content)

            # cleanup previous widgets from scroll area
            for i in reversed(range(vlay.count())):
                markedWidget = vlay.takeAt(i).widget()
                vlay.removeWidget(markedWidget)
                markedWidget.setParent(None)
            # cleanup previous widgets from verticalLayout_items
            for i in reversed(range(layout.count())):
                markedWidget = layout.takeAt(i).widget()
                layout.removeWidget(markedWidget)
                markedWidget.setParent(None)

            scroll = QtWidgets.QScrollArea()
            layout.addWidget(scroll)
            scroll.setWidget(content)
            scroll.setWidgetResizable(True)

            labelFont = QtGui.QFont()
            labelFont.setPointSize(12)
            itemFont = QtGui.QFont()
            itemFont.setPointSize(10)
            newsCheckbox = {}
            moduleKey = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
            itemWidget = {}
            for channel in self.getAvailableNewsChannels():
                if channel != moduleKey:
                    if channel not in currentSettings['modules'].keys():
                        currentSettings['modules'].update({channel: {}})
                    newsCheckbox[channel] = QtWidgets.QLabel(channel.split('.')[1])
                    newsCheckbox[channel].setFont(labelFont)
                    news = self.readNews(channel)
                    if news:
                        vlay.addWidget(newsCheckbox[channel])

                        for item in news:
                            itemWidget[item] = QtWidgets.QCheckBox(item)
                            itemWidget[item].setFont(itemFont)
                            # lambda will not deliver what you expect:
                            # itemWidget[item].clicked.connect(lambda:
                            #                                  self.handlemodulesettings(itemWidget[item].text(),
                            #                                  itemWidget[item].isChecked()))
                            itemWidget[item].stateChanged.connect(partial(self.handlemodulesettings,
                                                                          channel,
                                                                          itemWidget[item]))
                            vlay.addWidget(itemWidget[item])

                            # start set checkboxes from currentSettings
                            if item not in currentSettings['modules'][channel].keys():
                                itemWidget[item].setChecked(True)
                                itemWidget[item].stateChanged.emit(True)
                            else:
                                itemWidget[item].setChecked(currentSettings['modules'][channel][item])
                                itemWidget[item].stateChanged.emit(currentSettings['modules'][channel][item])
                            # end set checkboxes from currentSettings

            vlay.addStretch()

            content.adjustSize()
            self.window.mainWidget.adjustSize()
        except Exception as inst:
            print(inst)

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except Exception:
            pass

    def _show(self):
        self.window.show()
        self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.NOTINITIALIZED)

        # connect buttons
        self.widget.btnInitialize.clicked.connect(self._clickedBtnInitialize)

        # set current data file name
        self.widget.lblDataFilename.setText("< none >")

        # set message text
        self.widget.lblMessageRecorder.setText("not recording")
        self.widget.lblMessageRecorder.setStyleSheet('color: orange')

        # reads settings if available and expands the datarecorder widget
        try:
            for y in self.getAvailableModuleStatePackages():
                print(y)
            self.editWidget()
        except Exception as inst:
            print(inst)

    def start(self):
        print('start in datarecorder')
        if not self.window.isVisible():
            self._show()
        self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.START)
        self.action.start()
        self.startPulsar()

    def stop(self):
        self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.STOP)
        print('stop in datarecorder')
        self.stopPulsar()
        self.action.stop()

    def _close(self):
        self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.STOP)
        if self.window.isVisible():
            self.window.close()

    def handlemodulesettings(self, moduleKey, item):
        try:
            datarecorderSettings = DatarecorderSettings()
            datarecorderSettings.write(moduleKey=moduleKey, item=item)
        except Exception as inst:
            print(inst)

    def handlemodulestate(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            stateAsState = self.moduleStateHandler.getState(state)  # ensure we have the State object (not the int)

            if stateAsState == self.moduleStates.DATARECORDER.INITIALIZED:
                self.stateWidget.btnStart.setEnabled(True)
                self.widget.lblDataFilename.setText(self.action.getFilename())

            if stateAsState == self.moduleStates.DATARECORDER.NOTINITIALIZED:
                self.stateWidget.btnStart.setEnabled(False)
                self.stateWidget.btnStop.setEnabled(False)

            if stateAsState == self.moduleStates.DATARECORDER.START:
                self.stateWidget.btnStart.setEnabled(False)
                self.stateWidget.btnStop.setEnabled(True)
                self.widget.btnInitialize.setEnabled(False)

                # set message text
                self.widget.lblMessageRecorder.setText("Busy Recording ...")
                self.widget.lblMessageRecorder.setStyleSheet('color: red')

            if stateAsState == self.moduleStates.DATARECORDER.STOP:
                self.stateWidget.btnStart.setEnabled(False)
                self.stateWidget.btnStop.setEnabled(False)
                self.widget.btnInitialize.setEnabled(True)

                # set message text
                self.widget.lblMessageRecorder.setText("not recording")
                self.widget.lblMessageRecorder.setStyleSheet('color: orange')

            # update the state label
            self.stateWidget.lblModulestate.setText(stateAsState.name)
            self.widget.repaint()

            if stateAsState == self.moduleStates.DATARECORDER.START:
                self.stateWidget.btnStart.setStyleSheet("background-color: green")
            else:
                self.stateWidget.btnStart.setStyleSheet("background-color: none")

        except Exception as inst:
            print(inst)

    def handlemasterstate(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            stateAsState = self.masterStateHandler.getState(state)  # ensure we have the State object (not the int)

            # emergency stop
            if stateAsState == self.masterStates.ERROR:
                self.stop()
                self.widget.btnInitialize.setEnabled(True)

            # update the state label
            self.stateWidget.lblModulestate.setText(stateAsState.name)
            self.widget.repaint()

        except Exception as inst:
            print(inst)

    def _clickedBtnInitialize(self):
        """initialize the data recorder (mainly setting the data directory and data file prefix"""
        self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.INITIALIZING)
        if self.action.initialize():
            self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.INITIALIZED)
