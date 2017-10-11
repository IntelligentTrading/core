from datetime import datetime

from django.core.mail import EmailMessage
from django.db import models
import urllib

from apps.common.behaviors import Timestampable
from apps.common.utilities.email import email_to_string
from apps.common.utilities.multithreading import start_new_thread
from settings import STAGE, DEBUG, DEMO, LOCAL, PRODUCTION, SERVICE_EMAIL_ADDRESS
from apps.common.utilities.unicode_tools import clean_text

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Email(Timestampable, models.Model):
    to_address = models.CharField(max_length=140)
    from_address = models.CharField(
        max_length=140,
        default=SERVICE_EMAIL_ADDRESS
    )
    subject = models.TextField(max_length=140)
    body = models.TextField(default="")
    is_html_body = models.BooleanField(default=False)
    attachments = models.ManyToManyField('common.Document')

    (NOTIFICATION, EMAIL_CONFIRMATION) = list(range(2))
    # text values here are used as default subject line
    TYPE_CHOICES = ((NOTIFICATION, 'notification'),
                    (EMAIL_CONFIRMATION, 'email confirmation'),
                    )
    type = models.SmallIntegerField(
        choices=TYPE_CHOICES, null=True, blank=True, default=NOTIFICATION
    )

    # UPDATE HISTORY
    sent_at = models.DateTimeField(null=True)

    # MODEL PROPERTIES

    # MODEL FUNCTIONS
    def createMessageObject(self):
        self.email = EmailMessage()
        return self.email

    def createSubject(self):
        self.subject = self.subject or ""
        return self.subject

    def createBody(self):
        from django.template import Template, Context
        context = Context({})
        template = Template("Hello Email")
        self.body = clean_text(template.render(context))
        if LOCAL:
            print("printing email body on LOCAL ", self.body)
        return self.body

    def sendToUser(self, user_object):
        self.to_address = user_object.email
        self.send()

    def send(self, require_confirmation=False):
        if not (self.from_address and self.to_address):
            return False

        self.subject = self.subject or self.createSubject()
        self.body = self.body or self.createBody()

        # these actions requires the body to already be constructed
        if STAGE or DEBUG or DEMO:  # non-production emails
            self.body = ("""From: %s
                      To: %s
                      %s
                  """ % (self.from_address, self.to_address, self.body))
            self.from_address = "dev@incorporealtest.com"
            self.to_address = "dev@incorporealtest.com"

        self.save()  # in case it hasn't been saved yet and doesn't have an id
        if not hasattr(self, 'email'):
            self.email = self.createMessageObject()
        self.email.subject = self.subject
        self.email.body = self.body
        if self.is_html_body:
            self.email.content_subtype = "html"  # Main content is now text/html
        self.email.from_email = self.from_address or SERVICE_EMAIL_ADDRESS
        if not self.email.to:
            self.email.to = [self.to_address, ]
        if PRODUCTION:
            self.email.bcc = ["dev@incorporealtest.com", ]

        for attachment in self.attachments.all():
            file_name = (
                attachment.name | "file_upload"
            ) + attachment.file_extension
            file_via_url = urllib.request.urlopen(attachment.original)
            self.email.attach(file_name, file_via_url.read())

        logger.info("Sending email:")
        logger.info(email_to_string(self.email))

        if require_confirmation:
            return self.send_now()
        else:
            self.send_later()
            return None

    @start_new_thread  # cannot return a value, handle errors internally
    def send_later(self):
        self.send_for_realz()

    def send_now(self):
        try:
            self.send_for_realz()
            return True
        except Exception as e:
            logger.error(str(e))
            return False

    def send_for_realz(self):
        # if not LOCAL:
        self.email.send(fail_silently=False)
        self.sent_at = datetime.now()
        self.save()
