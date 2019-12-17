# fast-zwo
Minimal Python wrapper for ZWO ASI cameras

## Requirements

libusb

### MacOS

Install ASICAP from ZWO and point to: 
`/Applications/ASICAP.app/Contents/MacOS/libASICamera2.dylib.1.14.0425`

## Running it

Go to where you want to run it:

`cd /Volumes/Drive`

Copy `asi.py` and `mq_obs_run.py` to that location.

Edit parameters:
`max_files=3, max_bytes=50e6, exptime=0.005 * u.second, gain=300.`
at the very end of: `mq_obs_run.py`

Run it:

`python mq_obs_run.py`

To stop running, wait until the specified # of files are created or do: Ctrl+C



