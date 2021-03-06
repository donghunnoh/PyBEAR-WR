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

import pdb
import struct
import time
import sys

from itertools import chain

import numpy as np
import serial

from pybear.TIMING_TABLE import *
from pybear.CONTROL_TABLE import *
from pybear.CRC import *


class PKT(object):
    def __init__(self, port, baudrate, timeout=0.0, bulk_timeout=None):
        if not self.debug:
            self.ser = serial.Serial(
                port,
                baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout,
            )
        else:
            pass

        self._bulk_timeout = bulk_timeout

        if sys.version_info[0] < 3: # Python 2
            self.ord_adapt = lambda x : ord(x)
            self.sustr_adapt = lambda val: ''.join(chr(idx) for idx in val)
            self.sustr_loop_adapt = lambda idx, val: ''.join(chr(idx) for idx in val[idx:idx+4])
            pass
        else: # Python 3
            self.ord_adapt = lambda x : x
            self.sustr_adapt = lambda val: bytearray(val)
            self.sustr_loop_adapt = lambda idx, val: bytearray(val[idx:idx+4])

    def close(self):
        """
        Close the serial port
        """
        if self.ser:
            self.ser.close()

    def __del__(self):
        self.close()

    def __write_packet(self, packet):
        if not self.debug:
            self.ser.reset_input_buffer()
            self.ser.write(bytearray(packet))
        else:
            print("[DEBUG] :: __write_packet(): {}".format(packet))
            pdb.set_trace()

    # def __read_packet(self, motor_id):
    #     status_packet = []
    #     status_packet.extend(self.ser.read(4))
    #     # print("Waiting in... : {}".format(status_packet))
    #     if status_packet:
    #         extlen = ord(status_packet[3])
    #         while self.ser.inWaiting() < extlen:
    #             pass
    #         status_packet.extend(self.ser.read(extlen))
    #         status_packet = [ord(idx) for idx in status_packet[5:-1]]
    #     return status_packet

    def __read_packet(self, motor_id):
        # TODO: Should we use checksum to verify return?
        status_packet = []
        status_packet.extend(self.ser.read(4))
        if status_packet:
            extlen = self.ord_adapt(status_packet[3])
            while self.ser.inWaiting() < extlen:
                pass
            status_packet.extend(self.ser.read(extlen))
            # Temporary absolute error watch:
            if len(status_packet) < 7:
                print("Debug __read_packet, status_packet length is only", len(status_packet))
                print("extlen is:", extlen)
                error_code = 0b10000001
                status_packet = [self.ord_adapt(idx) for idx in status_packet[5:-1]]
            else:
                error_code = status_packet[4]
                status_packet = [self.ord_adapt(idx) for idx in status_packet[5:-1]]
        return status_packet, error_code

    def __read_bulk_packet(self, motor_id):
        """
        Returning multiple register values in the order of the initial status packet.
        """
        pass

    def __write_data(self, m_id, add_list, data, reg_type=None):
        if reg_type == 'cfg':
            instruction = INSTRUCTION.WRITE_CFG
        elif reg_type == 'stat':
            instruction = INSTRUCTION.WRITE_STAT

        if add_list > 2 and reg_type == 'cfg' or add_list > 1 and reg_type == 'stat':
            data = self.__float32_to_hex(data)
            data = [data[i:i+2] for i in range(2,len(data),2)]
            data = tuple([int(x, 16) for x in data])
            n_add = len((add_list,))+len((data))+2
            checksum = self.chksum(m_id, n_add, instruction, (add_list, sum(data)))
        else:
            data = (data & 0xFF, (data >> 8) & 0xFF, (data >> 16) & 0xFF, (data >> 24) & 0xFF)
            n_add = len((add_list,))+len((data))+2
            checksum = self.chksum(m_id, n_add, instruction, (add_list, sum(data)))

        # Generate packet
        packet = self.__packet_generator(m_id, n_add, instruction, add_list, data, checksum)

        # Write packet
        self.__write_packet(packet)

    def write_status_data(self, m_id, add_list, data):
        """
        This command is to write data to the status registers.
        """
        self.__write_data(m_id, add_list, data, reg_type='stat')

    def multi_write_status_data(self, add, data):
        """
        Convenient loop function for writing to multiple motors and to a single register.
        # TODO: To be merged into self.write_cfg_data() and deprecated.
        """
        for idx in range(len(data)):
            self.write_status_data(data[idx][0], add, data[idx][1])

    def write_cfg_data(self, m_id, add_list, data):
        """
        This command is to write data to the configuration registers.
        """
        self.__write_data(m_id, add_list, data, reg_type='cfg')

    def multi_write_cfg_data(self, add, data):
        """
        Convenient loop function for writing to multiple motors and to a single register.
        # TODO: To be merged into self.write_cfg_data() and deprecated.
        """
        for idx in range(len(data)):
            self.write_cfg_data(data[idx][0], add, data[idx][1])

    def write_bulk_cfg_data(self, m_id, adpair):
        """
        Write multiple configuration registers from a single motor in one packet.
        m_id: Motor ID
        adpair: ('address', data) pairs
        """
        self.__write_bulk_data(m_id, adpair, reg_type='cfg')

    def multi_write_bulk_cfg_data(self, argv):
        """
        Convenient loop function for writing to multiple motors with bulk writes to registers.
        """
        for idx in range(len(argv)):
            self.write_bulk_cfg_data(argv[idx][0], argv[idx][1:])

    def write_bulk_status_data(self, m_id, adpair):
        """
        Write multiple configuration registers from a single motor in one packet.
        m_id: Motor ID
        adpair: ('address', data) pairs
        """
        self.__write_bulk_data(m_id, adpair, reg_type='stat')

    def multi_write_bulk_status_data(self, argv):
        """
        Convenient loop function for writing to multiple motors with bulk writes to registers.
        """
        for idx in range(len(argv)):
            self.write_bulk_status_data(argv[idx][0], argv[idx][1:])

    def __write_bulk_data(self, m_id, adpair, reg_type=None):
        if reg_type == 'cfg':
            instruction = INSTRUCTION.WRITE_CFG
        elif reg_type == 'stat':
            instruction = INSTRUCTION.WRITE_STAT

        n_add = 0
        n_adpair = len(adpair)//2 # Identify the number of registers to write to
        adpair_hex = []


        for idx in range(n_adpair):
            idx_ptr = 2*idx
            if reg_type == 'cfg':
                addr = CFG_REG_DIC[adpair[idx_ptr]]
            elif reg_type == 'stat':
                addr = STAT_REG_DIC[adpair[idx_ptr]]

            data = adpair[idx_ptr+1]
            if addr > 2 and reg_type == 'cfg' or addr > 1 and reg_type == 'stat':
                data = self.__float32_to_hex(data)
                data = [data[i:i+2] for i in range(2,len(data),2)]
                data = [int(x, 16) for x in data]
                if reg_type == 'cfg':
                    n_add += len((CFG_REG_DIC[adpair[idx_ptr]],)) + len(data)
                elif reg_type == 'stat':
                    n_add += len((STAT_REG_DIC[adpair[idx_ptr]],)) + len(data)
            else:
                data = list((data & 0xFF, (data >> 8) & 0xFF, (data >> 16) & 0xFF, (data >> 24) & 0xFF))
                if reg_type == 'cfg':
                    n_add += len((CFG_REG_DIC[adpair[idx_ptr]],))+len(data)
                elif reg_type == 'stat':
                    n_add += len((STAT_REG_DIC[adpair[idx_ptr]],))+len(data)
        
            adpair_hex = adpair_hex + [addr] + data
        
        n_add += 2
        checksum = self.chksum(m_id, n_add, instruction, adpair_hex)

        # Generate packet
        packet = self.__packet_generator(m_id, n_add, instruction, adpair_hex, None, checksum)

        # Write packet
        self.__write_packet(packet)

    def __read_data(self, m_id, add_list, reg_type=None, data_type=None):
        if reg_type == 'cfg':
            instruction = INSTRUCTION.READ_CFG
        elif reg_type == 'stat':
            instruction = INSTRUCTION.READ_STAT

        pkt_len = np.add(len((add_list,)), 2)

        checksum = self.chksum(m_id, pkt_len, instruction, (add_list,))

        packet = self.__packet_generator(m_id, pkt_len, instruction, add_list, None, checksum)

        # while self.ser.in_waiting > 0:
        #     self.ser.reset_input_buffer()
        self.ser.reset_input_buffer()
        self.__write_packet(packet)

        # Timeout prevention if communication error starts occuring
        t_bus_init = time.time()
        while True:
            if self.ser.inWaiting() > 3:
                break
            if time.time() - t_bus_init > TIMEOUT_MAX:
                print("[PyBEAR | WARNING] :: Status response timed out. Re-sending the same packet.")
                self.ser.reset_input_buffer()
                self.__write_packet(packet)
                t_bus_init = time.time()
        # while self.ser.inWaiting() < 4:
        #     pass

        status, error_code = self.__read_packet(m_id)

        if data_type == 'f32':
            return self.__hex_to_float32(status), error_code
        elif data_type == 'u32':
            return status[0], error_code

    def __read_bulk_data(self, m_id, add_list, reg_type=None, data_type=None):
        """
        m_id: Motor id
        add_list: List of register addresses to read
        """
        if reg_type == 'cfg':
            instruction = INSTRUCTION.READ_CFG
        elif reg_type == 'stat':
            instruction = INSTRUCTION.READ_STAT

        pkt_len = np.add(len(add_list), 2)

        checksum = self.chksum(m_id, pkt_len, instruction, add_list)

        packet = self.__packet_generator(m_id, pkt_len, instruction, add_list, None, checksum)

        self.__write_packet(packet)

        while self.ser.inWaiting() < 4:
            pass

        # status = self.__read_bulk_packet(m_id)
        status, error_code = self.__read_packet(m_id)

        # Place holder for multiple reads later.
        # read_val = status[3]

        if data_type == 'f32':
            # return self.__hex_to_float32(status[5:-1])
            return self.__hex_to_float32(status), error_code
        elif data_type == 'u32':
            # return status[5]
            return status[0], error_code

    # def __bulk_communication_save(self,):
    #
    #
    #     instruction = INSTRUCTION.BULK_COMM
    #
    #     m_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    #
    #     num_stat_read = 3
    #     num_stat_write = 0
    #     num_total_stat = num_stat_write + num_stat_read*16
    #     read_addr = [STAT_REG.PRESENT_POS, STAT_REG.PRESENT_VEL, STAT_REG.WINDING_TEMP]
    #     pkt_length = 3+num_stat_read+num_stat_write+len(m_ids)+1
    #
    #     data = [len(m_ids), num_total_stat, sum(read_addr), sum(m_ids)]
    #
    #     checksum = self.chksum(0xFE, pkt_length, instruction, data)
    #
    #     packet = self.__packet_generator_bulk(m_ids, pkt_length, instruction, num_total_stat, read_addr, checksum)
    #
    #     self.__write_packet(packet)
    #
    #     while self.ser.inWaiting() < 4:
    #         pass
    #
    #     status_packet = []
    #     status_packet.extend(self.ser.read(4))
    #     # print("Status packet: {}".format(status_packet))
    #     if status_packet:
    #         retlen = ord(status_packet[3])
    #         totlen = retlen + (4+retlen)*(len(m_ids)-1)
    #         while self.ser.inWaiting() < totlen:
    #             pass
    #         status_packet.extend(self.ser.read(totlen))
    #         output = []
    #         for x in range(len(m_ids)):
    #             for idx in status_packet[5+x*(4+retlen):-1+(x+1)*(4+retlen)]:
    #                 output.append(ord(idx))
    #         status_packet = [ord(idx) for index in range(len(m_ids))
    #                          for idx in status_packet[5+index*(4+retlen):-1+(index+1)*(4+retlen)]]
    #
    #         return np.reshape(self.__hex_to_float32(status_packet), (len(m_ids),num_stat_read))

    def __bulk_communication(self, m_ids, read_addr, write_addr, write_data):

        instruction = INSTRUCTION.BULK_COMM

        num_motors = len(m_ids)
        num_read_regs = len(read_addr)
        num_write_regs = len(write_addr)
        num_total_regs = num_write_regs + num_read_regs*16  # lower 4 bits for writes, larger 4 bits for reads

        pkt_length = 3 + num_read_regs + num_write_regs + num_motors + num_write_regs*4*num_motors + 1

        if num_write_regs is 0:
            data_packets = [len(m_ids), num_total_regs, sum(read_addr), sum(write_addr), sum(m_ids)]
            checksum = self.chksum(0xFE, pkt_length, instruction, data_packets)
            packet = self.__packet_generator_bulk(m_ids, pkt_length, instruction, num_total_regs, read_addr, write_addr, None, checksum)
        else:
            data = tuple()
            for i in range(num_motors):
                command = self.__float32_to_hex(write_data[i])
                command = [command[j:j+2] for j in range(2,len(command),2)]
                data += (m_ids[i],) + tuple([int(x, 16) for x in command])
            data_packets = [len(m_ids), num_total_regs, sum(read_addr), sum(write_addr), sum(data)]
            checksum = self.chksum(0xFE, pkt_length, instruction, data_packets)
            packet = self.__packet_generator_bulk(m_ids, pkt_length, instruction, num_total_regs, read_addr, write_addr, data, checksum)

        num_retries = 3    # set this number to change how many times PyBEAR will try to resend the packet
        error_id = 0
        error_status = 0

        for i in range(num_retries):
            t0 = time.time()

            self.__write_packet(packet)
            found_packet = True

            while self.ser.inWaiting() < 4:
                if self._bulk_timeout is None:
                    pass
                elif time.time() - t0 > self._bulk_timeout:
                    found_packet = False
                    break

            if found_packet:
                status_packet = []
                status_packet.extend(self.ser.read(4))
                if status_packet:
                    #pdb.set_trace()
                    retlen = ord(status_packet[3])  # length of the data in a single packet
                    totlen = retlen + (4+retlen)*(len(m_ids)-1)  # total length of all data coming back
                    found_data = True
                    while self.ser.inWaiting() < totlen:
                        if self._bulk_timeout is None:
                            pass
                        elif time.time() - t0 > self._bulk_timeout:
                            buffer_length = self.ser.inWaiting()
                            error_id = int((buffer_length - retlen)/(4+retlen)) + 2
                            found_data = False
                            break
                   
                    # read from the buffer either way so that it gets cleared out 
                    status_packet.extend(self.ser.read(totlen))

                    if found_data:
                        data_output = [ord(idx) for index in range(len(m_ids))
                                       for idx in status_packet[5+index*(4+retlen):-1+(index+1)*(4+retlen)]]
                        motor_status = [ord(idx) for index in range(len(m_ids)) for idx in status_packet[4+index*(4+retlen)]]
                        return error_status, motor_status, np.reshape(self.__hex_to_float32(data_output), (len(m_ids), num_read_regs))

        # Communication has been attempted but has failed!
        # Return an error_status and zeros for everything else
        if error_id == 0:
            # No packets are being returned
            error_status = -99
        else:
            # Return the motor id number that is not communicating
            error_status = -error_id
        motor_status = np.zeros((len(m_ids), 1))
        data_ouput = np.zeros((len(m_ids), num_read_regs))
        return error_status, motor_status, data_ouput

    def bulk_comm(self, m_ids, read_registers, write_registers, write_data):
        """
        Read and write from multiple motors in a single shot
        """
        read_addr_list = []
        write_addr_list = []
        if len(read_registers) is not 0:
            for idx in range(0, len(read_registers)):
                read_addr_list.append(STAT_REG_DIC[read_registers[idx]])

        if len(write_registers) is not 0:
            for idx in range(0, len(write_registers)):
                write_addr_list.append(STAT_REG_DIC[write_registers[idx]])

        return self.__bulk_communication(m_ids, read_addr_list, write_addr_list, write_data)

    def read_cfg_data(self, m_id, add_list):
        """
        This command is to read data from the configuration registers.
        """
        if add_list > 2:
            return self.__read_data(m_id, add_list, reg_type='cfg', data_type='f32')
        else:
            return self.__read_data(m_id, add_list, reg_type='cfg', data_type='u32')

    def read_bulk_cfg_data(self, argv):
        """
        Read multiple configuration registers from a single motor in one packet.
        """
        m_id = argv[0]
        addr_list = []
        for idx in range(1, len(argv)):
            addr_list.append(CFG_REG_DIC[argv[idx]])
        return self.__read_bulk_data(m_id, addr_list, reg_type='cfg', data_type='f32')

    def read_status_data(self, m_id, add_list):
        """
        This command is to read data from the status registers.
        """
        if add_list > 1:
            return self.__read_data(m_id, add_list, reg_type='stat', data_type='f32')
        else:
            return self.__read_data(m_id, add_list, reg_type='stat', data_type='u32')

    def read_bulk_status_data(self, argv):
        """
        Read multiple status registers from a single motor in one packet.
        """
        m_id = argv[0]
        addr_list = []
        for idx in range(1, len(argv)):
            addr_list.append(STAT_REG_DIC[argv[idx]])
        return self.__read_bulk_data(m_id, addr_list, reg_type='stat', data_type='f32')

    def ping(self, m_id):
        """
        Function used to detect a motor. Will return an empty return packet.
        """
        # Type of instruction
        instruction = INSTRUCTION.PING

        # Number of parameters
        pkt_len = 2

        # Create checksum
        checksum = self.chksum(m_id, pkt_len, instruction, (0,))

        # Write packet
        self.__write_packet((0xFF, 0xFF, m_id, pkt_len, instruction, checksum))
        start_time = time.time()
        while self.ser.inWaiting() < 1:
            if time.time()- start_time > PING_TIMEOUT:
                # Timeout
                return None
            else:
                pass

        # Read status
        ping_status, _ = self.__read_packet(m_id)

        return ping_status

    def save_config(self, m_id):
        instruction = INSTRUCTION.SAVE_CFG

        n_add = 2

        checksum = self.chksum(m_id, n_add, instruction, (0,))

        self.__write_packet((0xFF, 0xFF, m_id, n_add, instruction, checksum))

    # ===== Utility functions
    def __packet_generator(self, m_id, length, instruction, param_n, data, checksum):
        if isinstance(param_n, list) and len(param_n) > 1:
            if data is None:
                l = tuple([0xFF, 0xFF, m_id, length, instruction] + param_n + [checksum])
            else:
                l = tuple([0xFF, 0xFF, m_id, length, instruction] + param_n + data + [checksum])
        else:
            if data is None:
                l = (0xFF, 0xFF, m_id, length, instruction, param_n, checksum)
            else:
                l = (0xFF, 0xFF, m_id, length, instruction, param_n, data, checksum)
        # TODO: Clean up the sequence below
        return tuple((chain(*(i if isinstance(i, tuple) else (i,) for i in l))))
        # return (0xFF, 0xFF, m_id, length, instruction, param_n, data, checksum)

    def __packet_generator_bulk(self, m_ids, length, instruction, num_regs, read_addrs, write_addrs, data, checksum):
        if data is None:
            l = tuple([0xFF, 0xFF, 0xFE, length, instruction, len(m_ids), num_regs] + read_addrs + m_ids + [checksum])
        else:
            l = tuple([0xFF, 0xFF, 0xFE, length, instruction, len(m_ids), num_regs] + read_addrs + write_addrs) + data + (checksum,)
        return tuple((chain(*(i if isinstance(i, tuple) else (i,) for i in l))))

    def __float32_to_hex(self, val):
        retval = hex(struct.unpack('<I', struct.pack('>f', val))[0])
        if retval[-1] == 'L':
            retval = retval[:-1]
        if len(retval) < 10:
            length = 10-len(retval)
            retval = '0x'+length*'0'+retval[2:]
        return retval

    def __hex_to_float32(self, val):
        if len(val) > 4:
            tmpval = []
            for idx in range(0, len(val), 4):
                tmpval.append(struct.unpack('<f', self.sustr_loop_adapt(idx, val))[0])
        else:
            tmpval = struct.unpack('<f', self.sustr_adapt(val))[0]
        return tmpval

    def chksum(self, m_id, length, instruction, param_n):
        return 255 - ((m_id + length + instruction + sum(param_n)) % 256)
