#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase


class HTMLCleanerTestCase(TestCase):

    def test_strips_breaklines(self):

        from cocktail.stringutils import clean_html

        assert clean_html("<p>Hello<br>world</p>") == "<p>Hello<br />world</p>"
        assert clean_html("Hello<br>") == "Hello"
        assert clean_html("Hello<br>  ") == "Hello"
        assert clean_html("<br>Hello") == "Hello"
        assert clean_html("  <br>Hello") == "Hello"
        assert clean_html("Hello<br/><br>") == "Hello"
        assert clean_html("<p><br></p>Hello") == "Hello"
        assert clean_html("Hello<p><br></p>") == "Hello"
        assert clean_html("Hello<br>world") == "Hello<br />world"
        assert clean_html("<p>Hello<br>world</p>") == "<p>Hello<br />world</p>"

    def test_strips_empty_tags(self):

        from cocktail.stringutils import clean_html
        
        assert clean_html("<p></p>") == ""
        assert clean_html("<p/>") == ""
        assert clean_html("<div> </div>") == ""
        assert clean_html("<div><div><div></div></div></div>") == ""
        assert clean_html("<div> <p>  </p> </div>") == ""
        assert clean_html("Hello<p> </p> ") == "Hello"
        assert clean_html("<p>Hello</p> <p> </p> ") == "<p>Hello</p>"
        assert clean_html("<p>Hello</p> <p>World</p>") == "<p>Hello</p> <p>World</p>"
        assert clean_html("<div>Hello</div>") == "<div>Hello</div>"
        assert clean_html("Hello<span></span> world") == "Hello world"
        assert clean_html("Hello<span class='foo'></span> world") == "Hello world"
        assert clean_html("Hello <span class='foo'>world</span>") \
            == 'Hello <span class="foo">world</span>'
        assert clean_html("<div> </div><div>foo</div>") == "<div>foo</div>"
        assert clean_html("<div> <p>  \n </p></div>") == ""
        assert clean_html("<div><div><div>Foo</div></div></div>") \
            == "<div><div><div>Foo</div></div></div>"

        for content in (
            '<img src="foo.png" />',
            '<hr />',
            '<object id="foobar"></object>',
            '<iframe src="foo.html"></iframe>',
            '<audio src="foo.mp3"></audio>',
            '<video src="foo.mpg"></video>'
        ):
            assert clean_html(content) == content
            html = ("<div>" * 3) + content + ("</div>" * 3)
            assert clean_html(html) == html

    def test_strips_nbsp_entities(self):

        from cocktail.stringutils import clean_html

        assert clean_html("&nbsp;") == ""
        assert clean_html("Hello&nbsp;") == "Hello"
        assert clean_html("&nbsp;Hello") == "Hello"
        assert clean_html("Hello&nbsp;world") == "Hello&nbsp;world"
        assert clean_html("Hello&nbsp;&nbsp;world") == "Hello&nbsp;&nbsp;world"
        assert clean_html("<div>&nbsp;</div>") == ""
        assert clean_html("<div>  \n &nbsp;  </div>") == ""
        assert clean_html("Hello<p>&nbsp;&nbsp;</p> world") == "Hello world"

