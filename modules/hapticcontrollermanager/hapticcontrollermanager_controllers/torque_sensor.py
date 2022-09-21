import math
import os

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic

from core.statesenum import State

from tools import LowPassFilterBiquad
from tools.haptic_controller_tools import find_closest_node

class TorqueSensor:
    def __init__(self):
        self.frequency = 100
        self._bq_filter_rate = LowPassFilterBiquad(fc=15, fs=self.frequency)

        # Observer dynamics
        self.damping = 0.25
        self.stiffness = 0.4
        self.inertia = 0.050542488894956494
        self.observer_matrix = 8 * np.array([[2, 0], [0, 2]])
        self.alpha = 2.5
        self.kappa = 1
        self.estimated_human_torque = 0.0
        self.x_hat = np.array([[0.0], [0.0]])
        self._old_steering_angle = 0

    def estimate_human_torque(self, steering_angle, torque, timestep):
        steering_state = self._compute_steering_states(steering_angle, timestep)
        nonlinear_component = self._compute_nonlinear_torques(steering_state)
        self._estimate_human_control(steering_state, torque, timestep)
        return self.estimated_human_torque, nonlinear_component

    def _compute_steering_states(self, steering_angle, timestep):
        # Compute steering wheel states, mainly just steering rate
        unfiltered_steering_rate = (steering_angle - self._old_steering_angle) / timestep
        steering_rate = self._bq_filter_rate.step(unfiltered_steering_rate)
        steering_state = np.array([[steering_angle], [steering_rate]])
        self._old_steering_angle = steering_angle
        return steering_state

    def _system_matrices(self):
        # Compute system matrices from steering wheel parameters
        A = np.array([[0, 1], [- self.stiffness / self.inertia, - self.damping / self.inertia]])
        B = np.array([[0], [1 / self.inertia]])
        return A, B

    def _estimate_human_control(self, steering_state, torque, delta_t):
        # Compose states
        A, B = self._system_matrices()
        x = steering_state
        xi_tilde = self.x_hat - x
        x_hat_dot = np.matmul(A, self.x_hat) + B * (torque + self.estimated_human_torque) - np.matmul(self.observer_matrix, xi_tilde)
        self.estimated_human_torque += - self.alpha * np.matmul(xi_tilde.transpose(), B) * delta_t
        self.x_hat += x_hat_dot * delta_t
        return self.estimated_human_torque

    def _compute_nonlinear_torques(self, x):
        """
        This function is used to do feedforward compensation of nonlinear torques due to gravity and friction, to use a linear system for computing human input torques.
            inputs
                x (np.array): System states composed of steering angle and steering rate

            outputs
                nonlinear_torques (float): output torque composed of gravity and friction torque.
        """
        g = 9.81
        m = 0.498970137272351
        dl = 0.008146703214514241
        dh = 0.042651190037657924
        vt = 0.2991305651849728
        vsp = 2 * vt
        tau_d = -0.08720280979209796
        tau_fric = 0.023387092205098114

        # Gravity
        tau_g = - m * g * dh * np.sin(x[0]) - m * g * dl * np.cos(x[0])

        # Friction
        v = x[1]
        gv = v / vsp * np.exp(-(v / (np.sqrt(2) * vsp)) ** 2 + 1 / 2)
        fc = tau_d * np.tanh(v / vt)
        tau_f = gv * tau_fric + fc
        nonlinear_torques = tau_f + tau_g
        return nonlinear_torques