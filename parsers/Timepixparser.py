#flag_function_tpx_ex.py
import sys, os
from matplotlib import pyplot as plt
import numpy as np



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

    # Board temps
    data.board_t1 = packet[0] + (packet[1] << 8)
    data.board_t2 = packet[2] + (packet[3] << 8)

    # ASIC voltages and currents
    for i in range(4):
        voltage = packet[4 + i * 4] + (packet[5 + i * 4] << 8)
        current = packet[6 + i * 4] + (packet[7 + i * 4] << 8)
        data.asic_voltages[i] = voltage
        data.asic_currents[i] = current

    # FPGA values
    for i in range(3):
        data.fpga_values[i] = packet[20 + i * 2] + (packet[21 + i * 2] << 8)

    # RPI storage fill - read from byte 26
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


def timepix_hk_parser(byte_data):
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
    rec_ff_unix = byte_data[2:6] 
    timepix_dict["unixtime"] = int.from_bytes(rec_ff_unix, byteorder='big')
    rec_flag_byte = byte_data[6] #7th byte 
    rec_read_hk = byte_data[7:34]
    rec_read_rates_bytes = byte_data[34:]

    # undo flag bytes
    flags_set = get_flags_from_byte(rec_flag_byte)

    # undo the hk_packet and get info
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

NUM_PHOTONS = 360
NUM_PCAPS = 4

def unpack_photon(data_bytes):
    val = int.from_bytes(data_bytes, byteorder="big")
    x     = (val >> 23) & 0x1FF
    y     = (val >> 14) & 0x1FF
    tot   = (val >> 4)  & 0x3FF
    spare = val & 0xF
    return x, y, tot, spare

def timepix_pc_parser(packet_bytes):
    """ parse a single frame (1440 bytes) of Timepix photon-counting data and output a np structured array."""
    if len(packet_bytes) != NUM_PHOTONS * 4:
        raise ValueError("Packet size is " + str(len(packet_bytes)) + ", not 1440 bytes")
    xs, ys, tots, spares = [], [], [], []
    for i in range(NUM_PHOTONS):
        x, y, tot, spare = unpack_photon(packet_bytes[i*4:i*4+4])
        xs.append(x)
        ys.append(y)
        tots.append(tot)
        spares.append(spare)
    
    # adapted from Savannah's code to store outputs in an np structured array:
    dt = np.dtype({'names': ('x', 'y', 'tot', 'spare'),
                   'formats': ('u2', 'u2', 'u2', 'u2')})
    df = np.zeros(NUM_PHOTONS, dtype=dt)
    df['x'] = np.array(xs, dtype=np.uint16)
    df['y'] = np.array(ys, dtype=np.uint16)
    df['tot'] = np.array(tots, dtype=np.uint16)
    df['spare'] = np.array(spares, dtype=np.uint16)
    return df

def unpack_pcap_size(data_bytes):
    """Unpack 2 bytes into a PCAP size (uint16)."""
    if len(data_bytes) != 2:
        raise ValueError("Data length must be exactly 2 bytes")
    return int.from_bytes(data_bytes, byteorder="big")

def timepix_pcap_parser(packet_bytes):
    """Unpack 8-byte packet into 4 PCAP sizes (uint16)."""
    expected_len = NUM_PCAPS * 2
    if len(packet_bytes) != expected_len:
        raise ValueError(f"Packet size must be {expected_len} bytes")
    sizes = []
    for i in range(NUM_PCAPS):
        size = unpack_pcap_size(packet_bytes[i*2:i*2+2])
        sizes.append(size)
    return np.array(sizes, dtype=np.uint16)


########################################################

# test from file
def timepix_hk_parser_test(path:str):
    # file is "timepix_fake_log.txt"
    with open(path,'rb') as f: 
        data = f.read()
        data = data[0:38]

    # Savannah's code directly
    rec_ff_unix = int.from_bytes(data[2:6], byteorder='big')
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
    timepix_data = timepix_hk_parser(byte_data=data)

    import pprint
    pprint.pprint(timepix_data)

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

def timepix_pc_parser_check(path:str):
    """ A visual check of confirm the timepix_pc.log file """
    with open(path, 'rb') as pc_f:
        pc_d = pc_f.read()
        # select only the first frame (1440 bytes) of data for plotting:
        this_pc = pc_d[0:NUM_PHOTONS*4]

        # parse it:
        pc = timepix_pc_parser(this_pc)

        print('x range:\t', np.min(pc['x']), np.max(pc['x']))
        print('y range:\t', np.min(pc['y']), np.max(pc['y']))
        print('tot range:\t', np.min(pc['tot']), np.max(pc['tot']))
                
        fig, ax = plt.subplots()
        
        scat = ax.scatter(pc['x'], pc['y'], c=pc['tot'], cmap='plasma')
        ax.set_aspect('equal', 'box')
        ax.set_xlabel('pixel x')
        ax.set_ylabel('pixel y')
        ax.set_title('Timepix event data image sample')
        bar = fig.colorbar(scat, ax=ax, location='right')
        bar.ax.set_title('ToT')
        plt.show()

def timepix_pcap_parser_check(path:str):
    with open(path, 'rb') as pc_f:
        pc_d = pc_f.read()
        # select only the first frame (8 bytes) of data for printing:
        these_pcaps = pc_d[6:6+NUM_PCAPS*2]
        pcaps = timepix_pcap_parser(these_pcaps)
        print("pcap sizes: ", pcaps)



if __name__=="__main__":
    if len(sys.argv) != 2:
        print("pass the path to directory containing timepix log files.")
        sys.exit(1)

    pc_name = 'timepix_pc.log'
    pcap_name = 'timepix_pcap.log'
    hk_name = 'timepix_tpx.log'

    # Event data:
    pc_path = os.path.join(sys.argv[1], pc_name)
    pcap_path = os.path.join(sys.argv[1], pcap_name)
    hk_path = os.path.join(sys.argv[1], hk_name)

    timepix_hk_parser_test(hk_path)
    timepix_pcap_parser_check(pcap_path)
    timepix_pc_parser_check(pc_path)

    # todo: include pcap test.
