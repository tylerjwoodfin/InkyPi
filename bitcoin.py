# /usr/bin/python3
# bitcoin_ticker v1.1
# Naviavia - https://github.com/naviavia/bitcoin_ticker

import requests
import json
from time import sleep
from inky import InkyPHAT
import argparse
from PIL import Image, ImageFont, ImageDraw
import os
from font_source_sans_pro import SourceSansProSemibold
import datetime
from inky.auto import auto
import sys
import pwd

userDir = pwd.getpwuid( os.getuid() )[ 0 ]

sys.path.insert(0, f'/home/{userDir}/Git/SecureData')
import secureData

# get current COIN price from Kraken API
def getCoinPrice():
    TICKER = API_ENDPOINT + "?pair=" + COIN
    try:
        r = requests.get(TICKER)
        json_data = r.text
        fj = json.loads(json_data)
        lastpriceFloat = fj["result"][COIN]["c"][0]
        return "{:.2f}".format(float(lastpriceFloat))
    except requests.ConnectionError:
        print("API - ERROR")

# variables
CURR_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"
RESOURCES = CURR_DIR + "resources/"
API_ENDPOINT = "https://api.kraken.com/0/public/Ticker"
COIN = "XXBTZUSD"
CURRENCYEXTRACT = "USD"
CURRENCYSYMBOL = "$"
CURRENT_PRICE = getCoinPrice()

inky_display = inky_display = auto(ask_user=True, verbose=True)
inky_display.set_border(inky_display.WHITE)

# parse flip arguments
parser = argparse.ArgumentParser()
parser.add_argument('--flip', '-f', type=str, help="true = screen is flipped")
parser.add_argument('--pair', '-p', type=str, help="Enter currency pair")
parser.add_argument('--debug', '-d', type=str, help="true = enable debug")
args, _ = parser.parse_known_args()

# check for errors
def getError():
    TICKER = API_ENDPOINT + "?pair=" + COIN
    r = requests.get(TICKER)
    json_data = r.text
    fj = json.loads(json_data)
    error = fj["error"]
    return (error)
  
if len(getError())!=0:
    print("Invalid coin pair: " + args.pair)
      
# check for file, if it doesn't exist create, otherwise read file
file_exists = os.path.isfile(CURR_DIR + "/" + "previousprice")

def updatePriceFile():
    f = open(CURR_DIR + "/" + "previousprice", "w")
    f.write(CURRENT_PRICE)
    return float(CURRENT_PRICE)
    
def previousPriceFile():
    if file_exists:
        ObjRead = open(CURR_DIR + "/" + "previousprice", "r")
        return ObjRead.read() or "-1"
        ObjRead.close()
    else:
        print("Price file not found")
        f = open(CURR_DIR + "/" + "previousprice", "w")
        f.write(CURRENT_PRICE)
        return float(CURRENT_PRICE)
        
if len(getError())==0:
    PREVIOUS_PRICE = str(previousPriceFile())
    PREVIOUS_PRICE_COMMAS = "{:,}".format(float(PREVIOUS_PRICE))
    updatePriceFile()
    
# Get price and format
if len(getError())==0:
    COINPRICE = float(CURRENT_PRICE)
    NUMBER_WITH_COMMAS = "{:,.2f}".format(COINPRICE)

#Flip screen is false argument not passed
if args.flip != "false":
    inky_display.h_flip = True
    inky_display.v_flip = True

# load SecureData
planty_status = secureData.variable('PLANTY_STATUS')
weather_data = json.loads(secureData.variable("WEATHER_DATA"))

# load images
if len(getError())==0:
    img_btc = Image.open(RESOURCES + "btc.png")
    img_plant_inside = Image.open(RESOURCES + "icon-plant-inside.png")
    img_plant_outside = Image.open(RESOURCES + "icon-plant-outside.png")
    img_plant_unknown = Image.open(RESOURCES + "icon-plant-unknown.png")
    img_weather = Image.open(RESOURCES + f"weather/{weather_data['current_conditions_icon']}.png")

# load price
if len(getError())==0:
    COINPRICE = f"${NUMBER_WITH_COMMAS}"
    print(COINPRICE)        

# create backdrop
img = Image.open(RESOURCES + "backdrop.png").resize(inky_display.resolution)
draw = ImageDraw.Draw(img)

# load fonts
font_baseline = ImageFont.truetype(SourceSansProSemibold, 24)
font_header = ImageFont.truetype(SourceSansProSemibold, 35)
font_price = ImageFont.truetype(RESOURCES + "fonts/Courierprime.ttf", 40)
font_price_label = ImageFont.truetype(SourceSansProSemibold, 20)
font_temperature = ImageFont.truetype(SourceSansProSemibold, 95)
font_divider = ImageFont.truetype(SourceSansProSemibold, 70)

# add elements to backdrop
if len(getError())==0:
    draw.text((20, 25), f"BTC {str(COINPRICE)}", inky_display.RED, font=font_price)
    draw.text((28, 70), f"Updated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", inky_display.BLACK, font=font_baseline) 
    
    draw.text((28, 160), f"{weather_data['current_temperature']}°", inky_display.BLACK, font=font_temperature)
    img.paste(img_weather, (170,190))
    

    draw.text((265, 175), "|", inky_display.RED, font=font_divider)
    if planty_status == 'in':
        img.paste(img_plant_inside, (300, 190))
    elif planty_status == 'out':
        img.paste(img_plant_outside, (300,190))
    else:
        img.paste(img_plant_unknown, (300,190))

else:
    draw.text((20, 25), "INVALID PAIR", inky_display.RED, font=font_price)

# display
inky_display.set_image(img)
inky_display.show()
