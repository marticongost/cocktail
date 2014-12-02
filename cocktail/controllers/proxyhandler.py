#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import urllib
import urllib2
import cherrypy

def proxy_handler(url):
    """Makes a call to another HTTP resource and proxies the response to the
    client.

    The function accesses request and response data for the current cherrypy
    context.

    @param url: The location of the proxied HTTP resource.
    @type url: str
    """
    # TODO: Propagate response status
    # TODO: Propagate headers (both ways)
    # TODO: Propagate request POST data
    # TODO: Verify cookies are propagated
    # TODO: 30X redirections
    # TODO: find the encoding from the remote resource (meta tag - for (X)HTML
    # resources - or header)
    encoding = "utf-8"
    
    # Taking request parameters
    params = cherrypy.request.params

    for key in params:

        if isinstance(params[key], list):
            params_tmp = []
            for element in params[key]:
                params_tmp.append(element.encode(encoding))
            params[key] = params_tmp
        else:
            params[key] = params[key].encode(encoding)

    try:

        data = urllib.urlencode(params,True)

        # Sending the request
        rfile = urllib2.urlopen(url, data)

    except urllib2.HTTPError, error:
        raise cherrypy.HTTPError(error.code, error.msg)

    response_body = rfile.read()
    response_body = unicode(response_body, encoding)
    cherrypy.response.body = response_body
