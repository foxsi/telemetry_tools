"""
Catch collection to handle the read-in RTD data.
"""

import numpy as np

class CatchCollection:
    """
    A container for Catch data after being parsed.
    
    Can be used to generate time series plots.
    
    Paramters
    ---------
    parsed_data : `tuple`, length 2
            Contains lines from the catch file.

    old_data_time : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            NOT USED
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.lines = parsed_data

    def get_last_line(self):
        """ Return the mean time-over-threshold. """
        if len(self.lines)>0: return self.lines[-1]
