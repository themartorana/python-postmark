#Postmark library for Python 2.4 and greater

PMMail, PMBatchMail, and PMBounceManager objects, as well as Django email backend (postmark.django_backend.EmailBackend) for [Postmark](http://postmarkapp.com)

##Contributors
- Dave Martorana (themartorana)
- Bill Jones (oraclebill)
- Richard Cooper (frozenskys)
- Miguel Araujo (maraujop)
- Patrick Lauber (digi604)
- Brian McFadden (brimcfadden)
- Joel Ryan (joelryan2k)
- Ben Hodgson (benhodgson)
- Dmitry Golomidov (deeGraYve)
- José Padilla (jpadilla)
- (Did I miss anyone?)

##Python Information
Works on **Python 2.4** and better. Versions 2.4 and 2.5 will require the "simplejson" library from http://code.google.com/p/simplejson/ Python 2.6 has JSON support built in.

##Change Log
###Version 0.3.1
- Added batch-messaging support (PMBatchMail object) (deeGraYve) See http://developer.postmarkapp.com/developer-build.html#batching-messages

###Version 0.2.3
- Merged in support for adding a tag through the Django backend (joelryan2k)
- Merged in support for POSTMARK_TEST_MODE overriding and beter settings defaults (benhodgson)

###Version 0.2.2
- Merged in email mime import fix from brimcfadden

###Version 0.2.1
- Merged in POSTMARK_TEST_MODE Django setting from maraujop

###Version 0.2.0
- Merged with frozenskys/master to bring in PMBounceManager
- Support for multiple to/cc (limit: 20 per)
- Changed .recipient to .to (legacy support for .recipient left in)
- Tag support (.tag) added
- Fixed the email endpoint
- Fixed a Django backend issue for multiple recipients (max 20)

###Version 0.1.6
- Added a new PMBounceManager Class that allows easy access to the PostMark bounce API.

###Version 0.1.5
- Added ".cc" property for carbon copy recipients. Changed django_backend to support multiple recipients, and to use "to" rather than "recipients" on the django mail object to prevent accidental leakage of BCC recipients.

###Version 0.1.4
- Added ".reply_to" property.  The "ReplyTo" custom header is unallowed by Postmark now, and their documentation has been updated to reflect the change. http://developer.postmarkapp.com

###Version 0.1.3
- Major fix to the way properties were being used, fixes doc strings in properties
- "custom_headers" is now always a dict, even if set to None

###Version 0.1.2
- Added 'custom_headers' property (must be a dictionary) to PMMail object
- Added optional 'test' argument to send function to print JSON message instead of actually sending it

###Version 0.1.1:
- Initial release

##Usage
Make sure you have a Postmark account. Visit http://postmarkapp.com to sign up for an account. Requires a Postmark API key.

Import `postmark.PMMail` to use Postmark Sending. Check class documentation on PMMail object for more information.

Import `postmark.PMBatchMail` object to send batches of messages. Either pass a "messages" argument or set the .messages property of the PMBatchMail object to an array of PMMail objects.

Import `postmark.PMBounceManager` to use Postmark Bounce API. Check class documentation on PMBounceManager object for more information.

Import `postmark.PMInboundManager` to parse the JSON data for each inbound email you want to process. Check class documentation on PMInboundManager for more information.

##Django:
The library can be used stand-alone with Django.  You can also add the settings:

```
POSTMARK_API_KEY    = 'your-key'
POSTMARK_SENDER     = 'sender@signature.com'
POSTMARK_TEST_MODE  = [True/False]
```

to your **settings.py** file, and when you create a new PMMail object, it will grab the API key and sender automatically.  Make sure the sender email address is one of your Sender Signature email addresses in Postmark. You can also customize the name on the sender by changing the format from 'email@address.com' to `'Sender Name <email@address.com>'` as long as the email part is part of a Sender Signature in Postmark.

Using `POSTMARK_TEST_MODE=True` will not actually send the email, but instead dump the JSON packet that would be sent to Postmarkapp.com. By default this setting is False, and if not specified, will be assumed to be False.

To reoute all Django E-Mail functions like `send_mail()` and `mail_admins()` through postmark use the following setting:

```
EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
```

But keep in mind that even when using standard Django functions the sender must be registered with postmarkapp.com.

##Exceptions
####PMMailMissingValueException(Exception)
One of the required values for attempting a send request is missing

####PMMailSendException(Exception)
Base Postmark send exception

####PMMailUnauthorizedException(PMMailSendException)
401: Unathorized sending due to bad API key

####PMMailUnprocessableEntityException(PMMailSendException)
422: Unprocessable Entity - usually an exception with either the sender not having a matching Sender Signature in Postmark. Read the message details for further information

####PMMailServerErrorException(PMMailSendException)
500: Internal error - this is on the Postmark server side. Errors are logged and recorded at Postmark.

####PMMailURLException(PMMailSendException)
A URLError was caught - usually has to do with connectivity and the ability to reach the server.  The inner_exception will have the base URLError object.

##To-do
- Add automatic multipart emails via regex stripping of HTML tags from html_body if the .multipart property is set to True
- Refactor PMBounceManager Object and improve error handling within it.
- Add PMBounceManager example to the Django test.
