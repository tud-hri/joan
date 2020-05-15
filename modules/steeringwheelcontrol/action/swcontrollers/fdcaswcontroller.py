import os

import pandas as pd

from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes
from .baseswcontroller import BaseSWController

class FDCASWController(BaseSWController):

    def __init__(self, module_action):
        super().__init__(controller_type=SWContollerTypes.FDCA_SWCONTROLLER, module_action=module_action)

        # Initialize local Variables
        self._hcr_list = []
        self._hcr = []
        self._t_lookahead_feedforward = 0.0
        self._k_y = 0.1
        self._k_psi = 0.4
        self._lohs = 1.0
        self._sohf = 1.0
        self._loha = 0.0

        self._current_hcr_name = ''
        self._path_hcr_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'hcr_trajectories')
        self.update_hcr_trajectory_list()

        # connect widgets
        self._controller_tab.btn_apply.clicked.connect(self.get_set_parameter_values_from_ui)
        self._controller_tab.btn_reset.clicked.connect(self.set_default_parameter_values)
        self._controller_tab.slider_loha.valueChanged.connect(
            lambda: self._controller_tab.lbl_loha.setText(str(self._controller_tab.slider_loha.value()/100.0))
        )
        self._controller_tab.btn_update_hcr_list.clicked.connect(self.update_hcr_trajectory_list)

        self.set_default_parameter_values()

    def do(self, data_in):
        """In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero"""
        self.data_out['sw_torque'] = 0.0

    def set_default_parameter_values(self):
        """set the default controller parameters
        In the near future, this should be from the controller settings class
        """

        # default values
        self._t_lookahead_feedforward = 0.0
        self._k_y = 0.1
        self._k_psi = 0.4
        self._lohs = 1.0
        self._sohf = 1.0
        self._loha = 0.25

        self.update_ui()

        self.get_set_parameter_values_from_ui()

        # load the default HCR
        self._current_hcr_name = 'default_hcr_trajectory.csv'
        self.update_hcr_trajectory_list()
        self.load_hcr()

    def get_set_parameter_values_from_ui(self):
        """update controller parameters from ui"""

        self._k_y = float(self._controller_tab.edit_k_y.text())
        self._k_psi = float(self._controller_tab.edit_k_psi.text())
        self._lohs = float(self._controller_tab.edit_lohs.text())
        self._sohf = float(self._controller_tab.edit_sohf.text())
        self._loha = self._controller_tab.slider_loha.value() / 100

        self.load_hcr()

        self.update_ui()

    def update_ui(self):
        """update the labels and line edits in the controller_tab with the latest values"""

        self._controller_tab.edit_k_y.setText(str(self._k_y))
        self._controller_tab.edit_k_psi.setText(str(self._k_psi))
        self._controller_tab.edit_lohs.setText(str(self._lohs))
        self._controller_tab.edit_sohf.setText(str(self._sohf))
        self._controller_tab.slider_loha.setValue(self._loha*100)

        # update the current controller settings
        self._controller_tab.lbl_k_y.setText(str(self._k_y))
        self._controller_tab.lbl_k_psi.setText(str(self._k_psi))
        self._controller_tab.lbl_lohs.setText(str(self._lohs))
        self._controller_tab.lbl_sohf.setText(str(self._sohf))

    def load_hcr(self):
        """new HCR selected"""
        fname = self._controller_tab.cmbbox_hcr_selection.itemText(self._controller_tab.cmbbox_hcr_selection.currentIndex())

        if fname != self._current_hcr_name:
            # fname is different from _current_hcr_name, load it!
            try:
                tmp = pd.read_csv(os.path.join(self._path_hcr_directory, fname))
                self._hcr = tmp.values
                self._current_hcr_name = fname
            except OSError as err:
                print('Error loading HCR trajectory file: ', err)

    def update_hcr_trajectory_list(self):
        # get list of csv files in directory
        files = [filename for filename in os.listdir(self._path_hcr_directory) if filename.endswith('csv')]

        self._controller_tab.cmbbox_hcr_selection.clear()
        self._controller_tab.cmbbox_hcr_selection.addItems(files)

        idx = self._controller_tab.cmbbox_hcr_selection.findText(self._current_hcr_name)
        if idx != -1:
            self._controller_tab.cmbbox_hcr_selection.setCurrentIndex(idx)
