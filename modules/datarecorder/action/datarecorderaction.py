from datetime import datetime
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from modules.datarecorder.action.states import DatarecorderStates
from modules.datarecorder.action.datawriter import DataWriter
from process.settings import ModuleSettings

# for editWidgets
from PyQt5 import QtWidgets, QtGui
from functools import partial
import os

class DatarecorderAction(JoanModuleAction):
    def __init__(self, millis=200):
        super().__init__(module=JOANModules.DATA_RECORDER, millis=millis)
    #def __init__(self, master_state_handler, millis=200):
    #    super().__init__(module=JOANModules.DATA_RECORDER, master_state_handler=master_state_handler, millis=millis)


        self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.NOTINITIALIZED)

        # next three Template lines are not used for datarecorder' 
        # 1. self.data['t'] = 0
        # 2. self.write_news(news=self.data)
        # 3. self.time = QtCore.QTime()
        

        # start settings for this module
        self.settings_object = ModuleSettings(file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'datarecordersettings.json'))
        self.settings = self.settings_object.read_settings()
        self.item_dict = {}

        self.settings_object.write_settings(group_key=JOANModules.DATA_RECORDER.name, item=self.item_dict)
        
        self.update_settings(self.settings)
        # end settings for this module

        self.filename = ''
        self.data_writer = DataWriter(news=self.get_all_news(), channels=self.get_available_news_channels(), settings=self.get_module_settings(JOANModules.DATA_RECORDER))

    def initialize_file(self):
        self.initialize()
        self.filename = self._create_filename(extension='csv')
        return True


    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        self._write()
        
        # next two Template lines are not used for datarecorder
        # 1. self.data['t'] = self.time.elapsed()
        # 2. self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        try:
            self.module_state_handler.request_state_change(DatarecorderStates.INIT.INITIALIZING)
        except RuntimeError:
            return False
        return True

    def stop(self):
        """
        Close the threaded filehandle(s)
        """
        super().stop()
        self.data_writer.close()
        self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.STOP)

    def start(self):
        self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.START)
        self.data_writer.open(filename=self.get_filename())
        super().start()

    def _write(self):
        now = datetime.now()
        self.data_writer.write(timestamp=now, news=self.get_all_news(), channels=self.get_available_news_channels())

    def _create_filename(self, extension=''):
        now = datetime.now()
        now_string = now.strftime('%Y%m%d_%H%M%S')
        filename = '%s_%s' % ('data', now_string)
        if extension != '':
            extension = extension[0] == '.' or '.%s' % extension
            filename = '%s%s' % (filename, extension)
        return filename

    def get_filename(self):
        return self.filename

    def _editWidget(self, layout=None):
        try:

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
            #module_key = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
            module_key = JOANModules.DATA_RECORDER
            item_widget = {}

            current_settings = self.settings_object and self.settings_object.read_settings() or {'data': {}}

            for channel in self.get_available_news_channels():
                if channel != module_key:
                    if channel.name not in current_settings['data'].keys():
                        current_settings['data'].update({channel.name: {}})
                    #news_checkbox[channel] = QtWidgets.QLabel(channel.split('.')[1])
                    news_checkbox[channel.name] = QtWidgets.QLabel(channel.name)
                    news_checkbox[channel.name].setFont(label_font)
                    news = self.read_news(channel)
                    if news:
                        vlay.addWidget(news_checkbox[channel.name])

                        for item in news:
                            item_widget[item] = QtWidgets.QCheckBox(item)
                            item_widget[item].setFont(item_font)
                            # lambda will not deliver what you expect:
                            # item_widget[item].clicked.connect(lambda:
                            #                                  self.handlemodulesettings(item_widget[item].text(),
                            #                                  item_widget[item].isChecked()))
                            item_widget[item].stateChanged.connect(
                                partial(self.handlemodulesettings, channel.name, item_widget[item])
                            )
                            vlay.addWidget(item_widget[item])

                            # start set checkboxes from current_settings
                            if item not in current_settings['data'][channel.name].keys():
                                item_widget[item].setChecked(True)
                                item_widget[item].stateChanged.emit(True)
                            else:
                                item_widget[item].setChecked(current_settings['data'][channel.name][item])
                                item_widget[item].stateChanged.emit(current_settings['data'][channel.name][item])
                            # end set checkboxes from current_settings

            vlay.addStretch()

            content.adjustSize()
        except Exception as inst:
            print(inst)

    def handlemodulesettings(self, module_key, item):
        try:
            item_dict = {}
            item_dict[item.text()] = item.isChecked()
            # self.get_available_news_channels() means only modules with news will be there in the datarecorder_settings file
            self.settings_object.write_settings(group_key=module_key, item=item_dict, filter=self.get_available_news_channels())
        except Exception as inst:
            print(inst)

    def _clicked_btn_initialize(self):
        """initialize the data recorder (mainly setting the data directory and data file prefix"""
        self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.INITIALIZING)
        if self.initialize_file():
            self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.INITIALIZED)
 