#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.html import Element


class MediaElementVideo(Element):

    tag = "video"
    width = None
    height = None
    autoplay = False
    show_player_controls = True
    media_element_defaults = {}
    sources = ()

    def _build(self):
        self["preload"] = "auto"
        self.media_element_options = self.media_element_defaults.copy()
        self.add_resource("/cocktail/mediaelement/mediaelementplayer.min.css")
        self.add_resource("/cocktail/mediaelement/mediaelement-and-player.min.js")
        self.add_resource("/cocktail/scripts/MediaElementVideo.js")

    def _ready(self):

        if self.width:
            self["width"] = self.width

        if self.height:
            self["height"] = self.height

        if self.autoplay:
            self["autoplay"] = "autoplay"

        if self.show_player_controls:
            self["controls"] = "controls"

        self.set_client_param(
            "mediaElementOptions",
            self.media_element_options
        )

        for url, mime_type in self.sources:
            source = Element("source")
            source["src"] = url
            source["type"] = mime_type
            self.append(source)

        Element._ready(self)

