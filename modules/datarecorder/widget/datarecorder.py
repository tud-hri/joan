from process import Control
import os
from PyQt5 import QtCore
from modules.datarecorder.action.states import DatarecorderStates
from modules.datarecorder.action.datarecorder import DatarecorderAction
#from modules.datarecorder.action.datarecordersettings import DatarecorderSettings

# for editWidgets
from PyQt5 import QtWidgets, QtGui
from functools import partial


class DeprecatedDatarecorderWidget(Control):
    """
    DatarecorderWidget
    """

    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 200
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)

        self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "datarecorder.ui"))
        self.create_settings(module=self, file=os.path.join(os.path.dirname(os.path.realpath(__file__)), "datarecordersettings.json"))
        self.settings = self.get_module_settings(module='modules.datarecorder.widget.datarecorder.DatarecorderWidget')

        self.data = {}
        self.write_news(channel=self, news=self.data)
        
        self.millis = kwargs['millis']

        # creating a self.module_state_handler which also has the module_states in self.module_state_handler.states
        self.define_module_state_handler(module=self, module_states=DatarecorderStates())
        self.module_state_handler.state_changed.connect(self.handle_module_state)
        self.master_state_handler.state_changed.connect(self.handle_master_state)

        try:
            self.action = DatarecorderAction()
            #self.action = DatarecorderAction(self.settings)
        except Exception as inst:
            print('De error bij de constructor van de widget is:    ', inst)

        #self.settings = DatarecorderSettings()

    def do(self):
        # handling is done in the action part
        self.action.write()

    def editWidget(self):
        try:
            layout = self.widget.verticalLayout_items

            content = QtWidgets.QWidget()
            vlay = QtWidgets.QVBoxLayout(content)

            # cleanup previous widgets from scroll area
            for i in reversed(range(vlay.count())):
                marked_widget = vlay.takeAt(i).widget()
                vlay.removeWidget(marked_widget)
                marked_widget.setParent(None)
            # cleanup previous widgets from verticalLayout_items
            for i in reversed(range(layout.count())):
                marked_widget = layout.takeAt(i).widget()
                layout.removeWidget(marked_widget)
                marked_widget.setParent(None)

            scroll = QtWidgets.QScrollArea()
            layout.addWidget(scroll)
            scroll.setWidget(content)
            scroll.setWidgetResizable(True)

            label_font = QtGui.QFont()
            label_font.setPointSize(12)
            item_font = QtGui.QFont()
            item_font.setPointSize(10)
            news_checkbox = {}
            module_key = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
            item_widget = {}

            current_settings = self.settings and self.settings.read() or {'data': {}}
            for channel in self.get_available_news_channels():
                if channel != module_key:
                    if channel not in current_settings['data'].keys():
                        current_settings['data'].update({channel: {}})
                    news_checkbox[channel] = QtWidgets.QLabel(channel.split('.')[1])
                    news_checkbox[channel].setFont(label_font)
                    news = self.read_news(channel)
                    if news:
                        vlay.addWidget(news_checkbox[channel])

                        for item in news:
                            item_widget[item] = QtWidgets.QCheckBox(item)
                            item_widget[item].setFont(item_font)
                            # lambda will not deliver what you expect:
                            # item_widget[item].clicked.connect(lambda:
                            #                                  self.handlemodulesettings(item_widget[item].text(),
                            #                                  item_widget[item].isChecked()))
                            item_widget[item].stateChanged.connect(
                                partial(self.handlemodulesettings, channel, item_widget[item])
                            )
                            vlay.addWidget(item_widget[item])

                            # start set checkboxes from current_settings
                            if item not in current_settings['data'][channel].keys():
                                item_widget[item].setChecked(True)
                                item_widget[item].stateChanged.emit(True)
                            else:
                                item_widget[item].setChecked(current_settings['data'][channel][item])
                                item_widget[item].stateChanged.emit(current_settings['data'][channel][item])
                            # end set checkboxes from current_settings

            vlay.addStretch()

            content.adjustSize()
            self.window.main_widget.adjustSize()
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
        self.module_state_handler.request_state_change(self.module_states.DATARECORDER.NOTINITIALIZED)

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
        self.module_state_handler.request_state_change(self.module_states.DATARECORDER.START)
        self.action.start()
        self.startPulsar()

    def stop(self):
        self.module_state_handler.request_state_change(self.module_states.DATARECORDER.STOP)
        print('stop in datarecorder')
        self.stopPulsar()
        self.action.stop()

    def _close(self):
        self.module_state_handler.request_state_change(self.module_states.DATARECORDER.STOP)
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
        self.module_state_handler.request_state_change(self.module_states.DATARECORDER.INITIALIZING)
        if self.action.initialize():
            self.module_state_handler.request_state_change(self.module_states.DATARECORDER.INITIALIZED)
