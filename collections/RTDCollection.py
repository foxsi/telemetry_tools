"""
RTD collection to handle the read-in RTD data.
"""

import numpy as np

from FoGSE.telemetry_tools.parsers.RTDparser import numpy_struct


class RTDCollection:
    """
    A container for RTD data after being parsed.
    
    Can be used to generate time series plots.
    
    Paramters
    ---------
    parsed_data : `tuple`, length 2
            Contains `df_values, `df_errors` as returned from the parser.

    old_data_time : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            
    Example
    -------
    ...
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.event, _ = parsed_data

        # filter data to only include the new stuff
        self.last_data_time = old_data_time
        self.new_entries = self.event['ti']>self.last_data_time
        self.last_data_time = self.event['ti'][-1]

        # collect new data
        self.new_data = self.event.filter(self.new_entries) 

        self.chip1_ids = ['ts0', 'ts1', 'ts2', 'ts3', 'ts4', 'ts5', 'ts6', 'ts7', 'ts8']
        self.chip2_ids = ['ts9', 'ts10', 'ts11', 'ts12', 'ts13', 'ts14', 'ts15', 'ts16', 'ts17']

    def chip1_data(self):
        """Chip 1 data: ti and t0 to t8. """
        chip1_values = [list(self.new_data["ti"])]
        for ids1 in self.chip1_ids:
            chip1_values.append(list(self.new_data[ids1]))
        return chip1_values

    def chip2_data(self):
        """Chip 2 data: ti and t9 to t17. """
        chip2_values = [list(self.new_data["ti"])]
        for ids2 in self.chip2_ids:
            chip2_values.append(list(self.new_data[ids2]))
        return chip2_values
