#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
import sys
import smtplib
from cgi import FieldStorage
from email.mime.text import MIMEText
from email.Utils import formatdate
import cherrypy
from cherrypy import _cperror

TEMPLATE = u"""
<h2>Request info</h2>
<table>
    <tr>
        <td><strong>Base:</strong></td>
        <td>%(base)s</td>
    </tr>
    <tr>
        <td><strong>Path info:</strong></td>
        <td><strong>%(path_info)s</strong></td>
    </tr>
    <tr>
        <td><strong>Query string:</strong></td>
        <td>%(query_string)s</td>
    </tr>
</table>

<h2>Request headers</h2>
<table>
    %(headers)s
</table>

<h2>Request parameters</h2>
<table>
    %(params)s
</table>

<h2>Traceback</h2>
<pre>
    %(traceback)s
</pre>
"""

HEADER_TEMPLATE = PARAM_TEMPLATE = u"""
        <tr>
            <td><strong>%s</strong></td>
            <td>%s</td>
        </tr>
"""

def error_email(
    smtp_host = "localhost",
    smtp_port = smtplib.SMTP_PORT,
    mime_type = "html",
    subject = None,
    sender = None,
    receivers = (),
    template = TEMPLATE,
    header_template = HEADER_TEMPLATE,
    param_template = PARAM_TEMPLATE,
    encoding = "utf-8"):
    
    def _serialize_value(value):
        if isinstance(value, FieldStorage):
            return "FieldStorage"
        elif isinstance(value, basestring):
            return _encode(value)
        else:
            return _encode(repr(value))

    def _encode(value):
        if isinstance(value, unicode):
            return value

        return unicode(value, encoding, errors='replace')

    host_name = cherrypy.request.headers.get(
        "X-FORWARDED-HOST",
        cherrypy.request.local.name
    )

    if subject is None:
        exc_type = sys.exc_info()[0]
        subject = "%s %s" % (
            host_name,
            exc_type.__name__
                if isinstance(exc_type, type)
                else exc_type
        )
    elif callable(subject):
        subject = subject()

    if isinstance(receivers, basestring):
        receivers = receivers.split(",")
    receivers = set([receiver.strip() for receiver in receivers])

    tpl_params = {}
    tpl_params["base"] = _encode(cherrypy.request.base)
    tpl_params["path_info"] = _encode(cherrypy.request.path_info)
    tpl_params["query_string"] = _encode(cherrypy.request.query_string)
    tpl_params["headers"] = u"".join(
        header_template % (_encode(k), _serialize_value(v))
        for k, v in cherrypy.request.header_list
    )
    tpl_params["params"] = u"".join(
        param_template % (_encode(k), _serialize_value(v))
        for k, v in cherrypy.request.params.iteritems()
    )
    tpl_params["traceback"] = _cperror.format_exc()

    html = template % tpl_params

    message = MIMEText(html.encode(encoding), _subtype = mime_type, _charset = encoding)
    message["Subject"] = subject
    message["From"] = sender or "errors@" + host_name
    message["To"] = ",".join(receivers)
    message["Date"] = formatdate()

    smtp = smtplib.SMTP(smtp_host, smtp_port)
    smtp.sendmail(sender, list(receivers), message.as_string())
    smtp.quit()


cherrypy.tools.error_email = cherrypy.Tool(
    'before_error_response',
    error_email
)

