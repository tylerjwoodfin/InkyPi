# /usr/bin/python3

import requests
import json
import argparse
from PIL import Image, ImageFont, ImageDraw
import os
from font_source_sans_pro import SourceSansProSemibold
import datetime
from inky.auto import auto
from securedata import securedata

# variables
source_directory = os.path.dirname(os.path.realpath(__file__)) + "/"
source_directory_resources = source_directory + "resources/"
secure_data_directory = securedata.getConfigItem("securePath")

inky_display = inky_display = auto(ask_user=True, verbose=True)
inky_display.set_border(inky_display.WHITE)

# see documentation for how to change `cloud`
cloud = "Dropbox:SecureData/settings.json"

# pull from cloud
os.system(f"rclone copyto {cloud} {secure_data_directory}/settings.json")

# parse flip arguments
parser = argparse.ArgumentParser()
parser.add_argument('--flip', '-f', type=str, help="true = screen is flipped")
parser.add_argument('--pair', '-p', type=str, help="Enter currency pair")
parser.add_argument('--debug', '-d', type=str, help="true = enable debug")
args, _ = parser.parse_known_args()

# get current BTC price from Kraken API
def getCoinPrice():
    endpoint = "https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD"
    try:
        r = requests.get(endpoint)
        json_data = r.text
        fj = json.loads(json_data)
        lastpriceFloat = fj["result"]["XXBTZUSD"]["c"][0]
        return "{:.2f}".format(float(lastpriceFloat))
    except requests.ConnectionError:
        print("API - ERROR")

#Flip screen is false argument not passed
if args.flip != "false":
    inky_display.h_flip = True
    inky_display.v_flip = True

# load SecureData
planty_status = securedata.getItem("planty", "status")
weather_data = securedata.getItem("weather", "data")

# load images
img_btc = Image.open(source_directory_resources + "btc.png")
img_plant_inside = Image.open(source_directory_resources + "icon-plant-inside.png")
img_plant_outside = Image.open(source_directory_resources + "icon-plant-outside.png")
img_plant_unknown = Image.open(source_directory_resources + "icon-plant-unknown.png")
img_weather = Image.open(source_directory_resources + f"weather/{weather_data['current_conditions_icon']}.png")

# create backdrop
img = Image.open(source_directory_resources + "backdrop.png").resize(inky_display.resolution)
draw = ImageDraw.Draw(img)

# load fonts
font_baseline = ImageFont.truetype(SourceSansProSemibold, 24)
font_header = ImageFont.truetype(SourceSansProSemibold, 35)
font_price = ImageFont.truetype(SourceSansProSemibold, 55)
font_price_label = ImageFont.truetype(SourceSansProSemibold, 20)
font_temperature = ImageFont.truetype(SourceSansProSemibold, 95)
font_divider = ImageFont.truetype(SourceSansProSemibold, 70)

# add elements to backdrop
try:
    draw.text((20, 0), f"BTC ${str('{:,.2f}'.format(float(getCoinPrice())))}", inky_display.BLACK, font=font_price)
    draw.text((20, 65), f"Updated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", inky_display.BLACK, font=font_baseline) 
    
    draw.text((20, 160), f"{weather_data['current_temperature']}°", inky_display.BLACK, font=font_temperature)
    img.paste(img_weather, (170,190))
    

    draw.text((265, 175), "|", inky_display.RED, font=font_divider)
    if planty_status == 'in':
        img.paste(img_plant_inside, (300, 190))
    elif planty_status == 'out':
        img.paste(img_plant_outside, (300,190))
    else:
        img.paste(img_plant_unknown, (300,190))
except Exception as e:
    draw.text((20, 25), f"Error:\n{e}", inky_display.RED, font=font_price)

# display
inky_display.set_image(img)
inky_display.show()