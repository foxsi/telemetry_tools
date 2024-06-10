"""
CdTe collection to handle the read-in CdTe data.
"""

from copy import copy

import numpy as np
import matplotlib.pyplot as plt

class DECollection:
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.parsed_data, error_flag = parsed_data

        self.latest_data_time = old_data_time

    def get_status(self):
        return self.parsed_data["status"]
    
    def get_ping(self):
        return self.parsed_data["ping"]
    
    def get_temp(self):
        return self.parsed_data["temp"]
    
    def get_cpu(self):
        return self.parsed_data["cpu"]
    
    def get_df_gb(self):
        return self.parsed_data["df_GB"]
    
    def get_unixtime(self):
        return self.parsed_data["unixtime"]