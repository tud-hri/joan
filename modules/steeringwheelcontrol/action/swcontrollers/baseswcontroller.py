import abc
import os

import pandas as pd
import numpy as np
import math

from PyQt5 import uic

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes


class BaseSWController:
    def __init__(self, controller_type: SWContollerTypes, module_action: JOANModules):
        self._action = module_action
        self._controller_type = controller_type

        # widget
        self._controller_tab = uic.loadUi(self._controller_type.tab_ui_file)

        # trajectory
        self._trajectory = []
        self._current_trajectory_name = ''
        self._path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')

        self._data_in = {}
        self._data_out = {}
        self._data_out['sw_torque'] = 0

    @abc.abstractmethod
    def do(self, data_in):
        """do is called every tick in steeringwheelcontrolaction's do
        this needs to be implemented by children of BaseSWController
        """
        return self._data_out

    def load_trajectory(self):
        """Load HCR trajectory"""
        fname = self._controller_tab.cmbbox_hcr_selection.itemText(
            self._controller_tab.cmbbox_hcr_selection.currentIndex()
        )

        if fname != self._current_trajectory_name:
            # fname is different from _current_hcr_name, load it!
            try:
                tmp = pd.read_csv(os.path.join(self._path_trajectory_directory, fname))
                self._trajectory = tmp.values
                # TODO We might want to do some checks on the trajectory here.
                self._current_trajectory_name = fname
            except OSError as err:
                print('Error loading HCR trajectory file: ', err)

    def update_trajectory_list(self):
        """Check what trajectory files are present and update the selection list"""
        # get list of csv files in directory
        if not os.path.isdir(self._path_trajectory_directory):
            os.mkdir(self._path_trajectory_directory)
        files = [filename for filename in os.listdir(self._path_trajectory_directory) if filename.endswith('csv')]

        self._controller_tab.cmbbox_hcr_selection.clear()
        self._controller_tab.cmbbox_hcr_selection.addItems(files)

        idx = self._controller_tab.cmbbox_hcr_selection.findText(self._current_trajectory_name)
        if idx != -1:
            self._controller_tab.cmbbox_hcr_selection.setCurrentIndex(idx)

    def find_closest_node(self, node, nodes):
        """find the node in the nodes list (trajectory)"""
        nodes = np.asarray(nodes)
        deltas = nodes - node
        dist_squared = np.einsum('ij,ij->i', deltas, deltas)
        return np.argmin(dist_squared)

    @property
    def get_controller_tab(self):
        return self._controller_tab

    @property
    def name(self):
        return str(self._controller_type)

    @property
    def controller_type(self):
        return self._controller_type

