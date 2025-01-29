"""
Ping collection to handle the read-in Formatter ping data.
"""


class PingCollection:
    """
    A container for ping data after being parsed.
    
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
        error, data = Pingparser(raw_data)
        
    ping_data = PingCollection((error, data))
    
    plt.figure()
    ping_data.plot_trace()
    plt.show()
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.output, self.error_flag = parsed_data
        
        # used in the filter to only consider data with times > than this
        self.last_data_time = old_data_time

    def get_unixtime(self):
        return self.output["unixtime"]
    
    def get_global_errors_int(self):
        return self.output["global_errors_int"]

    def get_all_systems_state(self):
        return {k: self.output[k]["system_state_str"] for k in self.output.keys() if type(k) is int}
    
    def get_all_systems_error(self):
        return {k: self.output[k]["system_error_str"] for k in self.output.keys() if type(k) is int}