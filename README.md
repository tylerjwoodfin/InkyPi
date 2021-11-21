# InkyPi
Little experiments for my Inky wHAT e-ink display (https://thepihut.com/products/inky-what-epaper-eink-epd)

Source for Bitcoin tracker: Naviavia - https://github.com/naviavia/bitcoin_ticker

## Dependencies
This project is not self-sustained and is published for academic purposes rather than "cloning and running". It relies on certain files from the dependencies below.
    
- [Inky wHAT e-ink display](https://thepihut.com/products/inky-what-epaper-eink-epd)
- [Secure Data](https://github.com/tylerjwoodfin/SecureData)
    - Used to store project data across multiple repos and provides easy file access
- Something running that populates the files mentioned in `main.py`, such as [Raspberry Pi Tools](https://github.com/tylerjwoodfin/RaspberryPI-Tools) and a crontab that runs the weather scripts within
- [rclone](https://rclone.org/install/) (optional)
    - Used to sync data between local devices and cloud repos, such as Dropbox

## Sources
[Bitcoin Ticker from Naviavia](https://github.com/naviavia/bitcoin_ticker)
    - "soft-forked" from this repo as a starting point, then modified heavily to fit my needs