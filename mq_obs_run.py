import time

from asi import ASICamera

from astropy.io import fits

import numpy as np

def frame_rate_test(camera, max_bytes=500e6, output_fits_name='out.fits'):
    if path.exists(output_fits_name):
        print(f'fits file already exists: {output_fits_name}\n EXITING')
        return

    bits_per_pixel = 16 # bits
    dimen_y = 5496
    dimen_x = 3672
    total_pixels = dimen_y * dimen_x
    total_memory_bits = bits_per_pixel * total_pixels
    total_memory_bytes = total_memory_bits / 8.
    print(total_memory_bytes)

    start_time = time.monotonic()
    camera.start_video_capture()

    image_data_list = []

    count = 0

    try:
        while True:
            image = camera.get_video_data()
            image_data_list.append(image)

            count += 1

            if count * total_memory_bytes > max_bytes:
                break

            if count % 1000 == 0:
                end_time = time.monotonic()
                fps = n / (end_time - start_time)
                msg = "Got {} frames in {} seconds ({} fps).".format(n, (end_time - start_time), fps)
                print(msg)

    except KeyboardInterrupt:
        print('Cancelled run')
    end_time = time.monotonic()
    camera.stop_video_capture()
    fps = n / (end_time - start_time)
    msg = "Got {} frames in {} seconds ({} fps).".format(n, (end_time - start_time), fps)
    print(msg)


    image_data_array = np.array(image_data_list)
    hdu = fits.PrimaryHDU(image_data_array)
    hdu.writeto(output_fits_name)


if __name__ == '__main__':
    camera = ASICamera(library_path='/Applications/ASICAP.app/Contents/MacOS/libASICamera2.dylib')
    print("Collect data at MQ Observatory:")
    frame_rate_test(camera, max_bytes=500e6, output_fits_name='out.fits')
