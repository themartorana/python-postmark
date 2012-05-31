from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, EmailMultiAlternatives

from core import PMMail, PMBatchMail

class PMEmailMessage(EmailMessage):
    def __init__(self, *args, **kwargs):
        if 'tag' in kwargs:
            self.tag = kwargs['tag']
            del kwargs['tag']
        else:
            self.tag = None

        super(PMEmailMessage, self).__init__(*args, **kwargs)
        
class PMEmailMultiAlternatives(EmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        if 'tag' in kwargs:
            self.tag = kwargs['tag']
            del kwargs['tag']
        else:
            self.tag = None

        super(PMEmailMultiAlternatives, self).__init__(*args, **kwargs)
        
class EmailBackend(BaseEmailBackend):
    
    def __init__(self, api_key=None, default_sender=None, **kwargs):
        """
        Initialize the backend.
        """
        super(EmailBackend, self).__init__(**kwargs)
        self.api_key = api_key if api_key is not None else getattr(settings, 'POSTMARK_API_KEY', None)
        if self.api_key is None:
            raise ImproperlyConfigured('POSTMARK API key must be set in Django settings file or passed to backend constructor.')            
        self.default_sender = getattr(settings, 'POSTMARK_SENDER', default_sender)
        self.test_mode = getattr(settings, 'POSTMARK_TEST_MODE', False) 
                                    
    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return         
        sent = self._send(email_messages)
        if sent:
            return len(email_messages)
        return 0
        
        
    def _build_message(self, message):
        """A helper method to convert a PMEmailMessage to a PMMail"""
        if not message.recipients():
            return False            
        recipients = ','.join(message.to)
        recipients_bcc = ','.join(message.bcc)
        
        html_body = None
        if isinstance(message, EmailMultiAlternatives):
            for alt in message.alternatives:
                if alt[1] == "text/html":
                    html_body=alt[0]
                    break
        
        reply_to = None
        custom_headers = {}           
        if message.extra_headers and isinstance(message.extra_headers, dict):
            if message.extra_headers.has_key('Reply-To'):
                reply_to = message.extra_headers.pop('Reply-To')
            if len(message.extra_headers):
                custom_headers = message.extra_headers
        attachments = []
        if message.attachments and isinstance(message.attachments, list):
            if len(message.attachments):
                attachments = message.attachments
        
        postmark_message = PMMail(api_key=self.api_key, 
                              subject=message.subject,
                              sender=message.from_email,
                              to=recipients,
                              bcc=recipients_bcc,
                              text_body=message.body,
                              html_body=html_body,
                              reply_to=reply_to,
                              custom_headers=custom_headers,
                              attachments=attachments)
        
        postmark_message.tag = getattr(message, 'tag', None)
        return postmark_message

    def _send(self, messages):
        """A helper method that does the actual sending."""
        if len(messages) == 1:
            to_send = self._build_message(messages[0])
            if to_send == False:
                # The message was missing recipients.
                # Bail.
                return False
        else:
            pm_messages = map(self._build_message, messages)
            pm_messages = filter(lambda m: m != False, pm_messages)
            if len(pm_messages) == 0:
                # If after filtering, there aren't any messages
                # to send, bail.
                return False
            to_send = PMBatchMail(messages=pm_messages)
        try:
            to_send.send(test=self.test_mode)
        except:
            if self.fail_silently:
                return False
            raise
        return True
