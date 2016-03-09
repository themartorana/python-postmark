"""
Postmark Mixin
"""
from tornado.options import options as opt
import postmark

class PostmarkMixin(object):
    def send_email(self, **kwargs):
        subject=kwargs.get('subject')
        body=kwargs.get('body')
        to=kwargs.get('to')
        postsig = opt.postmark_signature
        postemail = opt.postmark_sendemail

        sender = postmark.PMMail()
        sender.sender = postemail
        sender.api_key = postsig
        sender.to = to
        sender.html_body = body
        sender.subject = subject
        sender.send(test=False)
