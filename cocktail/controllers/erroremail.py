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
    param_template = PARAM_TEMPLATE):
    
    host_name = cherrypy.request.headers.get(
        "X-FORWARDED-HOST",
        cherrypy.request.local.name
    )

    if subject is None:
        subject = "%s %s" % (
            host_name,
            sys.exc_type.__name__
                if isinstance(sys.exc_type, type)
                else sys.exc_type
        )
    elif callable(subject):
        subject = subject()

    if not isinstance(receivers, basestring):
        receivers = ",".join(receivers)

    html = template % {
        "base": cherrypy.request.base,
        "path_info": cherrypy.request.path_info,
        "query_string": cherrypy.request.query_string,
        "headers": u"".join(header_template % (k, v)
                            for k, v in cherrypy.request.header_list),
        "params": u"".join(
            param_template % (
                k,
                # Don't include the whole datastream of FieldStorage instances
                # on error emails
                v if not isinstance(v, FieldStorage) else "FieldStorage"
            )
            for k, v in cherrypy.request.params.iteritems()
        ),
        "traceback": _cperror.format_exc()
    }
 
    message = MIMEText(html, mime_type)
    message["Subject"] = subject
    message["From"] = sender or "errors@" + host_name
    message["To"] = receivers
    message["Date"] = formatdate()

    smtp = smtplib.SMTP(smtp_host, smtp_port)
    smtp.sendmail(sender, receivers, message.as_string())
    smtp.quit()

cherrypy.tools.error_email = cherrypy.Tool(
    'before_error_response',
    error_email
)

