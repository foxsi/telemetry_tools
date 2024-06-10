
import os.path
import numpy as np
# todo: possibly roll raw MAX7317 readout into this raw stream as well?

def adcparser(data: bytes):
    """
    Parse ADC measurements of voltage and current into a `numpy.ndarray`.

    Paramaters
    ----------
    data : `bytes`
        A raw data frame output by the Housekeeping board. Raw data is 6 bytes 
        of header data, followed by 16 2-byte long samples concatenated 
        (38 bytes total, or a multiple of 38).
        Data is taken from the AD7490 multiplexed ADC: 
        https://www.analog.com/en/products/ad7490.html.
        First 4 bits are channel number. Next 12 bits are raw data for that channel.

    Returns
    -------
    `dict` : 
        A dictionary mapping `int` channel number into `float` measured value. The 
        first 4 entries (keys `0` through `3`) are voltages (unit V); the remainder  
        are currents (unit A).
    """
    
    frame_size = 38
    frame_count = len(data) // frame_size
    error_flag = False

    if len(data) % frame_size != 0:
        print("Housekeeping power frames are 38 bytes long. Cannot parse from a different block size.")
        error_flag = True
        return {}, error_flag
    
    unixtime_raw = int.from_bytes(data[2:6], "big")
    channels_raw = [int.from_bytes(data[i:i+2],"big") for i in range(6,len(data),2)]
    
    # measure the 5 V channel, use to bootstrap other measurements.
    raw_5v_src = int.from_bytes(data[12:14], "big", signed=False)
    channel_5v = raw_5v_src >> 12
    if channel_5v != 0x03:
        print("5 V measurement channel is in the wrong place! Got ", hex(channel_5v))
        error_flag = True
        return {},error_flag
    
    ref_5v = 5.0        # [V] reference input voltage for ADC scale
    current_gain = 0.2  # [V/A] current-to-voltage gain for Hall-effect sensors
    
    # note that last measured on-board, as-built value was 5.36 V for 5 V supply. This 
    # matches nicely with a coefficient of 1.68.
    divider_coefficients = [9.2, 4.0, 4.0, 1.68]
    measured_5v = divider_coefficients[3] * ref_5v * (raw_5v_src & 0x0fff) / 0x0fff
    
    output = {}
    for raw in channels_raw:
        ch = raw >> 12
        this_ratiometric = ref_5v * (raw & 0x0fff) / 0x0fff
        if ch < 4:
            if ch == 0x03:
                output[ch] = measured_5v
            else:
                output[ch] = divider_coefficients[ch] * this_ratiometric
        else:
            output[ch] = (this_ratiometric - measured_5v/2) / current_gain
    
    output["unixtime"] = unixtime_raw

    return output, error_flag

if __name__ == "__main__":
    # Kris! put your own test file here:
    testfile = "logs/received/23-1-2024_10:32:8/housekeeping_pow.log"
    with open(testfile, "rb") as f:
        data = f.read()
        adcparser(data)