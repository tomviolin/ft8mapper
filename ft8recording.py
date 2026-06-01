#!/usr/bin/env python3

import subprocess, struct, scipy.io.wavfile, numpy as np
from scipy.io import wavfile
import time
from  datetime import datetime, timezone
import os,sys
print("wait for the start of the next 15 second interval to start recording")
while datetime.now().second % 15 != 0:  # Wait until the start of the next 15 second interval
    time.sleep(0.005)

# rtl_fm -f 7074000 -s 12000 -M usb - | 

proc = subprocess.Popen(['rtl_fm', '-f', '7074000', '-s', '12000', '-M', 'usb', '-'], stdout=subprocess.PIPE)  # Use rtl_fm to capture the signal and pipe it to the script


wavdata = b''


while True:
    chunk = proc.stdout.read(12000)  # Read 12 s16le samples (1 ms of data at 12000 samples/sec
    print(type(chunk), len(chunk))
    if not chunk:
        break
    # Process the data as needed
    print('.', end='', flush=True)  # Print a dot to indicate progress

    wavdata += chunk
    timedate = datetime.now(timezone.utc)
    stamptime = int(timedate.timestamp())
    timestamp = timedate.strftime("%Y%m%d_%H%M%S")
    print (f'\nCollected {len(wavdata)} samples so far at {stamptime % 15:d} seconds into the current 15 second interval')
    # check if we are in the first second of the current 15 second interval.
    if ((stamptime % 15) == 0) and (len(wavdata) > 100000):  # checking for a bit less than 15 seconds of data in case of clock drift
        print(wavdata[:10])
        # save the wavdata to a file 
        print(f'\nSaving segment_{timestamp}.wav with {len(wavdata)} samples')
        if len(wavdata) % 2 == 0:
            os.makedirs('segments', exist_ok=True)
            wavfile.write(f'segments/segment_{timestamp}.wav', 12000, np.frombuffer(wavdata, '<i2'))
        # clear the wavdata
        wavdata = b''

