#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.translations import translations
from cocktail.html.element import Element

def get_tag_cloud_font_sizes(tags, max_font_increment = 75):

    # Find minimum and maximum frequency
    min_frequency = None
    max_frequency = 0

    for frequency in tags.itervalues():

        if min_frequency is None or frequency < min_frequency:
            min_frequency = frequency
        
        if frequency > max_frequency:
            max_frequency = frequency

    # Assign font sizes
    divergence = max_frequency - min_frequency

    if not divergence:
        font_sizes = dict((tag, 100) for tag in tags)
    else:
        font_sizes = {}
        for tag, frequency in tags.iteritems():
            ratio = float(frequency - min_frequency) / divergence
            font_sizes[tag] = 100 + int(ratio * max_font_increment)

    return font_sizes


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
        
        self._font_sizes = get_tag_cloud_font_sizes(
            self.tags,
            self.max_font_increment
        )

        for tag in self.sorted_tags(self.tags):
            self.append(self.create_tag_entry(tag, self.tags[tag]))
	    self.append(" ")

    def sorted_tags(self, tags):
        return sorted(tags.keys(), key = translations)

    def create_tag_entry(self, tag, frequency):        
        entry = Element("a")        
        entry.label = self.create_tag_label(tag, frequency) 
        entry.append(entry.label)
        entry.set_style("font-size", str(self._font_sizes[tag]) + "%")                
        return entry

    def create_tag_label(self, tag, frequency):
        return translations(tag)

