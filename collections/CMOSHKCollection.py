"""
CMOS collection to handle the read-in CMOS data.
"""

import numpy as np
import matplotlib.pyplot as plt


class CMOSHKCollection:
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.parsed = parsed_data
        
        # used in the filter to only consider data with times > than this
        self.last_data_time = old_data_time

    def get_line_time(self):
        return self.parsed["line_time"]
    
    def get_line_time_at_pps(self):
        return self.parsed["line_time_at_pps"]
    
    def get_cpu_load_average(self):
        return self.parsed["cpu_load_average"]
    
    def get_remaining_disk_size(self):
        return self.parsed["remaining_disk_size"]
    
    def get_software_status(self):
        return self.parsed["software_status"]
    
    def get_error_time(self):
        return self.parsed["error_time"]
    
    def get_error_flag(self):
        return self.parsed["error_flag"]
    
    def get_error_training(self):
        return self.parsed["error_training"]
    
    def get_data_validity(self):
        return self.parsed["data_validity"]
    
    def get_sensor_temp(self):
        return self.parsed["sensor_temp"]
    
    def get_fpga_temp(self):
        return self.parsed["fpga_temp"]
    
    def get_gain_mode(self):
        return self.parsed["gain_mode"]
    
    def get_exposureQL(self):
        return self.parsed["exposureQL"]
    
    def get_exposurePC(self):
        return self.parsed["exposurePC"]
    
    def get_repeat_N(self):
        return self.parsed["repeat_N"]
    
    def get_repeat_n(self):
        return self.parsed["repeat_n"]
    
    def get_gain_even(self):
        return self.parsed["gain_even"]
    
    def get_gain_odd(self):
        return self.parsed["gain_odd"]
    
    def get_ncapture(self):
        return self.parsed["ncapture"]
    
    def get_write_pointer_position_store_data(self):
        return self.parsed["write_pointer_position_store_data"]
    
    def get_read_pointer_position_QL(self):
        return self.parsed["read_pointer_position_QL"]
    
    def get_data_size_QL(self):
        return self.parsed["data_size_QL"]
    
    def get_read_pointer_position_PC(self):
        return self.parsed["read_pointer_position_PC"]
    
    def get_data_size_PC(self):
        return self.parsed["data_size_PC"]
    
    def get_cmos_init(self):
        return self.parsed["cmos_init"]
    
    def get_cmos_training(self):
        return self.parsed["cmos_training"]
    
    def get_cmos_setting(self):
        return self.parsed["cmos_setting"]
    
    def get_cmos_start(self):
        return self.parsed["cmos_start"]
    
    def get_cmos_stop(self):
        return self.parsed["cmos_start"]
    
    def get_data_size_PC(self):
        return self.parsed["cmos_stop"]