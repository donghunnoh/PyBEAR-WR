#!usr/bin/env python

################################################################################
# Copyright 2020 Westwood Robotics Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

__author__ = "Westwood Robotics Corporation"
__email__ = "info@westwoodrobotics.net"
__copyright__ = "Copyright 2020 Westwood Robotics"
__date__ = "Jan. 01, 2020"

__version__ = "0.0.1"
__status__ = "Prototype"

import os

import pdb

import serial

import time

# import Packet
from pybear import Packet

from pybear.CONTROL_TABLE import *


class BEAR(Packet.PKT):
    """
    Provides control of Dynamixel servos using PySerial
    """
    def __init__(self,
                 port = '/dev/ttyUSB0',
                 baudrate = '8000000',
                 bytesize = serial.EIGHTBITS,
                 parity = serial.PARITY_NONE,
                 stopbits = serial.STOPBITS_ONE,
                 timeout = 0.0,
                 bulk_timeout = None,
                 debug = False):
        """
        Constructor for opening up the serial port.
        :param port: Port address; Should be specified per object if using multiple chains
        :param baudrate: Specified baudrate
        """

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.connected = False
        self.motors = {}

        self.ascii_art = True

        self.debug = debug # Option for ease of debugging. Set to false for proper operation.

        super(BEAR, self).__init__(self.port, self.baudrate, bulk_timeout=bulk_timeout)

        self.welcome_msg()

    def welcome_msg(self):
        if self.ascii_art:
            os.system('clear')
            print("==============================================================")
            print("   __        __          _                               _ ")
            print("   \ \      / /___  ___ | |_ __      __ ___    ___    __| | ")
            print("    \ \ /\ / // _ \/ __|| __|\ \ /\ / // _ \  / _ \  / _` | ")
            print("     \ V  V /|  __/\__ \| |_  \ V  V /| (_) || (_) || (_| | ")
            print("      \_/\_/  \___||___/ \__|  \_/\_/  \___/  \___/  \__,_| ")
            print("              ____         _             _    _             ")
            print("             |  _ \  ___  | |__    ___  | |_ (_)  ___  ___  ")
            print("             | |_) |/ _ \ | '_ \  / _ \ | __|| | / __|/ __| ")
            print("             |  _ <| (_) || |_) || (_) || |_ | || (__ \__ \ ")
            print("             |_| \_\\\___/ |_.__/  \___/  \__||_| \___||___/ ")
            print("==============================================================")
            print("=== PyBEAR by Westwood Robotics -- Last Updated 2020.06.29 ===")
            print("==============================================================")

    # =================================================================================================================
    # ===== Configuration Registers

    def get_id(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.ID) for idx in range(len(argv))]

    def set_id(self, *argv):
        self.multi_write_cfg_data(CFG_REG.ID, argv)

    def get_mode(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.MODE) for idx in range(len(argv))]

    def set_mode(self, *argv):
        self.multi_write_cfg_data(CFG_REG.MODE, argv)

    def get_baudrate(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.BAUDRATE) for idx in range(len(argv))]

    def set_baudrate(self, *argv):
        self.multi_write_cfg_data(CFG_REG.BAUDRATE, argv)

    def get_homing_offset(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.HOMING_OFFSET) for idx in range(len(argv))]
    
    def set_homing_offset(self, *argv):
        self.multi_write_cfg_data(CFG_REG.HOMING_OFFSET, argv)

    def get_p_gain_id(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.P_GAIN_ID) for idx in range(len(argv))]

    def set_p_gain_id(self, *argv):
        self.multi_write_cfg_data(CFG_REG.P_GAIN_ID, argv)

    def get_i_gain_id(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.I_GAIN_ID) for idx in range(len(argv))]

    def set_i_gain_id(self,*argv):
        self.multi_write_cfg_data(CFG_REG.I_GAIN_ID, argv)

    def get_d_gain_id(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.D_GAIN_ID) for idx in range(len(argv))]

    def set_d_gain_id(self, *argv):
        self.multi_write_cfg_data(CFG_REG.D_GAIN_ID, argv)

    def get_p_gain_iq(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.P_GAIN_IQ) for idx in range(len(argv))]

    def set_p_gain_iq(self, *argv):
        self.multi_write_cfg_data(CFG_REG.P_GAIN_IQ, argv)

    def get_i_gain_iq(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.I_GAIN_IQ) for idx in range(len(argv))]

    def set_i_gain_iq(self, *argv):
        self.multi_write_cfg_data(CFG_REG.I_GAIN_IQ, argv)

    def get_d_gain_iq(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.D_GAIN_IQ) for idx in range(len(argv))]

    def set_d_gain_iq(self, *argv):
        self.multi_write_cfg_data(CFG_REG.D_GAIN_IQ, argv)

    def get_p_gain_velocity(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.P_GAIN_VEL) for idx in range(len(argv))]

    def set_p_gain_velocity(self, *argv):
        self.multi_write_cfg_data(CFG_REG.P_GAIN_VEL, argv)

    def get_i_gain_velocity(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.I_GAIN_VEL) for idx in range(len(argv))]

    def set_i_gain_velocity(self, *argv):
        self.multi_write_cfg_data(CFG_REG.I_GAIN_VEL, argv)

    def get_d_gain_velocity(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.D_GAIN_VEL) for idx in range(len(argv))]

    def set_d_gain_velocity(self, *argv):
        self.multi_write_cfg_data(CFG_REG.D_GAIN_VEL, argv)

    def get_p_gain_position(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.P_GAIN_POS) for idx in range(len(argv))]

    def set_p_gain_position(self, *argv):
        self.multi_write_cfg_data(CFG_REG.P_GAIN_POS, argv)

    def get_i_gain_position(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.I_GAIN_POS) for idx in range(len(argv))]

    def set_i_gain_position(self, *argv):
        self.multi_write_cfg_data(CFG_REG.I_GAIN_POS, argv)

    def get_d_gain_position(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.D_GAIN_POS) for idx in range(len(argv))]

    def set_d_gain_position(self, *argv):
        self.multi_write_cfg_data(CFG_REG.D_GAIN_POS, argv)

    def get_p_gain_force(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.P_GAIN_FORCE) for idx in range(len(argv))]

    def set_p_gain_force(self, *argv):
        self.multi_write_cfg_data(CFG_REG.P_GAIN_FORCE, argv)

    def get_i_gain_force(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.I_GAIN_FORCE) for idx in range(len(argv))]

    def set_i_gain_force(self, *argv):
        self.multi_write_cfg_data(CFG_REG.I_GAIN_FORCE, argv)

    def get_d_gain_force(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.D_GAIN_FORCE) for idx in range(len(argv))]

    def set_d_gain_force(self, *argv):
        self.multi_write_cfg_data(CFG_REG.D_GAIN_FORCE, argv)

    def get_limit_id_max(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.LIMIT_ID_MAX) for idx in range(len(argv))]

    def set_limit_id_max(self, *argv):
        self.multi_write_cfg_data(CFG_REG.LIMIT_ID_MAX, argv)

    def get_limit_iq_max(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.LIMIT_IQ_MAX) for idx in range(len(argv))]

    def set_limit_iq_max(self, *argv):
        self.multi_write_cfg_data(CFG_REG.LIMIT_IQ_MAX, argv)

    def get_limit_velocity_max(self,*argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.LIMIT_VEL_MAX) for idx in range(len(argv))]

    def set_limit_velocity_max(self, *argv):
        self.multi_write_cfg_data(CFG_REG.LIMIT_VEL_MAX, argv)

    def get_limit_position_min(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.LIMIT_POS_MIN) for idx in range(len(argv))]
    
    def set_limit_position_min(self, *argv):
        self.multi_write_cfg_data(CFG_REG.LIMIT_POS_MIN, argv)
    
    def get_limit_position_max(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.LIMIT_POS_MAX) for idx in range(len(argv))]
    
    def set_limit_position_max(self, *argv):
        self.multi_write_cfg_data(CFG_REG.LIMIT_POS_MAX, argv)

    # Not implemented yet
    # def get_min_voltage(self, m_id):
    #     return self.read_cfg_data(m_id, CFG_REG.MIN_VOLTAGE)
    #
    # def set_min_voltage(self, m_id, val):
    #     self.write_cfg_data(m_id, CFG_REG.MIN_VOLTAGE, val)
    #
    # def get_max_voltage(self, m_id):
    #     return self.read_cfg_data(m_id, CFG_REG.MAX_VOLTAGE)
    #
    # def set_max_voltage(self, m_id, val):
    #     self.write_cfg_data(m_id, CFG_REG.MAX_VOLTAGE, val)

    def get_low_voltage_warning(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.LOW_VOLTAGE_WARNING) for idx in range(len(argv))]

    def set_low_voltage_warning(self, *argv):
        self.multi_write_cfg_data(CFG_REG.LOW_VOLTAGE_WARNING, argv)

    def get_temp_limit_low(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.TEMP_LIMIT_LOW) for idx in range(len(argv))]

    def set_temp_limit_low(self, *argv):
        self.multi_write_cfg_data(CFG_REG.TEMP_LIMIT_LOW, argv)

    def get_temp_limit_high(self, *argv):
        return [self.read_cfg_data(argv[idx], CFG_REG.TEMP_LIMIT_HIGH) for idx in range(len(argv))]

    def set_temp_limit_high(self, *argv):
        self.multi_write_cfg_data(CFG_REG.TEMP_LIMIT_HIGH, argv)

    def get_bulk_config(self, *argv):
        return [self.read_bulk_cfg_data(argv[idx]) for idx in range(len(argv))]

    def set_bulk_config(self, *argv):
        self.multi_write_bulk_cfg_data(argv)


    # =================================================================================================================
    # ===== Status Registers
    def get_torque_enable(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.TORQUE_ENABLE) for idx in range(len(argv))]

    def set_torque_enable(self, *argv):
        self.multi_write_status_data(STAT_REG.TORQUE_ENABLE, argv)

    # Not implemented yet
    # def get_homing_complete(self, m_id):
    #     val = self.read_status_data(m_id, STAT_REG.HOMING_COMPLETE)
    #     return val

    def get_goal_id(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.GOAL_ID) for idx in range(len(argv))]

    def set_goal_id(self, *argv):
        self.multi_write_status_data(STAT_REG.GOAL_ID, argv)

    def get_goal_iq(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.GOAL_IQ) for idx in range(len(argv))]

    def set_goal_iq(self, *argv):
        self.multi_write_status_data(STAT_REG.GOAL_IQ, argv)

    def get_goal_velocity(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.GOAL_VEL) for idx in range(len(argv))]

    def set_goal_velocity(self, *argv):
        self.multi_write_status_data(STAT_REG.GOAL_VEL, argv)

    def get_goal_position(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.GOAL_POS) for idx in range(len(argv))]

    def set_goal_position(self, *argv):
        self.multi_write_status_data(STAT_REG.GOAL_POS, argv)

    def get_present_id(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.PRESENT_ID) for idx in range(len(argv))]

    def get_present_iq(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.PRESENT_IQ) for idx in range(len(argv))]

    def get_present_velocity(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.PRESENT_VEL) for idx in range(len(argv))]

    def get_present_position(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.PRESENT_POS) for idx in range(len(argv))]

    def get_input_voltage(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.INPUT_VOLTAGE) for idx in range(len(argv))]

    def get_winding_temperature(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.WINDING_TEMP) for idx in range(len(argv))]

    def get_powerstage_temperature(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.POWERSTAGE_TEMP) for idx in range(len(argv))]

    def get_ic_temperature(self, *argv):
        return [self.read_status_data(argv[idx], STAT_REG.IC_TEMP) for idx in range(len(argv))]

    # Not implemented yet
    # def get_error_status(self, m_id):
    #     val = self.read_status_data(m_id, STAT_REG.ERROR_STATUS)
    #     return val
    #
    # def get_warning_status(self, m_id):
    #     val = self.read_status_data(m_id, STAT_REG.WARNING_STATUS)
    #     return val

    def get_bulk_status(self, *argv):
        return [self.read_bulk_status_data(argv[idx]) for idx in range(len(argv))]

    def set_bulk_status(self, *argv):
        self.multi_write_bulk_status_data(argv)

    def bulk_read(self, m_ids, registers):
        return self.bulk_comm(m_ids, registers, [], [])
    
    def bulk_write(self, m_ids, registers, commands):
        return self.bulk_comm(m_ids, [], registers, commands)

    def bulk_read_write(self, m_ids, read_reg, write_reg, commands):
        return self.bulk_comm(m_ids, read_reg, write_reg, commands)
