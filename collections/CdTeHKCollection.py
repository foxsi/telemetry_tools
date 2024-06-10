"""
CdTe collection to handle the read-in CdTe data.
"""

from copy import copy

import numpy as np
import matplotlib.pyplot as plt

class CdTeHKCollection:
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.parsed_data, error_flag = parsed_data

        self.latest_data_time = old_data_time
        
    def get_status(self):
        return self.parsed_data["status"]
    
    def get_write_pointer(self):
        return self.parsed_data["write_pointer"]
    
    def get_hv_set(self):
        return self.parsed_data["hv"]
    
    def get_frame_count(self):
        return self.parsed_data["frame_count"]
    
    def get_unread_can_frame_count(self):
        return self.parsed_data["unread_can_frame_count"]
