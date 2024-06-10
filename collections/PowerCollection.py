"""
Power collection to handle the read-in power data.
"""

import numpy as np
import matplotlib.pyplot as plt


class PowerCollection:
    """
    A container for power data after being parsed.
    
    Parameters
    ---------
    parsed_data : `tuple`, length 2
            Contains `error`, `data`, as returned from the parser.

    old_data_time : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            
    Example
    -------
    with BackwardsReader(file=self.data_file, blksize=self.buffer_size, forward=True) as f:
        data = f.read_block()
        error, data = Powerparser(raw_data)
        
    power_data = PowerCollection((error, data))
    
    plt.figure()
    power_data.plot_trace()
    plt.show()
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.output, self.error_flag = parsed_data
        
        # used in the filter to only consider data with times > than this
        self.last_data_time = old_data_time

    def get_unixtime(self):
        return self.output["unixtime"]
    
    def get_p0(self):
        return self.output[0]
    
    def get_p1(self):
        return self.output[1]
    
    def get_p2(self):
        return self.output[2]
    
    def get_p3(self):
        return self.output[3]
    
    def get_p3(self):
        return self.output[3]
    
    def get_p4(self):
        return self.output[4]
    
    def get_p5(self):
        return self.output[5]
    
    def get_p6(self):
        return self.output[6]
    
    def get_p7(self):
        return self.output[7]
    
    def get_p8(self):
        return self.output[8]
    
    def get_p9(self):
        return self.output[9]
    
    def get_p10(self):
        return self.output[10]
    
    def get_p11(self):
        return self.output[11]
    
    def get_p12(self):
        return self.output[12]
    
    def get_p13(self):
        return self.output[13]
    
    def get_p14(self):
        return self.output[14]
    
    def get_p15(self):
        return self.output[15]
