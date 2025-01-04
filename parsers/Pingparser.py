
"""Dictionary describing values the system_state field can take"""
system_state_values = {
    "off":          0x00,
    "await":        0x01,
    "startup":      0x02,
    "init":         0x03,
    "loop":         0x04,
    "end":          0x05,
    "disconnect":   0x06,
    "abandon":      0x07,
    "invalid":      0xff
}

"""Dictionary describing values the system_error field can take"""
system_error_values = {
    "reading_packet":       1 << 0,
    "reading_frame":        1 << 1,
    "reading_invalid":      1 << 2,
    "writing_invalid":      1 << 3,
    "frame_packetizing":    1 << 4,
    "packet_framing":       1 << 5,
    "commanding":           1 << 6,
    "uplink_forwarding":    1 << 7,
    "downlink_buffering":   1 << 8,
    "command_lookup":       1 << 9,
    "buffer_lookup":        1 << 10,
    "spw_vcrc":             1 << 11,
    "spw_length":           1 << 12
}

# inverting the above dictionaries, so we can look up by the `int` value and get the name
system_state_names = {v: k for k, v in system_state_values.items()}
system_error_names = {v: k for k, v in system_error_values.items()}

# debug
# pprint(system_error_names)
# pprint(system_error_values)
# assert(len(system_error_values) == len(system_error_names))



def pingparser(data: bytes):
    """
    Parse Formatter Ping packet into a `dict`.

    Paramaters
    ----------
    data : `bytes`
        A raw data frame output by the Formatter board. Raw data 46 bytes total, 4 bytes of 
        Formatter unixtime, 2 bytes of global software status (currently unused), then 10 
        repeating byte patterns for each onboard system. The pattern is:
            - system hex ID [1 byte]
            - system state code [1 byte]
            - system error code [2 bytes]
        The order in which systems appear here is dictated by the loop order in the Formatter
        software.

    Returns
    -------
    `tuple(dict, bool)` : 
        The bool indicates whether there was an error in parsing. The dict has the following 
        structure:
            - `unixtime`: the Formatter clock value when it recorded the ping packet.
            - `global_errors_int`: currently unused, always zero.
            - A `dict` of `dict`s. The outer key is the system hex ID code (see systems.json), 
            and the inner keys are:
                - `system_state_int`: raw integer code for system state (8 bit)
                - `system_error_int`: raw integer code for system state (16 bit)
                - `system_state_str`: string description of system state
                - `system_error_str`: `dict(str, bool)` indicating which error flags are raised.
    """

    frame_size = 46
    frame_count = len(data) // frame_size
    if frame_count > 1:
        data = data[0:frame_size]

    error_flag = False

    if len(data) % frame_size != 0:
        print("Formatter ping frames are 46 bytes long. Cannot parse from a different block size.")
        error_flag = True
        return {}, error_flag
    
    unixtime_raw = int.from_bytes(data[0:4], "big")
    global_errors_raw = int.from_bytes(data[5:6], "big")

    nsys = (len(data) - 6) // 4     # count systems in the rest of the packet
    result = {"unixtime": unixtime_raw, "global_errors_int": global_errors_raw}

    for k in range(nsys):   # k indexes systems
        i = 6 + 4*k         # i indexes the data array

        try:
            this_system = int(data[i])
            this_state_int = int(data[i+1])
            this_error_int = int.from_bytes(data[i+2:i+4], "big")

            result[this_system] = {
                "system_state_int": this_state_int,
                "system_error_int": this_error_int,
                "system_state_str": system_state_names[this_state_int],
                "system_error_str": {system_error_names[e]: (this_error_int & e) != 0 for e in system_error_names.keys()}
            }
        except KeyError:
            error_flag = True

    return result, error_flag



if __name__ == "__main__":
    
    import sys
    from pprint import pprint

    if len(sys.argv) == 1:
        testfile = "data/ping.log"
        with open(testfile, "rb") as f:
            data = f.read()
            p = pingparser(data)
            pprint(p)

    elif len(sys.argv) == 2:
        print("opening", sys.argv[1])
        with open(sys.argv[1], "rb") as f:
            
            def chunks(lst, n):
                """Yield successive n-sized chunks from lst."""
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]
            
            data = f.read()
            for chunk in chunks(data, 46):
                p = pingparser(chunk)
                pprint(p[0][9]['system_error_str']['reading_packet'])

    else:
        print("use like this:\n\t> python parsers/Pingparser.py\n\t\tor\n\t>python parsers/Pingparser.py path/to/ping/file.log")