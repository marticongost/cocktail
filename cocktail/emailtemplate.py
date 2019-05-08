"""Classes that streamline the definition of email message templates.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Iterable, Mapping, Set, Union
from smtplib import SMTP, SMTP_PORT
from mimetypes import guess_type
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from email.utils import formatdate, parseaddr, formataddr
from email import encoders

from cocktail.pkgutils import get_full_name
from cocktail.translations import get_language, translations

email_account = str


class EmailTemplate:
    """An email template."""

    type: str = "html"
    encoding: str = "utf-8"
    default_smtp: Union[SMTP, dict, None] = None

    def get_sender(self) -> email_account:
        """Determines the email address to use as the email's sender."""
        return ""

    def get_receivers(self) -> Iterable[email_account]:
        """Determines the email addresses that should be included in the 'To'
        field of the message.
        """
        return []

    def get_bcc(self) -> Iterable[email_account]:
        """Indicates additional email addresses that should also receive the
        message, without appearing on its 'To' field.
        """
        return []

    def get_subject(self) -> str:
        """Establishes the subject for the message."""
        return ""

    def get_body(self) -> str:
        """Establishes the content of the body for the message."""
        return ""

    def get_attachments(self) -> Mapping[str, Union[str, dict]]:
        """Supplies files that should be attached to the message."""
        return {}

    def send(self, smtp: Union[SMTP, dict, None] = None) -> Set[email_account]:
        """Sends the message using the supplied SMTP server."""

        # Body
        message = MIMEText(self.get_body(), self.type, self.encoding)

        # Attachments
        attachments = self.get_attachments()
        if attachments:
            attachments = dict(
                (cid, attachment)
                for cid, attachment in attachments.items()
                if attachment is not None
            )
            if attachments:
                message_text = message
                message = MIMEMultipart("related")
                message.attach(message_text)

                for cid, attachment in attachments.items():

                    if isinstance(attachment, Mapping):
                        file_path = attachment["path"]
                        file_name = attachment["name"]
                        mime_type = attachment["mime_type"]
                    else:
                        file_path = attachment
                        file_name = os.path.basename(file_path)
                        mime_type_guess = guess_type(file_path)
                        if mime_type_guess:
                            mime_type = mime_type_guess[0]
                        else:
                            mime_type = "application/octet-stream"

                    main_type, sub_type = mime_type.split("/", 1)
                    message_attachment = MIMEBase(main_type, sub_type)
                    message_attachment.set_payload(open(file_path).read())
                    encoders.encode_base64(message_attachment)
                    message_attachment.add_header("Content-ID", "<%s>" % cid)
                    message_attachment.add_header(
                        "Content-Disposition",
                        'attachment; filename="%s"' % file_name
                    )
                    message.attach(message_attachment)

         # Receivers
        receivers = set(recv.strip() for recv in self.get_receivers())

        if not receivers:
            return set()

        message["To"] = ", ".join(receivers)

        # Sender
        sender = self.get_sender()
        if sender:
            message["From"] = sender

        # BCC
        bcc = self.get_bcc()
        if bcc:
            receivers.update(recv.strip() for recv in bcc)

        # Subject
        subject = self.get_subject()
        if subject:
            message["Subject"] = Header(subject, self.encoding).encode()

        # Date
        message["Date"] = formatdate()

        # Send the message
        if not smtp:
            smtp = self.default_smtp

        if isinstance(smtp, dict):
            should_close = True
            smtp_conn = SMTP(
                smtp.get("host", "127.0.0.1"),
                smtp.get("port", SMTP_PORT)
            )
            user = smtp.get("user")
            password = smtp.get("password")
            if user and password:
                smtp_conn.login(user, password)
        elif smtp is None:
            should_close = True
            smtp_conn = SMTP("127.0.0.1", SMTP_PORT)
        else:
            should_close = False
            smtp_conn = smtp

        try:
            smtp_conn.sendmail(sender, list(receivers), message.as_string())
        finally:
            if should_close:
                smtp_conn.quit()

        return receivers


class TranslatedEmailTemplate(EmailTemplate):
    """An email template that uses translation bundles to obtain its subject
    and body.
    """

    def __init__(self, language: str = None, **context):
        super().__init__()
        self.language = language
        context["message"] = self
        self.context = context
        self.init_context(context)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.full_name = get_full_name(cls)
        translations.request_bundle(cls.full_name.rsplit(".", 1)[0])

    def init_context(self, context):
        pass

    def get_subject(self) -> str:
        return translations(
            self.full_name + ".subject",
            **self.context,
            language=self.language
        )

    def get_body(self) -> str:
        return translations(
            self.full_name + ".body",
            **self.context,
            language=self.language
        )

