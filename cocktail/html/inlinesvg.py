#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from os import stat
from threading import Lock
from cocktail.resourceloader import ResourceLoader
from .resources import resource_repositories

_xml_doctype_regex = re.compile(r"<!DOCTYPE .*?>")
_xml_pi_regex = re.compile(r"<\?.*?\?>")
_xml_comment_regex = re.compile(r"<!--.*?-->")

def _load_svg(svg_path):
    with open(svg_path) as file:
        svg = file.read().decode("utf-8")
        svg = svg.replace("\r\n", "\n")
        svg = _xml_pi_regex.sub("", svg)
        svg = _xml_doctype_regex.sub("", svg)
        svg = _xml_comment_regex.sub("", svg)
        svg = svg.replace("\n\n", "\n").strip()
        return svg

cache = ResourceLoader(load = _load_svg, lock = Lock())
cache.updatable = False

def get_file_svg(path):
    return cache.request(
        path,
        invalidation = stat(path).st_mtime if cache.updatable else None
    )

def get_uri_svg(uri):
    return get_file_svg(resource_repositories.locate(uri))

