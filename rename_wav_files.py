
# renames files in the current directory 
# that match the pattern "segiment*.wav" to "segment_YYYYMMDD_HHMMSS.wav" 
# based on their last modification time.
# actually quite useful, but you'll have to change the glob pattern to match your files, 
# and make sure the new name format is what you want. Notice that this is
# also serving to fix a typo in the original pattern ("segiment" instead of "segment").
# my bad, but also my good 'cause I fixed it with this program. Now you can, too.
#
# NOTE that the ft8decode.sh script expects the files to be named "segment_YYYYMMDD_HHMMSS.wav" which
# matches what this script does, so you have a bunch of old WAV files of FT8 recordings,
# this will help.
#

import os,sys
from datetime import datetime, timezone

from glob import glob

wavfiles = glob("segiment*.wav")

for wavfile in wavfiles:
    modtime = os.path.getmtime(wavfile)
    dt = datetime.fromtimestamp(modtime, timezone.utc)
    newname = "segment_"+dt.strftime("%Y%m%d_%H%M%S") + ".wav"
    if wavfile != newname:
        os.rename(wavfile, newname)


