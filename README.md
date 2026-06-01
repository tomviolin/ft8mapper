# ft8mapper
Maps FT8 signals received using RTL-SDR. Creates a static map in one HTML file that uses KeplerGL and another map using Folio.Easily changed to other modes supported by WSJTX.  Requires the RTL-SDR Blog CLI tool "rtl_fm" and the WSJTX CLI tool "jt9".

## quick start:

`git clone` this repo into a working directory.

In one terminal window, `cd` into the working directory and then:

`python3 ft8recording.py`

In a second terminal window, `cd` into the working directory and then:

`bash ft8decode.sh`

You can just run these and they will complain about something missing, which you can then install. Rinse and repeat until it works. Everything needed to run under Linux Mint or Ubuntu should be available in standard distribution repos via `apt` or in the standard Python `pypi` repo. Don't know where to find a dependency? Google will know.

( these are incredibly lame directions. I'll make them better if anyone actually asks me to. )
