[![Build Status](https://travis-ci.org/themartorana/python-postmark.svg?branch=master)](https://travis-ci.org/themartorana/python-postmark)
[![PyPI](https://img.shields.io/pypi/v/python-postmark.svg)](https://pypi.python.org/pypi/python-postmark)
[![PyPI](https://img.shields.io/pypi/dm/python-postmark.svg)](https://pypi.python.org/pypi/python-postmark)

python-postmark library for [Postmark](http://postmarkapp.com)
================================================================

Supports Python 2.7 and greater, including 3.x.

Includes:

- PMMail
- PMBatchMail
- PMBounceManager 
- Django email backend (postmark.django_backend.EmailBackend)

Contributors
--------------
See [CONTRIBUTORS.md](https://github.com/themartorana/python-postmark/blob/master/CONTRIBUTORS.md).

Changelog
----------
*[See full changelog](https://github.com/themartorana/python-postmark/blob/master/CHANGELOG.md)*

Usage
-----
Make sure you have a Postmark account.  Visit http://postmarkapp.com to sign up for an account. Requires a Postmark API key.

Import `postmark.PMMail` to use Postmark. Check class documentation on `PMMail` object for more information.
    
Django
-------
The library can be used stand-alone with Django.  You can also add the settings:

```python 
POSTMARK_API_KEY     = 'your-key'
POSTMARK_SENDER      = 'sender@signature.com'
POSTMARK_TEST_MODE   = [True/False]
POSTMARK_TRACK_OPENS = [True/False]
POSTMARK_RETURN_MESSAGE_ID = [True/False] Return list of sent message-ids while using Django backend. Defaults to False, returns count.
```

to your settings.py file, and when you create a new PMMail object, it will grab the API key and sender automatically.  Make sure the sender email address is one of your Sender Signature email addresses in Postmark. You can also customize the name on the sender by changing the format from 'email@address.com' to 'Sender Name <email@address.com>' as long as the email part is part of a Sender Signature in Postmark.

Using `POSTMARK_TEST_MODE=True` will not actually send the email, but instead dump the JSON packet that would be sent to Postmarkapp.com. By default this setting is False, and if not specified, will be assumed to be False.

To reroute all Django E-Mail functions like `send_mail()` and `mail_admins()` through postmark use the following setting:

```python
EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
```

But keep in mind that even when using standard Django functions the sender must be registered with postmarkapp.com.

#### Adding a Tag to the Message
One tag can be set via Django Mail system by setting both the `X-PM-Tag` header, and setting the variable `tag` on the EmailMessage object.

e.g. using `EmailMultiAlternatives` from `django.core.mail`

```python
from django.core.mail import get_connection, EmailMultiAlternatives

tag = "my-tag"
headers = { 'X-PM-Tag': tag }

mail = EmailMultiAlternatives(subject, msg_plain, from_email, recipients, connection=connection, headers=headers)

mail.tag = tag
mail.send()
```

#### Setting the `message_stream`
```python
from django.core.mail import get_connection, EmailMultiAlternatives

mail = EmailMultiAlternatives(subject, msg_plain, from_email, recipients, connection=connection, headers=headers)

mail.message_stream = "broadcast"
mail.send()
```

    
Tornado
-------

For tornado support of postmark implemented as Mixin. 

Example of usage:

```python
import tornado.web
import tornado.options
from postmark.tornado_mixin import PostmarkMixin

tornado.options.define('postmark_signature', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
tornado.options.define('postmark_sendemail', 'email@email.com')

class EmailHandler(tornado.web.RequestHandler, PostmarkMixin):
    def post(self):
        to = 'test@test.com'
        body = 'This is test message'
        subject = 'Test Message'
        self.send_email(body=body, to=to, subject=subject)
```

Postmark Templates
------------------
Getting an HTML email to look good on most email clients can be tricky. The whole reason to send email as HTML is to make an impression on the reader. If the client renders it badly, its worse than just sending a plain text email.

Postmark understands this and has created a templating system to make it easier to create robust HTML emails. For more information, see: [Special delivery: Postmark templates] (https://postmarkapp.com/blog/special-delivery-postmark-templates)

Using templates in python-postmark is straightforward: 

1. Create a template for your server on the Postmark website.

2. Get the ID for the template from the page on Postmark where the template was made.

3. Make a dict in python that contains the values of the template variables. Postmark calls this the "TemplateModel"

4. Instantiate PMMail with the the appropriate kwargs, including "template_id" and "template_model". NOTE: "subject" kwarg is ignored.

5. Call the send() method

Here is an example:

```
from postmark.core import PMMail

template_model = {
    'firm_name':'Acme Law',
    'total': '125.43',
    'date': 'July 10, 2016',
    'client_name': 'Joe Blow',
    'invoice_details': [
        {
            'description': 'Credit report',
            'amount': '25.43'
        },
        {
            'description': 'Legal Services',
            'amount': '100.00'
        }
    ],
    'opening_balance': '2000.00',
    'closing_balance': "<span class='negative_amount'>1800.00</span>",
    'notes': 'Thank you for choosing Acme Law.',
}
pm = PMMail(to='groucho.marx@gmail.com', sender='harpo.marx@gmail.com',
            template_id=123456, template_model=template_model)
    pm.send()
```


Exceptions
-----------

```python
class PMMailMissingValueException(Exception):
    #One of the required values for attempting a send request is missing

class PMMailSendException(Exception):
    #Base Postmark send exception

class PMMailUnauthorizedException(PMMailSendException):
    #401: Unathorized sending due to bad API key

class PMMailUnprocessableEntityException(PMMailSendException):
    # 422: Unprocessable Entity - usually an exception with either the sender not having a matching Sender Signature in Postmark.  Read the message details for further information

class PMMailServerErrorException(PMMailSendException):
    #500: Internal error - this is on the Postmark server side.  Errors are logged and recorded at Postmark.

class PMMailURLException(PMMailSendException):
    #A URLError was caught - usually has to do with connectivity and the ability to reach the server.  The inner_exception will have the base URLError object.

class PMMailInactiveRecipientException(PMMailSendException):
    # 406: You tried to send a message to a recipient that has been marked as inactive. If this was a batch operation, the rest of the messages were still sent.
```

TODO
----
    
- Add automatic multipart emails via regex stripping of HTML tags from html_body if the .multipart property is set to True
- Refactor PMBounceManager Object and improve error handling within it.
- Add PMBounceManager example to the Django test.
- Write tests for large percentage of coverage
