#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
import sys
from warnings import warn

supported_platforms = ["linux2"]

color_map = {
    ("white", "black", None): 0,
    ("white", "black", "bold"): 1,
    ("white", "black", "underline"): 4,
    ("white", "black", "strike_through"): 9,
    ("black", "white", None): 7,
    ("black", "black", None): 30,
    ("red", "black", None): 31,
    ("green", "black", None): 32,
    ("brown", "black", None): 33,
    ("blue", "black", None): 34,
    ("violet", "black", None): 35,
    ("turquoise", "black", None): 36,
    ("light_gray", "black", None): 37,
    ("white", "red", None): 41,
    ("white", "green", None): 42,
    ("white", "brown", None): 43,
    ("white", "blue", None): 44,
    ("white", "violet", None): 45,
    ("white", "turquoise", None): 46,
    ("white", "light_gray", None): 47,
    ("dark_gray", "black", None): 90,
    ("magenta", "black", None): 91,
    ("bright_green", "black", None): 92,
    ("yellow", "black", None): 93,
    ("slate_blue", "black", None): 94,
    ("pink", "black", None): 95,
    ("cyan", "black", None): 96,
    ("white", "dark_gray", None): 100,
    ("white", "magenta", None): 101,
    ("white", "bright_green", None): 102,
    ("white", "yellow", None): 103,
    ("white", "slate_blue", None): 104,
    ("white", "pink", None): 105,
    ("white", "cyan", None): 106,
    ("white", "white", None): 107
}

if sys.platform in supported_platforms:
    
    def styled(
        string,
        foreground = "white",
        background = "black",
        style = None):
        
        key = (foreground, background, style)
        code = color_map.get(key)

        if code is None:
            warn("Can't print using the requested style: %s" % key)
            return string
        else:
            return "\033[0;%dm%s\033[m" % (code, string)

else:
    def styled(string, foreground = None, background = None, style = None):
        if not isinstance(string, basestring):
            string = str(string)
        return string

