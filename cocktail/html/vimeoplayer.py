#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.element import Element


class VimeoPlayer(Element):

    tag = "iframe"
    https = True
    width = 480
    height = 385
    allow_fullscreen = True
    video_id = None
    vimeo_autoplay = False
    vimeo_loop = False
    vimeo_api = False
    vimeo_player_id = None
    vimeo_title = True
    vimeo_byline = True
    vimeo_portrait = True
    vimeo_color = None

    def _build(self):
        self["frameborder"] = "0"

    def _ready(self):
        self["src"] = self.get_video_url()
        self["width"] = self.width
        self["height"] = self.height
        self["allowfullscreen"] = self.allow_fullscreen
        self["mozallowfullscreen"] = self.allow_fullscreen
        self["webkitallowfullscreen"] = self.allow_fullscreen
        Element._ready(self)

    def get_video_url(self):

        url = "%s://player.vimeo.com/video/%s" % (
            "https" if self.https else "http",
            self.video_id
        )

        params = [
            "autoplay=%d" % self.vimeo_autoplay,
            "loop=%d" % self.vimeo_loop,
            "api=%d" % self.vimeo_api,
            "title=%d" % self.vimeo_title,
            "byline=%d" % self.vimeo_byline,
            "portrait=%d" % self.vimeo_portrait
        ]

        if self.vimeo_player_id:
            params.append("player_id=" + self.vimeo_player_id)

        if self.vimeo_color:
            params.append("color=" + self.vimeo_color.lstrip("#"))

        url += "?" + "&".join(params)
        return url

