#!/usr/bin/env python
"""Adds quote box to image
"""

# AUR-packages: python-pillow python requests python-google-api-python-client python-oauth2client

# standard imports
import os
import random
import textwrap

# 3rd party imports
import click
# python-pillow
from PIL import Image, ImageDraw, ImageFont, ImageStat

# local imports
import download_wallpaper_image
import get_calendar_events

# BING_LOCALES = ["cz-CZ", "da-DK", "de-AT", "de-CH", "de-DE", "en-AU", "en-CA", "en-GB", "en-NZ", "en-US", "en-ZA", "es-ES", "es-MX", "et-EE", "fi-FI", "fr-BE", "fr-CA", "fr-CH", "fr-FR", "hr-HR", "hu-HU", "is-IS", "it-CH", "it-IT", "jp-JP", "ko-KR", "lv-LV", "lt-LT", "no-NO", "nl-BE", "nl-NL", "pl-PL", "pt-BR", "pt-PT", "ru-RU", "sk-SK", "sl-SI", "sr-latn-RS", "sv-SE", "tr-TR", "zh-HK", "zh-TW"]
BING_LOCALES = ["en-AU", "jp-JP"]
BING_RESOLUTIONS = ["1366x768", "800x600", "1920x1080", "1024x768"]


@click.command()
@click.option(
    "--country",
    type=click.Choice(BING_LOCALES, case_sensitive=True),
    default="en-AU",
    show_default=True,
    help="Localization",
)
@click.option(
    "--resolution",
    type=click.Choice(BING_RESOLUTIONS, case_sensitive=True),
    default="1920x1080",
    show_default=True,
)
@click.option(
    "--quote-file",
    type=click.Path(exists=True, readable=True, resolve_path=True),
    default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "quotes.txt"),
    help="Can be any newline seperated plaintext file",
    show_default=True,
)
def manipulate_wallpaper(country, resolution, quote_file):
    """ This script will choose a random line from the quote-file, append the user's calendar for the next two days, and the overlay it on that day's Bing wallpaper
    """

    # get image
    download_wallpaper_image.download_bing_wallpaper(country, resolution)

    # get agenda
    agenda = get_calendar_events.main()

    # get base image
    base_image = Image.open("/tmp/bing.jpg").convert("RGBA")

    # set font
    font = "/usr/share/fonts/gnu-fee/FreeMono.otf"
    font_size = 25
    quote_font = ImageFont.truetype(font, font_size)

    # make a blank image for the text, initialized to transparent text color
    text_image = Image.new("RGBA", base_image.size, (255, 255, 255, 0))

    # create a list where each entry is a line of text
    with open(quote_file) as f:
        quote_pool = f.read().splitlines()
    random_quote = random.choice(quote_pool)
    quote_lines = textwrap.wrap(random_quote, width=55)
    quote_lines.append("")
    quote_lines = quote_lines + agenda.splitlines()
    # Need to replace blank with single space so that it gets added to the image as a new line
    quote_lines = [" " if x=="" else x for x in quote_lines]

    # get a drawing context
    draw = ImageDraw.Draw(text_image)

    # determine location of text
    x_loc = base_image.size[0]

    # determine the size of one line of the quote, and multiply by how many lines giving the y-size
    quote_size_y = len(quote_lines) * quote_font.getsize(quote_lines[0])[1]

    # determine x size by seeing how wide the text will be
    quote_size_x = quote_font.getsize(quote_lines[0])[0]

    # put the quote so the centre always matches the centre of the image
    y_loc = base_image.size[1] / 2 - (quote_size_y / 2)

    # get average background image brightness by converting to greyscale and getting RMS
    mean_brightness = int(ImageStat.Stat(base_image.convert("L")).mean[0])
    square_brightness = int(100 + mean_brightness)

    # draw text
    for line in quote_lines:
        line_width, line_height = quote_font.getsize(line)
        draw.text(
            ((x_loc - line_width - 20), y_loc),
            line,
            font=quote_font,
            fill=((255, 255, 255, square_brightness)),
        )
        y_loc += line_height
    textbox_image = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(textbox_image)
    x_loc = base_image.size[0]
    y_loc = base_image.size[1] / 2 - (quote_size_y / 2)
    draw.rectangle(
        (
            (x_loc - quote_size_x * 1.25),
            y_loc - 10,
            x_loc - 10,
            y_loc + quote_size_y + 10,
        ),
        (0, 0, 0, square_brightness),
    )

    image_out = Image.alpha_composite(base_image, textbox_image)
    image_out = Image.alpha_composite(image_out, text_image)

    image_out.save("/tmp/wallpaper.png")

if __name__ == "__main__":
    manipulate_wallpaper()
