#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.element import Element


class YouTubePlayer(Element):

    tag = "iframe"
    video_id = None
    width = 480
    height = 385
    allow_fullscreen = True
    autoplay = False
    show_info = False
    show_related_videos = False
    https = True

    def _build(self):
        self["frameborder"] = "0"

    def _ready(self):
        self["src"] = self.get_video_url()
        self["width"] = self.width
        self["height"] = self.height
        self["allowfullscreen"] = self.allow_fullscreen
        Element._ready(self)

    def get_video_url(self):

        url = "%s://www.youtube.com/embed/%s" % (
            "https" if self.https else "http",
            self.video_id
        )

        params = []

        if not self.show_info:
            params.append("showinfo=0")

        if not self.show_related_videos:
            params.append("rel=0")
            
        if self.allow_fullscreen:
            params.append("fs=1")

        if self.autoplay:
            params.append("autoplay=1")

        if params:
            url += "?" + "&".join(params)

        return url

