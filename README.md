python-postmark library for [Postmark](http://postmarkapp.com)
================================================================

Supports Python 2.6 and greater, including 3.x.

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

Version 0.4.2
- Added in .track_opens to support open tracking
  See: http://developer.postmarkapp.com/developer-build.html#open-tracking

Version 0.4.1
- Merged proper handling of content_subtype in the Django backend - thanks Josh Owen!

Version 0.4.0
- Merged in Python 3 support - thanks Jacob!
- Moving minimum python version to 2.6. If you need 2.4 support, please continue to use v0.3.2!

*[See full changelog](https://github.com/themartorana/python-postmark/blob/master/CHANGELOG.md)*


Usage
-----
Make sure you have a Postmark account.  Visit http://postmarkapp.com to sign up for an account. Requires a Postmark API key.

Import `postmark.PMMail` to use Postmark. Check class documentation on `PMMail` object for more information.

Django
-------
The library can be used stand-alone with Django.  You can also add the settings:

```python
POSTMARK_API_KEY    = 'your-key'
POSTMARK_SENDER     = 'sender@signature.com'
POSTMARK_TEST_MODE  = [True/False]
```

to your settings.py file, and when you create a new PMMail object, it will grab the API key and sender automatically.  Make sure the sender email address is one of your Sender Signature email addresses in Postmark. You can also customize the name on the sender by changing the format from 'email@address.com' to 'Sender Name <email@address.com>' as long as the email part is part of a Sender Signature in Postmark.

Using `POSTMARK_TEST_MODE=True` will not actually send the email, but instead dump the JSON packet that would be sent to Postmarkapp.com. By default this setting is False, and if not specified, will be assumed to be False.

To reoute all Django E-Mail functions like `send_mail()` and `mail_admins()` through postmark use the following setting:

```python
EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
```

But keep in mind that even when using standard Django functions the sender must be registered with postmarkapp.com.


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
```

TODO
----

- Add automatic multipart emails via regex stripping of HTML tags from html_body if the .multipart property is set to True
- Refactor PMBounceManager Object and improve error handling within it.
- Add PMBounceManager example to the Django test.
- Write tests for large percentage of coverage
- *Fill out the "Usage" section*


