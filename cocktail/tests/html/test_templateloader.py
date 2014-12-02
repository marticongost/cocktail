#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
"""
import sys
from os import mkdir
from os.path import join, exists
from tempfile import mkdtemp
from shutil import rmtree
from unittest import TestCase
from time import sleep


class TemplateLoaderTestCase(TestCase):

    def setUp(self):
        from cocktail.html.templates.loader import TemplateLoader
        self.loader = TemplateLoader()
        self.temp_folder = mkdtemp()
        self.template_repository = join(self.temp_folder, "testtemplates")
        mkdir(self.template_repository)
        self.write_module("__init__.py", "")
        sys.path.append(self.temp_folder)
        sys.modules.pop("testtemplates", None)

    def tearDown(self):
        sys.path.remove(self.temp_folder)
        rmtree(self.temp_folder)

    def write_module(self, filename, code):
        
        path = join(self.template_repository, filename)

        if exists(path):            
            sleep(1)

        f = open(path, "w")
        f.write(code)
        f.close()

        return path

    def _cml(self, root_tag):
        return """<?xml version="1.0" encoding="utf-8"?>
<%s
    xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://www.whads.com/ns/cocktail/templates"/>""" % root_tag

    def test_caches_cml_templates(self):
        
        self.write_module("Foo.cml", self._cml("div"))        
        cls = self.loader.get_class("testtemplates.Foo")

        for i in range(3):
            assert self.loader.get_class("testtemplates.Foo") is cls

    def test_caches_python_templates(self):
                
        self.write_module("foo.py", """
from cocktail.html import Element

class Foo(Element):
    pass
""")
        cls = self.loader.get_class("testtemplates.Foo")

        for i in range(3):
            assert self.loader.get_class("testtemplates.Foo") is cls

    def test_reload_modified_cml(self):

        self.write_module("Foo.cml", self._cml("div"))
        a = self.loader.get_class("testtemplates.Foo")

        self.write_module("Foo.cml", self._cml("span"))
        b = self.loader.get_class("testtemplates.Foo")

        assert a is not b

    def test_reload_modified_cml_base(self):

        self.write_module("ViewA.cml", self._cml("div"))
        self.write_module("ViewB.cml", self._cml("py:testtemplates.ViewA"))
        self.write_module("ViewC.cml", self._cml("py:testtemplates.ViewB"))
        view1 = self.loader.get_class("testtemplates.ViewC")

        self.write_module("ViewA.cml", self._cml("span"))
        view2 = self.loader.get_class("testtemplates.ViewC")

        self.write_module("ViewA.cml", self._cml("table"))
        view3 = self.loader.get_class("testtemplates.ViewC")

        assert view1 is not view2
        assert view1 is not view3
        assert view1().tag == "div"
        assert view2().tag == "span"
        assert view3().tag == "table"

    def test_can_disable_timestamp_checks(self):

        self.write_module("Foo.cml", self._cml("div"))
        a = self.loader.get_class("testtemplates.Foo")

        self.loader.cache.checks_modification_time = False

        self.write_module("Foo.cml", self._cml("span"))
        b = self.loader.get_class("testtemplates.Foo")
        
        assert a is b

