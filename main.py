# /usr/bin/python3

from font_source_sans_pro import SourceSansProSemibold
from PIL import Image, ImageFont, ImageDraw
from securedata import securedata, mail
from inky.auto import auto
from inky import InkyWHAT
import traceback
import requests
import argparse
import datetime
import json
import os

# variables
source_directory = os.path.dirname(os.path.realpath(__file__)) + "/"
source_directory_resources = source_directory + "resources/"
secure_data_directory = securedata.getConfigItem("path_securedata")

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--color', '-c', type=str, required=False,
                    choices=["red", "black", "yellow"], help="ePaper display color")
args = parser.parse_args()

color = args.color or "red"

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


def getCoinPrice():
    endpoint = "https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD"
    latest_price_stored = securedata.getFileAsArray(
        "BTC_LATEST_PRICE", ignoreNotFound=True) or ['0']
    try:
        r = requests.get(endpoint)
        json_data = r.text

        if json_data and len(json_data) > 0:
            fj = json.loads(json_data)
            latest_price_float = fj["result"]["XXBTZUSD"]["c"][0]
            print(f"Found price: {latest_price_float}")
            securedata.writeFile("BTC_LATEST_PRICE", content=latest_price_float)
            return "{:.2f}".format(float(latest_price_float))
    except KeyError:
        print("API - KeyError")
        print(f"Returning {latest_price_stored[0]}")
        return latest_price_stored[0]


# load securedata
planty_status = securedata.getItem("planty", "status")
weather_data = securedata.getItem("weather", "data")

# steps
steps = 'No steps found'
steps_data = securedata.getFileAsArray('steps.md', secure_data_directory)
if len(steps_data) > 0:
    steps = f"{steps_data[0]} today"

# load images
img_btc = Image.open(source_directory_resources + "btc.png")
img_plant_inside = Image.open(
    source_directory_resources + "icon-plant-inside.png")
img_plant_outside = Image.open(
    source_directory_resources + "icon-plant-outside.png")
img_plant_unknown = Image.open(
    source_directory_resources + "icon-plant-unknown.png")
img_weather = Image.open(source_directory_resources +
                         f"weather/{weather_data['current_conditions_icon']}.png")

# temperature
temperature = weather_data.get('current_temperature') or "--"
temperature_font_size = 95

if type(temperature) == int and (temperature >= 100 or temperature <= -10):
    temperature_font_size = 80

# load fonts
font_baseline = ImageFont.truetype(SourceSansProSemibold, 24)
font_header = ImageFont.truetype(SourceSansProSemibold, 35)
font_price = ImageFont.truetype(SourceSansProSemibold, 55)
font_steps = ImageFont.truetype(SourceSansProSemibold, 40)
font_price_label = ImageFont.truetype(SourceSansProSemibold, 20)
font_temperature = ImageFont.truetype(
    SourceSansProSemibold, temperature_font_size)
font_divider = ImageFont.truetype(SourceSansProSemibold, 70)

# add elements to backdrop
try:
    print("Drawing...")
    draw.text((20, 60), steps, inky_display.BLACK, font=font_steps)
    draw.text((20, 0), f"BTC ${str('{:,.2f}'.format(float(getCoinPrice())))}",
              inky_display.BLACK, font=font_price)
    draw.text((20, 130), f"{temperature}°",
              inky_display.BLACK, font=font_temperature)
    img.paste(img_weather, (170, 160))

    draw.text((265, 145), "|", inky_display.RED, font=font_divider)
    draw.text((20, 260), f"Updated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
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
