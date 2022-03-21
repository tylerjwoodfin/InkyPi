# InkyPi

Little experiments for my [Inky wHAT e-ink display](https://thepihut.com/products/inky-what-epaper-eink-epd)

## Hardware Dependencies

- [Inky wHAT e-ink display](https://thepihut.com/products/inky-what-epaper-eink-epd)
- Raspberry Pi (other Linux devices or distros may not work)

## Library Dependencies

This project is not self-sustained and is published for academic purposes rather than "cloning and running". It relies on certain files from the dependencies below.

- [Inky Library](https://learn.pimoroni.com/article/getting-started-with-inky-what)
- [Secure Data](https://github.com/tylerjwoodfin/securedata)
  - Used to store project data across multiple repos and provides easy file access
  - `python -m pip install font-source-sans-pro`
- [font-source-sans-pro](https://pypi.org/project/font-source-sans-pro/)
  - `python -m pip install font-source-sans-pro`
- [rclone](https://rclone.org/install/) (optional)
  - Used to sync data between local devices and cloud repos, such as Dropbox

## Sources

[Bitcoin Ticker from Naviavia](https://github.com/naviavia/bitcoin_ticker) - "soft-forked" from this repo as a starting point, then modified heavily to fit my needs