# Multi-threaded File Downloader

<badges>[![version](https://img.shields.io/pypi/v/mfd.svg)](https://pypi.org/project/mfd/)
[![license](https://img.shields.io/pypi/l/mfd.svg)](https://pypi.org/project/mfd/)
[![pyversions](https://img.shields.io/pypi/pyversions/mfd.svg)](https://pypi.org/project/mfd/)  
[![donate](https://img.shields.io/badge/Donate-Paypal-0070ba.svg)](https://paypal.me/foxe6)
[![powered](https://img.shields.io/badge/Powered%20by-UTF8-red.svg)](https://paypal.me/foxe6)
[![made](https://img.shields.io/badge/Made%20with-PyCharm-red.svg)](https://paypal.me/foxe6)
</badges>

<i>Useful for downloading files from servers which does not throttle bandwidth of each connection as long as that total bandwidth does not exceed ISP caps.</i>

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
```

# Example

## python
```python

```
