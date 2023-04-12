# /usr/bin/python3

"""
Displays the temperature and other prudent information on an e-ink screen; see README.md for details
"""

import os
import sys
import json
import traceback
import argparse
import datetime
from datetime import datetime
import requests
from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from cabinet import Cabinet, mail
from font_source_sans_pro import SourceSansProSemibold

cab = Cabinet()

def get_latest_weather_file():
    """
    Get the name of the latest weather file in the 'weather' folder of cabinet.

    Returns:
        str: The name of the latest file in the format 'weather YYYY-MM-DD.json',
        or None if no such file is found.

    Raises:
        None.
    """
    folder_path = cab.path_cabinet + "/weather"

    # Get a list of all files in the folder
    try:
        files = os.listdir(folder_path)
    except FileNotFoundError:
        cab.log(f"No weather files found in {folder_path}")
        return None

    # Filter out any files that don't start with "weather "
    files = [f for f in files if f.startswith("weather ")]

    # Convert the file names to datetime objects
    dates = [datetime.strptime(f[8:-5], "%Y-%m-%d") for f in files]

    # Get the index of the latest date
    latest_index = dates.index(max(dates))

    # Get the name of the latest file
    latest_file = files[latest_index]

    return latest_file or -1

# variables
TODAY = str(datetime.today().strftime('%Y-%m-%d'))
directory_source = os.path.dirname(os.path.realpath(__file__)) + "/"
directory_resources = directory_source + "resources/"
FILE_WEATHER_ARRAY = cab.get_file_as_array(
    get_latest_weather_file(), cab.path_cabinet + "/weather", ignore_not_found=True)

if FILE_WEATHER_ARRAY is None:
    cab.log(f"Could not find `weather {TODAY}.json`")
    sys.exit(-1)

FILE_WEATHER = ''.join(FILE_WEATHER_ARRAY)

# filter trailing comma, if needed
if FILE_WEATHER.endswith(','):
    FILE_WEATHER = FILE_WEATHER[:-1]

FILE_WEATHER = f"[{FILE_WEATHER}]"

# get weather inside
file_weather_inside = json.loads(FILE_WEATHER)
temperature_in_c = file_weather_inside[-1]["temperature"] or 537.222
temperature_in = round(temperature_in_c * 9/5 + 32, 1)

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--color', '-c', type=str, required=False,
                    choices=["red", "black", "yellow"], help="ePaper display color")
ARGS = parser.parse_args()

color = ARGS.color or "red"

# Set up the correct display and scaling factors
print("Checking for InkyWHAT...")
inky_display = InkyWHAT(color)
print("Found!")
inky_display.set_border(inky_display.WHITE)
# inky_display.set_rotation(180)

w = inky_display.WIDTH
h = inky_display.HEIGHT

# Create a new canvas to draw on

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# get current BTC price from Kraken API


def get_coin_price():
    """
    gets the current Bitcoin price
    """

    endpoint = "https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD"
    latest_price_stored = cab.get_file_as_array(
        "BTC_LATEST_PRICE", ignore_not_found=True) or ['0']
    try:
        response = requests.get(endpoint, timeout=30)
        json_data = response.text

        if json_data and len(json_data) > 0:
            json_data_formatted = json.loads(json_data)
            latest_price_float = json_data_formatted["result"]["XXBTZUSD"]["c"][0]
            print(f"Found price: {float(latest_price_float):,.2f}")
            cab.write_file("BTC_LATEST_PRICE", content=latest_price_float)
            return f"{float(latest_price_float):,.2f}"

    except (KeyError, requests.exceptions.Timeout) as error:
        print("API - KeyError", error)
        print(f"Returning {latest_price_stored[0]}")
        return latest_price_stored[0]


# load cabinet
planty_status = cab.get("planty", "status")
weather_data = cab.get("weather", "data")

# steps
STEPS = 'No steps found'
steps_data = cab.get_file_as_array('steps.md', cab.path_cabinet)
if len(steps_data) > 0:
    STEPS = f"{steps_data[0]} today"

# load images
img_btc = Image.open(directory_resources + "btc.png")
img_plant_inside = Image.open(
    directory_resources + "icon-plant-inside.png")
img_plant_outside = Image.open(
    directory_resources + "icon-plant-outside.png")
img_plant_unknown = Image.open(
    directory_resources + "icon-plant-unknown.png")
img_weather = Image.open(directory_resources +
                         f"weather/{weather_data['current_conditions_icon']}.png")

# temperature
temperature_out = weather_data.get('current_temperature') or "--"
TEMPERATURE_FONT_SIZE = 50

if isinstance(temperature_out, int) and (temperature_out >= 100 or temperature_out <= -10):
    TEMPERATURE_FONT_SIZE -= 15

TEMPERATURE_FONT_SIZE_OUTSIDE = TEMPERATURE_FONT_SIZE + 30

# load fonts
font_baseline = ImageFont.truetype(SourceSansProSemibold, 24)
font_header = ImageFont.truetype(SourceSansProSemibold, 35)
font_price = ImageFont.truetype(SourceSansProSemibold, 55)
font_steps = ImageFont.truetype(SourceSansProSemibold, 40)
font_price_label = ImageFont.truetype(SourceSansProSemibold, 20)
font_temperature = ImageFont.truetype(
    SourceSansProSemibold, TEMPERATURE_FONT_SIZE)
font_temperature_outside = ImageFont.truetype(
    SourceSansProSemibold, TEMPERATURE_FONT_SIZE_OUTSIDE)
font_divider = ImageFont.truetype(SourceSansProSemibold, 70)

# add elements to backdrop
try:
    print("Drawing...")
    draw.text((20, 60), STEPS, inky_display.BLACK, font=font_steps)
    draw.text((20, 0), f"BTC ${get_coin_price()}",
              inky_display.BLACK, font=font_price)
    draw.text((40, 100), f"{temperature_out}°",
              inky_display.BLACK, font=font_temperature_outside)
    draw.text((40, 190), f"{temperature_in}°",
              inky_display.RED, font=font_temperature)
    img.paste(img_weather, (170, 160))

    draw.text((265, 145), "|", inky_display.RED, font=font_divider)
    draw.text((20, 260), f"Updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
              inky_display.BLACK, font=font_baseline)
    if planty_status == 'in':
        img.paste(img_plant_inside, (300, 160))
    elif planty_status == 'out':
        img.paste(img_plant_outside, (300, 160))
    else:
        img.paste(img_plant_unknown, (300, 160))
except Exception as e:
    traceback.print_exc()
    mail.send("InkyPi Error", traceback.format_exc())
    draw.text((20, 25), f"Error:\n{e}", inky_display.RED, font=font_baseline)

# display
inky_display.set_image(img)
inky_display.show()
