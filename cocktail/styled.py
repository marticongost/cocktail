#-*- coding: utf-8 -*-
u"""Provides functions for styling output in CLI applications.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
from warnings import warn

supported_platforms = ["linux2"]

foreground_codes = {
    "default": 39,
    "white": 37,
    "black": 30,
    "red": 31,
    "green": 32,
    "brown": 33,
    "blue": 34,
    "violet": 35,
    "turquoise": 36,
    "light_gray": 37,
    "dark_gray": 90,
    "magenta": 91,
    "bright_green": 92,
    "yellow": 93,
    "slate_blue": 94,
    "pink": 95,
    "cyan": 96,
}

background_codes = {
    "default": 49,
    "black": 48,
    "red": 41,
    "green": 42,
    "brown": 43,
    "blue": 44,
    "violet": 45,
    "turquoise": 46,
    "light_gray": 47,
    "dark_gray": 100,
    "magenta": 101,
    "bright_green": 102,
    "yellow": 103,
    "slate_blue": 104,
    "pink": 105,
    "cyan": 106,
    "white": 107
}

style_codes = {
    "normal": 0,
    "bold": 1,
    "underline": 4,
    "inverted": 7,
    "hidden": 8,
    "strike_through": 9
}

if sys.platform in supported_platforms:
    
    def styled(
        string,
        foreground = "default",
        background = "default",
        style = "normal"):
        
        foreground_code = foreground_codes.get(foreground)
        background_code = background_codes.get(background)
        style_code = style_codes.get(style)
        
        if foreground_code is None \
        or background_codes is None \
        or style_code is None:
            warn(
                "Can't print using the requested style: %s %s %s"
                % (foreground, background, style)
            )
            return string
        else:
            return "\033[%d;%d;%dm%s\033[m" % (
                style_code,
                foreground_code,
                background_code,
                string
            )

else:
    def styled(string, foreground = None, background = None, style = None):
        if not isinstance(string, str):
            string = str(string)
        return string


if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--foreground", "-f",
        help = "A subset of foreground colors to display")
    parser.add_option("--background", "-b",
        help = "A subset of background colors to display")
    parser.add_option("--style", "-s",
        help = "A subset of text styles to display")
    options, args = parser.parse_args()

    fg_list = (options.foreground.split(",")
        if options.foreground
        else foreground_codes)

    bg_list = (options.background.split(",")
        if options.background
        else background_codes)

    st_list = (options.style.split(",")
        if options.style
        else style_codes)

    for fg in fg_list:
        for bg in bg_list:
            for st in st_list:
                print fg.ljust(15), bg.ljust(15), st.ljust(15),
                print styled("Example text", fg, bg, st)

