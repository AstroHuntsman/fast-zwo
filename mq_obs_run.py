import time

from asi import ASICamera

from astropy.io import fits
import astropy.units as u

import numpy as np

from os import path


def frame_rate_test(camera, max_files=2, max_bytes=500e6):

    bits_per_pixel = 16  # bits
    dimen_y = 5496
    dimen_x = 3672
    total_pixels = dimen_y * dimen_x
    total_memory_bits = bits_per_pixel * total_pixels
    total_memory_bytes = total_memory_bits / 8.

    camera.start_video_capture()

    try:

        for i in range(0, max_files):
            output_name = f'out_{i}.npy'
            if path.exists(output_name):
                print(f'Output file already exists: {output_name}\n EXITING')
                return
            start_time = time.monotonic()
            count = 0
            image_data_list = []

            while True:
                image = camera.get_video_data()
                image_data_list.append(image)

                count += 1

                if count * total_memory_bytes > max_bytes:
                    break

                if count % 200 == 0:
                    end_time = time.monotonic()
                    fps = count / (end_time - start_time)
                    msg = "Got {} frames in {} seconds ({} fps).".format(
                        count, (end_time - start_time), fps)
                    print(msg)
            end_time = time.monotonic()

            fps = count / (end_time - start_time)
            msg = "Got {} frames in {} seconds ({} fps).".format(
                count, (end_time - start_time), fps)
            print(msg)

            print(f'Writing to file now: {output_name}')
            write_start_time = time.monotonic()
            np.save(output_name, image_data_list)
            write_end_time = time.monotonic()
            msg = f"Took {write_end_time - write_start_time} seconds to write out a {(total_memory_bytes * count) / 1e9} Gigabyte file: {output_name}"
            print(msg)

    except KeyboardInterrupt:
        print('Cancelled run')
    camera.stop_video_capture()


if __name__ == '__main__':
    camera = ASICamera(library_path='/Applications/ASICAP.app/Contents/MacOS/libASICamera2.dylib',
                       exptime=0.005 * u.second,
                       gain=300.)
    print("Collect data at MQ Observatory:")
    frame_rate_test(camera, max_files=3, max_bytes=5000e6)
