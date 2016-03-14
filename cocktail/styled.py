#-*- coding: utf-8 -*-
u"""Provides functions for styling output in CLI applications.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
from warnings import warn
from time import time

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

supported_platform = (sys.platform in supported_platforms)

if supported_platform:

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


class ProgressBar(object):

    width = 30
    min_time_between_updates = 0.005

    completed_char = "*"
    completed_style = {"foreground": "bright_green"}

    pending_char = "*"
    pending_style = {"foreground": "dark_gray"}

    def __init__(self, total_cycles, label = None, visible = True):
        self.__first_iteration = True
        self.__last_update = None
        self.progress = 0
        self.total_cycles = total_cycles
        self.label = label
        self.visible = visible

    def __enter__(self):
        self.update()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            self.finish()

    def message(self, label):
        self.label = label
        self.update(force = True)

    def update(self, cycles = 0, force = False):

        if not self.visible:
            return

        self.progress += cycles

        # Prevent flickering caused by too frequent updates
        if not force and self.min_time_between_updates is not None:
            now = time()
            if (
                self.__last_update is not None
                and now - self.__last_update < self.min_time_between_updates
            ):
                return False
            self.__last_update = now

        if supported_platform:
            line = self.get_bar_string() + self.get_progress_string()
        else:
            line = self.get_progress_string()

        label = self.label

        if self.__first_iteration:
            self.__first_iteration = False
        else:
            if supported_platform:
                line = "\033[1A\033[K" + line
                if label:
                    label = "\033[2A\033[K" + label + "\n"

        if label:
            print label

        print line
        sys.stdout.flush()
        return True

    def finish(self):
        self.progress = self.total_cycles
        self.update(force = True)

    def get_bar_string(self):
        if not self.total_cycles:
            completed_width = 0
        else:
            completed_width = int(
                self.width * (float(self.progress) / self.total_cycles)
            )
        return (
            styled(
                self.completed_char * completed_width,
                **self.completed_style
            )
            + styled(
                self.pending_char * (self.width - completed_width),
                **self.pending_style
            )
        )

    def get_progress_string(self):
        return " (%d / %d)" % (self.progress, self.total_cycles)


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

