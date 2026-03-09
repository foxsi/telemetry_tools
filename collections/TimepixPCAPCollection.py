"""
Timepix collection to handle the read-in RTD data.
"""

import numpy as np

class TimepixPCAPCollection:
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

    def get_pcap_all(self):
        """ All PCAP values. """
        return self.data

    def get_pcap1(self):
        """ PCAP1: most recent PCAP's size """
        return self.data[0]

    def get_pcap2(self):
        """ PCAP2: 2nd most recent PCAP's size """
        return self.data[1]

    def get_pcap3(self):
        """ PCAP3:  """
        return self.data[2]

    def get_pcap4(self):
        """ PCAP4:  """
        return self.data[3]
    