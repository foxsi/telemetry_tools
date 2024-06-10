#flag_function_tpx_ex.py

class FlagByte:
    def __init__(self):
        self.flags = 0         								# Initialize with all flags set to 0
    def raise_flag(self, flag_index):
        self.flags |= (1 << flag_index)         			# Set the bit at the specified index to 1
    def clear_flag(self, flag_index):         				# Set the bit at the specified index to 0
        self.flags &= ~(1 << flag_index)
    def is_flag_set(self, flag_index):				        # Check if the bit at the specified index is 1
        return bool(self.flags & (1 << flag_index))
    def get_flags(self):					        		# Return the entire byte representing flags
        return self.flags


class ReadALLHKPacket:
    def __init__(self, board_t1: int = 0, board_t2: int = 0, asic_voltages: list = [0, 0, 0, 0],
                 asic_currents: list = [0, 0, 0, 0], fpga_values: list = [0, 0, 0], rpi_storage_fill: int = 0):
        self.board_t1 = board_t1  # 3-digit integer
        self.board_t2 = board_t2  # 3-digit integer
        self.asic_voltages = asic_voltages  # List of 4 integers (each with a max of 5 digits)
        self.asic_currents = asic_currents  # List of 4 integers (each with a max of 4 digits)
        self.fpga_values = fpga_values  # List of 3 integers (each with a max of 4 digits)
        self.rpi_storage_fill = rpi_storage_fill  # 3-digit integer

class ReadRatesPacket:
    def __init__(self, mean_tot: int = 0, flx_rate: int = 0):
        self.mean_tot = mean_tot  					# 2-byte integer (0-1022)
        self.flx_rate = flx_rate  					# 2-byte integer (four digits)



def unpack_read_all_hk_packet(packet):
    data = ReadALLHKPacket()

    data.board_t1 = packet[0] + (packet[1] << 8)
    data.board_t2 = packet[2] + (packet[3] << 8)

    for i in range(4):
        voltage = packet[4 + i * 4] + (packet[5 + i * 4] << 8)
        current = packet[6 + i * 4] + (packet[7 + i * 4] << 8)
        data.asic_voltages[i] = voltage
        data.asic_currents[i] = current

    for i in range(3):
        data.fpga_values[i] = packet[20 + i * 2] + (packet[21 + i * 2] << 8)
    data.rpi_storage_fill = packet[26]
    return data


def unpack_read_rates_packet(packet):
    data = ReadRatesPacket()
    data.mean_tot = packet[0] | (packet[1] << 8)
    data.flx_rate = packet[2] | (packet[3] << 8)
    return data

def get_flags_from_byte(byte_value):
    flags = []
    for i in range(8):
        if byte_value & (1 << i):
            flags.append(i)
    return flags


def defined_flag(flags_set):
    flag_messages = {
        0: "Warning: large UDPs",
        1: "HVPS Bias On",
        2: "Software Error",
        3: "Storage Warning",
        4: "Board Temp Exceeding",
        5: "FPGA Temp Exceeding",
        6: "In HIGHPOWER",
        7: "Timeout"
    }

    if not flags_set:
        print("No flags are set")
    else:
        print("Flags are set:")
        for flag in flags_set:
            if flag in flag_messages:
                print(flag_messages[flag])

FLAG_MESSAGES = {
        0: "Warning: large UDPs",
        1: "HVPS Bias On",
        2: "Software Error",
        3: "Storage Warning",
        4: "Board Temp Exceeding",
        5: "FPGA Temp Exceeding",
        6: "In HIGHPOWER",
        7: "Timeout"
    }

def get_defined_flags(flags_set):
    """ Return a list of the flag messages if any. """
    if not flags_set:
        return [flags_set]

    return [FLAG_MESSAGES[flag] for flag in flags_set if flag in FLAG_MESSAGES]


def check_hvps(flags_set):
    if 1 in flags_set:
        print("hvps on")
    else:
        print("hvps off")

def get_hvps_status(flags_set):
    """ Return whether HVPS is set. """
    if 1 in flags_set:
        return "on"
    else:
        return "off"


def timepix_parser(byte_data):
    """ Take in a frame of raw bytes for a Timepix frame and return 
    usable values. 
    
    Parameters
    ----------
    byte_data : `list[bytes]`
        The frame bytes of a Timepix frame (size of 0x26 bytes==38 bytes).
    
    Returns
    -------
    `dict` :
        A dictionary of the Timepix data from the `byte_data` frame.
    """
    # create dictionary for timepix info to be returned
    timepix_dict = dict()

    # separate bytes
    rec_ff_unix = byte_data[0:6] #first 6 bytes 
    timepix_dict["unixtime"] = rec_ff_unix # does this need converted?
    rec_flag_byte = byte_data[6:7] #7th byte 
    rec_read_hk = byte_data[7:34]
    rec_read_rates_bytes = byte_data[34:]

    # undo flag bytes
    byte_value = rec_flag_byte  # Corrected byte value creation
    flags_set = get_flags_from_byte(byte_value[0])

    #undo the hk_packet and get info
    received_data = unpack_read_all_hk_packet(rec_read_hk)
    timepix_dict["board_t1"] = received_data.board_t1
    timepix_dict["board_t2"] = received_data.board_t2
    timepix_dict["asic_voltages"] = received_data.asic_voltages
    timepix_dict["asic_currents"] = received_data.asic_currents
    timepix_dict["fpga_voltages"] = received_data.fpga_values[:2]
    timepix_dict["fpga_temp"] = received_data.fpga_values[-1]
    timepix_dict["storage_fill"] = received_data.rpi_storage_fill

    # get the actual data info
    read_rates_data = unpack_read_rates_packet(rec_read_rates_bytes)
    timepix_dict["mean_tot"] = read_rates_data.mean_tot
    timepix_dict["flx_rate"] = read_rates_data.flx_rate

    # now get final flag info
    timepix_dict["flags"] = flags_set 
    timepix_dict["defined_flags"] = get_defined_flags(flags_set)
    timepix_dict["hvps_status"] = get_hvps_status(flags_set)

    return timepix_dict

########################################################

# test from file
def timepix_parser_test():
    # file is "timepix_fake_log.txt"
    with open('/Users/kris/Downloads/timepix_fake_log.txt','rb') as f: 
        data = f.read()

    # Savannah's code directly
    rec_ff_unix = data[0:6] #first 6 bytes 
    rec_flag_byte = data[6:7] #7th byte 
    rec_read_hk = data[7:34]
    rec_read_rates_bytes = data[34:]

    #undo flag bytes 
    byte_value = rec_flag_byte  # Corrected byte value creation
    flags_set = get_flags_from_byte(byte_value[0])

    #undo the hk_packet 
    received_data = unpack_read_all_hk_packet(rec_read_hk)

    read_rates_data = unpack_read_rates_packet(rec_read_rates_bytes)
    mean_tot = read_rates_data.mean_tot
    flx_rate = read_rates_data.flx_rate

    # Modified code into one parser
    timepix_data = timepix_parser(byte_data=data)

    # now check that both agree
    assert timepix_data["unixtime"]==rec_ff_unix, "Unixtime does not match."
    assert timepix_data["board_t1"]==received_data.board_t1, "Board T1 does not match."
    assert timepix_data["board_t2"]==received_data.board_t2, "Board T2 does not match."
    assert timepix_data["asic_voltages"]==received_data.asic_voltages, "ASIC Voltages does not match."
    assert timepix_data["asic_currents"]==received_data.asic_currents, "ASIC Curents does not match."
    assert timepix_data["fpga_voltages"]+[timepix_data["fpga_temp"]]==received_data.fpga_values, "FPGA Voltages does not match."
    assert timepix_data["storage_fill"]==received_data.rpi_storage_fill, "Storage Fill does not match."
    assert timepix_data["mean_tot"]==mean_tot, "Mean TOT does not match."
    assert timepix_data["flx_rate"]==flx_rate, "Flux Rate does not match."
    assert timepix_data["flags"]==flags_set, "Flags does not match."
    print("Timepix test passed.")


if __name__=="__main__":
    timepix_parser_test()

    ## original Savannah's runnign code
    # with open('./timepix_fake_log.txt','rb') as f: 
    #     data = f.read()

    # print("length of data frame from text log :",len(data))


    # rec_ff_unix = data[0:6] #first 6 bytes 
    # rec_flag_byte = data[6:7] #7th byte 
    # rec_read_hk = data[7:34]
    # rec_read_rates_bytes = data[34:]

    # print("rec'd values: ")
    # print("rec_ff_unix:",rec_ff_unix)
    # print("rec_flag_byte:", rec_flag_byte)
    # print("rec_read_hk:",rec_read_hk)
    # print("rec_read_rates:",rec_read_rates_bytes)

    # #undo flag bytes 

    # byte_value = rec_flag_byte  # Corrected byte value creation
    # flags_set = get_flags_from_byte(byte_value[0])
    # print("Rec'd flags set:", flags_set)

    # #undo the hk_packet 
    # received_data = unpack_read_all_hk_packet(rec_read_hk)#(read_all_hk_packet)
    # print("Received Board T1:", received_data.board_t1)
    # print("Received Board T2:", received_data.board_t2)
    # print("Received ASIC Voltages:", received_data.asic_voltages)
    # print("Received ASIC Currents:", received_data.asic_currents)
    # print("Received FPGA Voltages:", received_data.fpga_values)
    # print("Received RPI Storage Fill:", received_data.rpi_storage_fill)

    # read_rates_data = unpack_read_rates_packet(rec_read_rates_bytes)
    # mean_tot = read_rates_data.mean_tot
    # flx_rate = read_rates_data.flx_rate
    # print("Mean Tot:", mean_tot)
    # print("Flx Rate:", flx_rate)


    # print("check all flags:")
    # defined_flag(flags_set)

    # print("____________")

    # print("check_hvps function:")
    # check_hvps(flags_set)

    ## ABOVE'S OUTPUT
    # length of data frame from text log : 38
    # rec'd values: 
    # rec_ff_unix: b'\r\x00e\x89V\t'
    # rec_flag_byte: b'\x04'
    # rec_read_hk: b'\xfa\x00,\x0190\x1d\t\xa0[\xe8\x03\x9e*\xe9\x03\x06\xeb\xfb\t.\x16\x85\x1ac\x00\n'
    # rec_read_rates: b'\x88\x13|\x15'
    # Rec'd flags set: [2]
    # Received Board T1: 250
    # Received Board T2: 300
    # Received ASIC Voltages: [12345, 23456, 10910, 60166]
    # Received ASIC Currents: [2333, 1000, 1001, 2555]
    # Received FPGA Voltages: [5678, 6789, 99]
    # Received RPI Storage Fill: 10
    # Mean Tot: 5000
    # Flx Rate: 5500
    # check all flags:
    # Flags are set:
    # Software Error
    # ____________
    # check_hvps function:
    # hvps off

