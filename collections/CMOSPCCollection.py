"""
CMOS collection to handle the read-in CMOS data.
"""
import os
import numpy as np
import matplotlib.pyplot as plt


class CMOSPCCollection:
    """
    A container for CMOS data after being parsed.
    
    Can be used to generate spectrograms or images.
    
    Paramters
    ---------
    parsed_data : `tuple`, length 4
            Contains `linetime`, `gain`, `exposure_pc`, and `pc_images` as 
            returned from the parser.

    old_data_time : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            
    Example
    -------
    with BackwardsReader(file=self.data_file, blksize=self.buffer_size, forward=True) as f:
        data = f.read_block()
        linetime, gain, exposure_pc, pc_image = PCimageData(raw_data)
        
    cmos_data = CMOSPCCollection((linetime, gain, exposure_pc, pc_image))
    
    plt.figure(figsize=(12,8))
    cmos_data.plot_image()
    plt.show()
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.linetime, self.gain_pc, self.exposure_pc, self._image = parsed_data

        self.whole_photon_rate_threshold = 60 # np.mean(self._image)
        
        # used in the filter to only consider data with times > than this
        self.last_data_time = old_data_time

        if not self.new_array():
            self._image = self.empty()

    def empty(self):
        """ Define what an empty return should be. """
        return np.zeros((384,768))
    
    def new_array(self):
        """ Check if the array is new or a repeat. """
        return True
        # previously was
        # if self.linetime>self.last_data_time:
        #     return True
        # return False
    
    def image_array(self):
        """
        Method to return the image array of the parser output.

        Returns
        -------
        `np.ndarray` :
            The image array.
        """
        im = self._image
        return im
    
    def plot_image(self):
        """
        Method to plot the image of the CMOS file.

        Returns
        -------
        `matplotlib.pyplot.imshow`:
            The object which holds the plot.
        """

        i = plt.imshow(self.image_array(), 
                       rasterized=True, 
                       origin="lower")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("CMOS Image")
        
        return i
    
    def get_exposure(self):
        """ Return the exposure time of PC image. """
        print("Do not use CMOSPCCollection's get_exposure, it is wrong I say!")
        return self.exposure_pc
    
    def get_gain(self):
        """ Return the exposure time of PC image. """
        print("Do not use CMOSPCCollection's get_gain, it is wrong I say!")
        return self.gain_pc
    
    def get_whole_photon_rate(self):
        """ Fraction of PC pixels over a threshold to all pixels"""
        return np.sum(self._image>self.whole_photon_rate_threshold)/self._image.size
    
    def get_whole_photon_rate_bkg_sub(self, bkg):
        """ Fraction of PC pixels over a threshold to all pixels"""
        return np.sum((self._image-bkg)>self.whole_photon_rate_threshold)/self._image.size
    
def det_pc_edges():
    """ 
    Function to define the physical sizes of the CMOS PC image. 
    
    In cm.
    """
    x1, x2, y1, y2 = 0, 0.8448, 0, 0.4224 # cm
    return x1, x2, y1, y2

def det_pc_arcminutes():
    """ 
    Function to define the physical sizes of the CMOS PC pixels. 
    
    Returns the edges as arcminutes from centre.
    """
    x_pixels, y_pixels = 768, 384

    arcsec_per_pix = 1 

    x_arcmin, y_arcmin = x_pixels*arcsec_per_pix/60, y_pixels*arcsec_per_pix/60
    
    return -x_arcmin/2, x_arcmin/2, -y_arcmin/2, y_arcmin/2

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
DARK_FRAME_DIR = FILE_DIR+"/../data/cmos_dark_frame/"

def get_cmos1_pc_ave_background():
    """ Return the dark PC frame for CMOS 1. """
    return np.load(DARK_FRAME_DIR+"cmos1-pc-bkg-from-mar20-run16.npy")

def get_cmos2_pc_ave_background():
    """ Return the dark PC frame for CMOS 2. """
    return np.load(DARK_FRAME_DIR+"cmos2-pc-bkg-from-mar20-run16.npy")

CMOS1_PC_AVE_BACKGROUND = get_cmos1_pc_ave_background()
CMOS2_PC_AVE_BACKGROUND = get_cmos2_pc_ave_background()