#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import (
    translations,
    language_context,
    get_language
)
from cocktail.urls import URL, URLBuilder
from .request import get_request_url
from .dispatcher import StopRequest

translations.load_bundle("cocktail.controllers.redirection")

def redirect(destination, status = None):
    """Redirect the current request to the given URL."""

    if isinstance(destination, URLBuilder):
        destination = str(destination.get_url())
    elif not isinstance(destination, str):
        destination = str(destination)

    raise cherrypy.HTTPRedirect(destination, status = status)

def reload_request_url():
    """Redirect to the current URL using a GET request."""
    raise cherrypy.HTTPRedirect(get_request_url())

def post_redirection(destination, data):
    """Redirect the client to the given URL using a POST request."""

    with language_context(get_language() or "en"):
        trans_prefix = "cocktail.controllers.redirection.post_redirection."
        title = translations(trans_prefix + "title")
        submit_label = translations(trans_prefix + "submit_button")
        explanation = translations(trans_prefix + "explanation")

    form_content = "\n".join(
        """<input type="hidden" name="%s" value="%s">"""
        % (key, value)
        for key, value in data.items()
    )

    cherrypy.response.status = 200
    cherrypy.response.body = (
        """
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                <title>%(title)s</title>
                <script type="text/javascript">
                    <!--
                    onload = function () {
                        document.getElementById("redirectionForm").submit();
                    }
                    //-->
                </script>
            </head>
            <body>
                <form id="redirectionForm" method="POST" action="%(action)s">
                    %(form_content)s
                    <noscript>
                        <p>%(explanation)s</p>
                        <input type="submit" value="%(submit_label)s">
                    </noscript>
                </form>
            </body>
        </html>
        """ % {
            "title": title,
            "action": destination,
            "form_content": form_content,
            "explanation": explanation,
            "submit_label": submit_label
        }
    )
    raise StopRequest()

