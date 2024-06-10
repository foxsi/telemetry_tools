"""
Timepix collection to handle the read-in RTD data.
"""

import numpy as np

class TimepixCollection:
    """
    A container for Timepix data after being parsed.
    
    Can be used to generate time series plots.
    
    Paramters
    ---------
    parsed_data : `tuple`, length 2
            Contains `df_values, `df_errors` as returned from the parser.

    old_data_time : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            NOT USED
            
    Example
    -------
    from FoGSE.telemetry_tools.parsers.Timepixparser import timepix_parser
    from FoGSE.telemetry_tools.collections.TimepixCollection import TimepixCollection

    # get the raw data and parse it
    tot, flx, flgs = timepix_parser(raw_data)

    # set to a single variable
    parsed_data = (tot, flx, flgs)

    # pass the parsed data to the collection
    col = TimepixCollection(parsed_data, 0)

    # to get the mean time-over-threshold, e.g., for the parsed data
    col.get_mean_tot()
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.data = parsed_data
        # # filter data to only include the new stuff
        # self.last_data_time = old_data_time
        # self.new_entries = self.event['ti']>self.last_data_time
        # self.last_data_time = self.event['ti'][-1]

    def get_unixtime(self):
        """ Return the unix time for the frame. """
        return self.data["unixtime"]
    
    def get_mean_tot(self):
        """ Return the mean time-over-threshold. """
        return self.data["mean_tot"]
    
    def get_flux(self):
        """ Return the flux. """
        return self.data["flx_rate"]

    def get_flags(self):
        """ Return the flags. """
        flags = self.data["flags"]
        if (type(flags) is list) and (1 in flags): flags.remove(1)
        return flags
    
    def get_defined_flags(self):
        """ Return the descriptions of the raised flags. """
        return self.data["defined_flags"]

    def get_board_t1(self):
        """ Return the first temperature for the board. """
        return self.data["board_t1"]

    def get_board_t2(self):
        """ Return the second temperature for the board. """
        return self.data["board_t2"]

    def get_asic_voltages(self):
        """ Return the ASIC voltages. """
        return self.data["asic_voltages"]

    def get_asic_currents(self):
        """ Return the ASIC currents. """
        return self.data["asic_currents"]

    def get_fpga_voltages(self):
        """ Return the FPGA voltages. """
        return self.data["fpga_voltages"]
    
    def get_fpga_temp(self):
        """ Return the FPGA temperature. """
        return self.data["fpga_temp"]

    def get_storage_fill(self):
        """ Return the storage reading. """
        return self.data["storage_fill"]

    def get_hvps_status(self):
        """ Return the storage reading. """
        return self.data["hvps_status"]