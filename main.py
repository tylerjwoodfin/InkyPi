#!/usr/bin/env python3

"""
Displays a random quote and trash duty information on an e-ink screen.
"""

import os
import textwrap
from datetime import datetime, timedelta
from typing import Optional

import requests
from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from font_source_sans_pro import SourceSansProSemibold

# Constants
LAST_UPDATED = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
DIRECTORY_SOURCE = os.path.dirname(os.path.realpath(__file__)) + "/"
DIRECTORY_RESOURCES = DIRECTORY_SOURCE + "resources/"
IMG_TRASH_PATH = DIRECTORY_RESOURCES + "icon-trash.png"
QUOTE_API_URL = "https://zenquotes.io/api/random"

# Load static resources
try:
    IMG_TRASH = Image.open(IMG_TRASH_PATH)
except FileNotFoundError:
    raise RuntimeError(f"Could not load trash icon from {IMG_TRASH_PATH}")

def get_trash_week_owner() -> str:
    """
    Determine whose week it is to take out the trash.
    
    Trash week alternates every other Thursday, calculated based on
    the "epoch week" starting from January 1, 1970.

    Returns:
        str: "Tyler" if the epoch week is even, otherwise "Huy".
    """
    today = datetime.today()
    days_since_thursday = (today.weekday() - 3) % 7
    last_thursday = today - timedelta(days=days_since_thursday)

    epoch_start = datetime(1970, 1, 1)
    days_since_epoch = (last_thursday - epoch_start).days
    epoch_week = days_since_epoch // 7

    return "Tyler" if epoch_week % 2 == 0 else "Huy"

def get_random_quote() -> str:
    """
    Fetch a random quote from the ZenQuotes API.
    
    If the API request fails, return an error message.

    Returns:
        str: A formatted quote string wrapped to 30 characters per line.
    """
    try:
        response = requests.get(QUOTE_API_URL, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        quote_data = response.json()[0]
        quote = quote_data["q"]
        author = quote_data["a"]
        wrapped_quote = "\n".join(textwrap.wrap(quote, width=30))
        return f'"{wrapped_quote}"\n- {author}'
    except (requests.RequestException, KeyError, IndexError) as e:
        print(f"Error fetching quote: {e}")
        return "Error fetching quote."

def setup_display(color: str = "red") -> InkyWHAT:
    """
    Set up the InkyWHAT display with the specified color.
    
    Args:
        color (str): The display color mode ("red", "black", or "yellow").
    
    Returns:
        InkyWHAT: The initialized InkyWHAT display object.
    """
    print("Checking for InkyWHAT...")
    inky_display = InkyWHAT(color)
    inky_display.v_flip = True
    inky_display.h_flip = True
    print("Found!")
    inky_display.set_border(inky_display.WHITE)
    return inky_display

def main() -> None:
    """
    Main function to display trash duty and a random quote on the InkyWHAT.
    """
    inky_display = setup_display()
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_baseline = ImageFont.truetype(SourceSansProSemibold, 24)
    font_header = ImageFont.truetype(SourceSansProSemibold, 55)
    font_quote = ImageFont.truetype(SourceSansProSemibold, 25)

    # Fetch data
    trash_owner = get_trash_week_owner()
    quote = get_random_quote()

    # Draw content on the canvas
    try:
        print("Drawing...")
        img.paste(IMG_TRASH, (15, 5))
        draw.text((92, 6), f"{trash_owner}'s Week", inky_display.BLACK, font=font_header)
        draw.text((30, 260), f"Updated at {LAST_UPDATED}", inky_display.BLACK, font=font_baseline)
        draw.multiline_text((30, 100), quote, inky_display.BLACK, font=font_quote, spacing=5)
    except Exception as e:
        print(f"Error during drawing: {e}")
        draw.text((20, 25), f"Error:\n{e}", inky_display.RED, font=font_baseline)

    # Display the image on the InkyWHAT
    inky_display.set_image(img)
    inky_display.show()

if __name__ == "__main__":
    main()
