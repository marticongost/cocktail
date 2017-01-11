#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from types import GeneratorType
import cherrypy
from json import dumps
from string import letters, digits
from cocktail.events import Event
from cocktail.stringutils import random_string, normalize_indentation as ni
from cocktail.html import resource_repositories
from .sessions import session

_protection = None

def get_csrf_protection(instance):
    """Gets the active CSRF protection scheme, as set by `set_csrf_protection`.

    :return instance: The installed CSRF protection scheme, or None if CSRF
        protection is not enabled.
    :rtype instance: `CSRFProtection`
    """
    return _protection

def set_csrf_protection(instance):
    """Installs the given CSRF protection scheme.

    :param instance: The CSRF protection scheme to install, or None to disable
        CSRF protection.
    :type instance: `CSRFProtection`
    """
    global _protection
    _protection = instance

# Prevent POST requests that don't include the correct token
def _csrf_token_validation():
    if _protection and _protection.should_require_token():
        session_token = _protection.get_session_token()
        received_token = _protection.get_request_token()
        if received_token != session_token:
            _protection.handle_token_error(session_token, received_token)

cherrypy.request.hooks.attach("before_handler", _csrf_token_validation)

# Send the token to the client using a cookie (the most direct
# approach would be to embed the token into served pages, but that
# would make the content uncachable). Inject javascript that reads that cookie
# and injects it as a field (on HTML forms) or as an HTTP header (on Ajax
# requests).
def _csrf_token_injection():

    if not _protection or not _protection.should_inject():
        return

    # Generate the code and send it to the client in a cookie
    cookie = cherrypy.request.cookie.get(_protection.cookie_name)
    cookie_token = cookie and cookie.value
    session_token = _protection.get_session_token()

    if cookie_token != session_token:
        cherrypy.response.cookie[_protection.cookie_name] = session_token
        cherrypy.response.cookie[_protection.cookie_name]["path"] = "/"

    # Insert the script that will inject the token into POST requests
    content_type = cherrypy.response.headers.get("Content-Type")
    if not content_type or content_type.split(";", 1)[0] == "text/html":
        code = (
            ni("""
            <script type="text/javascript">
            cocktail.declare("cocktail.csrfprotection");
            cocktail.setVariable("cocktail.csrfprotection.cookieName", %s);
            cocktail.setVariable("cocktail.csrfprotection.field", %s);
            cocktail.setVariable("cocktail.csrfprotection.header", %s);
            </script>
            <script type="text/javascript" src="%s"></script>
            """)
            % (
                dumps(_protection.cookie_name),
                dumps(_protection.field),
                dumps(_protection.header),
                resource_repositories.normalize_uri(
                    "cocktail://scripts/csrfprotection.js"
                )
            )
        )
        html = u"".join(
            (
                chunk.decode("utf-8")
                if isinstance(chunk, str)
                else chunk
            )
            for chunk in cherrypy.response.body
        )
        pos = html.find("</head>")
        if pos == -1:
            pos = html.find("</body>")
        if pos != -1:
            html = html[:pos] + code + html[pos:]
        cherrypy.response.body = [html]

cherrypy.request.hooks.attach("before_finalize", _csrf_token_injection)


class CSRFProtection(object):
    """A class that provides protection against CSRF attacks.

    For background on Cross Site Request Forgery attacks, see the
    `corresponding entry on the OWASP website
    <https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)>`.

    The class implements a Synchronizer Token pattern to disallow POST requests
    that don't include a previously supplied token. Tokens are generated on a
    per session basis, and can also be explicitly renewed by calling the
    `renew_session_token` method.

    Tokens are sent to the client using a cookie and injected into form
    submissions and Ajax requests via Javascript. This approach prevents
    interference with response caching, at the cost of preventing POST requests
    from user agents without javascript enabled.

    Only a single instance of this class can be enabled at any one time. To
    install the protection scheme, create an instance of the class and pass it
    to `set_csrf_protection`. Note that the module automatically installs an
    instance of the class by default, so unless the default behavior needs to
    be changed, users don't need to do anything to enable the protection.
    """
    session_key = "cocktail.csrf_protection_token"
    cookie_name = session_key
    token_characters = letters + digits
    token_length = 40
    field = "__cocktail_csrf_token"
    header = "X-Cocktail-CSRF-Token"

    deciding_injection = Event()

    def should_inject(self):
        """Specifies wether the protection scheme should be applied to the
        current request.

        All requests are protected by default.

        :return: True if the scheme should be enabled, False otherwise.
        :rtype: True
        """
        try:
            self.deciding_injection()
        except CSRFProtectionExemption:
            return False
        else:
            return True

    def should_require_token(self):
        """Specifies wether the current request should be protected.

        By default, all POST requests are protected.

        :return: True if the request should be protected, False otherwise.
        :rtype: True
        """
        return cherrypy.request.method == "POST"

    def generate_token(self):
        """Generate a Synchronizer Token.

        The default implementation generates a random string containing as many
        characters from `token_characters` as indicated by `token_length`.

        :return: The generated token.
        :rtype: str
        """
        return random_string(self.token_length, self.token_characters)

    def renew_session_token(self):
        """Generate a new token for the active session."""
        session.pop(self.session_key, None)
        return self.get_session_token()

    def get_session_token(self):
        """Get (and set, if new) the token for the active session.

        :return: The token assigned to the active session.
        :rtype: str
        """
        token = session.get(self.session_key)

        if not token:
            token = self.generate_token()
            session[self.session_key] = token

        return token

    def get_request_token(self):
        """Get the token included in the present request.

        The method will check for either an HTTP header (as specified by the
        `header` property) and a POST data field (as specified by the `field`
        property).

        :return: The token included in the request, or None if the request
            contains no Synchronizer token.
        :rtype: str
        """
        return (
            cherrypy.request.headers.get(self.header)
            or cherrypy.request.params.get(self.field)
        )

    def handle_token_error(self, session_token, received_token):
        """Specifies what should happen when a non authenticated request is
        received.

        Note that a request without a valid token doesn't necessarily equate
        with an attack:
            - Any user agent without javascript enabled will produce this.
            - If the session is lost, existing clients may send tokens that are
              no longer valid.

        The default behavior will raise a `CSRFTokenError` exception (which
        will typically end up producing a 403 HTTP error).

        :param session_token: The token that should have been included in the
            request for it to be considered valid.
        :type session_token: str

        :param received_token: The invalid token that was received instead, or
            None if no token was included.
        :type received_token: str
        """
        raise CSRFTokenError()


class CSRFProtectionExemption(Exception):
    """An exception raised by the `CSRFProtection.deciding_injection` to
    prevent the protection scheme from being injected into the current request.
    """


class CSRFTokenError(cherrypy.HTTPError):
    """An exception raised if someone attempts a POST request without the
    proper CSRF prevention token.
    """

    def __init__(self):
        cherrypy.HTTPError.__init__(
            self,
            403,
            "Invalid request authorization token"
        )


# Enabled by default, using standard parameters. Set to None to disable, or to
# another instance to change the default behavior.
set_csrf_protection(CSRFProtection())

