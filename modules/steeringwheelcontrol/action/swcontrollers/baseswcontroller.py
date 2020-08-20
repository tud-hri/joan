import abc
import os

import numpy as np
import pandas as pd
from PyQt5 import uic

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes


class BaseSWController:
    def __init__(self, controller_type: SWControllerTypes, module_action: JOANModules):
        self._action = module_action
        self._controller_type = controller_type

        # widget
        self._tuning_tab = uic.loadUi(self._controller_type.tuning_ui_file)
        self._controller_tab = uic.loadUi(self._controller_type.controller_tab_ui_file)

        # widget actions
        self._controller_tab.btn_remove_sw_controller.clicked.connect(self.remove_sw_controller)

        # trajectory
        self._trajectory = []
        self._current_trajectory_name = ''
        self._path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')

        self._data_in = {}
        self._data_out = {'sw_torque': 0}

    @abc.abstractmethod
    def calculate(self, vehicle_object, hw_data_in):
        """
        Calculate SW control torque
        :param vehicle_object: data from the vehicle
        :param hw_data_in: data from the hardware
        :return: dict, including sw_torque
        """
        return self._data_out

    def remove_sw_controller(self):
        """
        Remove the sw controller
        """
        self.module_action.remove_controller(self)

    def load_trajectory(self):
        """Load HCR trajectory"""
        try:

            tmp = pd.read_csv(os.path.join(self._path_trajectory_directory, self.settings.trajectory_name))
            if np.array_equal(tmp.values, self._trajectory):
                print('trajectory already loaded')
            else:
                self._trajectory = tmp.values
                print('loaded')
            # TODO We might want to do some checks on the trajectory here.
            # self.trajectory_name = fname
        except OSError as err:
                print('Error loading HCR trajectory file: ', err)

    def checkEqual(lst):
        return lst[1:] == lst[:-1]

    def update_trajectory_list(self):
        """
        Check what trajectory files are present and update the selection list
        """
        # get list of csv files in directory
        if not os.path.isdir(self._path_trajectory_directory):
            os.mkdir(self._path_trajectory_directory)
        files = [filename for filename in os.listdir(self._path_trajectory_directory) if filename.endswith('csv')]

        self.settings_dialog.cmbbox_hcr_selection.clear()
        self.settings_dialog.cmbbox_hcr_selection.addItems(files)

        idx = self.settings_dialog.cmbbox_hcr_selection.findText(self._current_trajectory_name)
        if idx != -1:
            self.settings_dialog.cmbbox_hcr_selection.setCurrentIndex(idx)

    def find_closest_node(self, node, nodes):
        """
        Find the node in the nodes list (trajectory)
        """
        nodes = np.asarray(nodes)
        deltas = nodes - node
        dist_squared = np.einsum('ij,ij->i', deltas, deltas)
        return np.argmin(dist_squared)

    @property
    def get_controller_tab(self):
        return self._controller_tab

    def get_tuning_tab(self):
        return self._tuning_tab

    @property
    def name(self):
        return str(self._controller_type)

    @property
    def controller_type(self):
        return self._controller_type
