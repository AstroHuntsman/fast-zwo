# convert numpy npy file to a fits cube

from os import path
import sys
import numpy as np

from astropy.io import fits


def main(npy_filename):
    fits_filename = npy_filename.replace('.npy', '.fits')
    if path.exists(fits_filename):
        print(f"File {fits_filename} already exists, EXITING")

    image_data_list = np.load(npy_filename)
    hdu = fits.PrimaryHDU(image_data_list)
    hdu.writeto(fits_filename)


if __name__ == '__main__':
    npy_filename = sys.argv[1]
    main(npy_filename)
