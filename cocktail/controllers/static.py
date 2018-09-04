#-*- coding: utf-8 -*-
u"""Serve and preprocess static files.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .filepublication import file_publication

# For backwards compatibility
serve_file = file_publication.serve_file
file_publisher = file_publication.file_publisher
folder_publisher = file_publication.folder_publisher

