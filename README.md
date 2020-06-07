# Multi-threaded File Downloader

<badges>[![version](https://img.shields.io/pypi/v/mfd.svg)](https://pypi.org/project/mfd/)
[![license](https://img.shields.io/pypi/l/mfd.svg)](https://pypi.org/project/mfd/)
[![pyversions](https://img.shields.io/pypi/pyversions/mfd.svg)](https://pypi.org/project/mfd/)  
[![donate](https://img.shields.io/badge/Donate-Paypal-0070ba.svg)](https://paypal.me/foxe6)
[![powered](https://img.shields.io/badge/Powered%20by-UTF8-red.svg)](https://paypal.me/foxe6)
[![made](https://img.shields.io/badge/Made%20with-PyCharm-red.svg)](https://paypal.me/foxe6)
</badges>

<i>Useful for downloading files from servers which does not throttle bandwidth of each connection as long as that total bandwidth does not exceed ISP caps.</i>

<u>No cookie or session support.</u>

```
Example:
ISP cap: 2MBps
File server bandwidth per connection: 2MBps
Number of connections: 8
Expected download speed per connection: 256KBps
Expected download speed of the file: 2MBps
Download speed is capped by ISP

ISP cap: 10MBps
File server bandwidth per connection: 1MBps
Number of connections: 8
Expected download speed per connection: 1MBps
Expected download speed of the file: 8MBps
Download speed is capped by file server, can be enhanced by using more connections (which may be limited by the file server)
```

# Hierarchy

```
mfd
'---- MFD()
    |---- download()
    |---- retry_download() 
    '---- stop()
```

# Example

## python
<u>MFD() is not thread-safe.  
Do not use the same MFD() instance in threads.</u>
```python
from mfd import MFD
mfd = MFD(
    # file saving directory
    save_dir="I:\\test",
    # piece size of each download connection
    # adjust with hard disk speed and Internet bandwidth
    # size in bytes
    piece_size=1024*1024*(2**4),
    # number of retry when a piece is failed to download
    retry=2
)
info = mfd.download(
    # file url
    url="direct download url",
    # number of download connections
    connections=2**3,
    # whether to calculate SHA1 after downloading
    cal_hash=False
)
print(info)
# {"file_path": "I:\\test\\file"}
# {"file_path": "I:\\test\\file", "sha1": "checksum"}
# if it is failed to download after the specified retries,
# an exception is raised
# additional retry can be like this
try:
    mfd.download(...)
except: 
    mfd.retry_download(
        # number of download connections
        connections=2**3
    )
# necessary to stop the downloader after downloading
mfd.stop()
```
