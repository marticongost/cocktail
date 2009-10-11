#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.translations import translations
from cocktail.html.element import Element


class TagCloud(Element):
    """An element that renders a link cloud for a set of tags.
    
    @var tags: A mapping of tags and their frequency.
    @type tags: dict

    @var max_font_increment: The maximum percentage increment to the font size
        of the most frequent tag.
    @type max_font_increment: int
    """
    tags = {}
    max_font_increment = 75

    def _ready(self):
        Element._ready(self)
        
        # Find minimum and maximum frequency
        min_frequency = None
        max_frequency = 0

        for tag, frequency in self.tags.iteritems():

            if min_frequency is None or frequency < min_frequency:
                min_frequency = frequency
            
            if frequency > max_frequency:
                max_frequency = frequency

        self._min_frequency = min_frequency
        self._max_frequency = max_frequency
        self._divergence = self._max_frequency - self._min_frequency
        
        # Render tags
        for tag, frequency in self.tags.iteritems():
            self.append(self.create_tag_link(tag, frequency))

    def create_tag_link(self, tag, frequency):
        
        entry = Element("a")
        entry.append(self.create_tag_label(tag, frequency))
        
        # Font size variation
        if self._divergence:
            ratio = float(frequency - self._min_frequency) / self._divergence
            size_increment = int(ratio * self.max_font_increment)
            entry.set_style("font-size", str(100 + size_increment) + "%")

        return entry

    def create_tag_label(self, tag, frequency):
        return "%s (%d)" % (translations(tag), frequency)

