CHANGELOG for python-postmark
===============================

Version 0.5.6
--------------
- Encoding issues (PR #91)
- Add message_stream attribute to PMMail (PR #94)

Version 0.5.5
--------------
- Setting to return message IDs in django backend (PR #89)

Version 0.5.4
--------------
- Fix for sending batch emails with templates (PR #87)

Version 0.5.3
--------------
- Allow empty "to" field if "bcc" is populated (PR #83)

Version 0.5.2
--------------
- EmailMultiAlternatives content_subtype fix (PR #82)

Version 0.5.1
--------------
- Postmark metadata support (PR #75)

Version 0.5.0
--------------
- Postmark templates support (PR #63)

Version 0.4.12
--------------
- EmailMessage.reply_to fix and housekeeping

Version 0.4.11
--------------
- Account for EmailMessage.reply_to (#68)

Version 0.4.10
--------------
- Added inline images support (#47)
- Fix for attachments in Python 3 (issue #66, PR #67)

Version 0.4.9
-------------
- Tornado mixin (tigrus)
- PMJSONEncoder unicode changes (mattrobenolt)

Version 0.4.8
-------------
- Handle inactive recipient errors (nicholasserra)

Version 0.4.7
-------------
- Fix base64 encoding in Django API for attachments (thanosd)

Version 0.4.6
-------------
- Fix for using content subtype in Django backend for HTML email (ryankuczka)

Version 0.4.5
-------------
- Fix for Python 3 support (issue #42, PR #43) (mflaxman)

Version 0.4.4
-------------
- Minor code cleanup (Stranger6667)
- Fix for Django 1.5+ ugettext_lazy strings being improperly converted (#11, #41) (justinabrahms, rduffield)
- Demo brought up to Django 1.6 (catskul)

Version 0.4.3
-------------
- Added message_id property to messages for post-send record-tracking (jdavisp3)

Version 0.4.2
-------------
- Added in .track_opens to support open tracking
  See: http://developer.postmarkapp.com/developer-build.html#open-tracking
- Added POSTMARK_TRACK_OPENS setting to the Django backend (danxshap)
- Don't require `content_subtype` in Django backend to be set to `"html"` (danxshap)

Version 0.4.1
--------------
- Merged proper handling of content_subtype in the Django backend - thanks Josh Owen!

Version 0.4.0
--------------
- Merged in Python 3 support - thanks Jacob!
- Moving minimum Python version to 2.6. If you need 2.4 support, please continue to use v0.3.2!

Version 0.3.2
--------------
- Uses simplejson if installed for faster C _speedups
- PMBatchMail properly chunks large message sets
- Django backend uses PMBatchMail properly
- Use https by default
- Proper testing API key out of the box
- Cleaned up some PMBatchMail properties
- Added a few utility methods (add_message, remove_message) to PMBatchMail
- Added proper value checking to PMBatchMail pre-send
- A BIG THANKS to all new contributors!

Version 0.3.1
--------------
- Added batch-messaging support (PMBatchMail object) (deeGraYve)
  See http://developer.postmarkapp.com/developer-build.html#batching-messages

Version 0.2.3
--------------
- Merged in support for adding a tag through the Django backend (joelryan2k)
- Merged in support for POSTMARK_TEST_MODE overriding and beter settings defaults (benhodgson)

Version 0.2.2
--------------
- Merged in email mime import fix from brimcfadden

Version 0.2.1
--------------
- Merged in POSTMARK_TEST_MODE Django setting from maraujop

Version 0.2.0
--------------
- Merged with frozenskys/master to bring in PMBounceManager
- Support for multiple to/cc (limit: 20 per)
- Changed .recipient to .to (legacy support for .recipient left in)
- Tag support (.tag) added
- Fixed the email endpoint
- Fixed a Django backend issue for multiple recipients (max 20)

Version 0.1.6
--------------
- Added a new PMBounceManager Class that allows easy access to the PostMark
  bounce API.

Version 0.1.5
--------------
- Added ".cc" property for carbon copy recipients. Changed django_backend to 
  support multiple recipients, and to use "to" rather than "recipients" on the django
  mail object to prevent accidental leakage of BCC recipients.
  
Version 0.1.4
--------------
- Added ".reply_to" property.  The "ReplyTo" custom header is unallowed by Postmark 
  now, and their documentation has been updated to reflect the change.
  http://developer.postmarkapp.com

Version 0.1.3
--------------
- Major fix to the way properties were being used, fixes doc strings in properties
- "custom_headers" is now always a dict, even if set to None

Version 0.1.2
--------------
- Added 'custom_headers' property (must be a dictionary) to PMMail object
- Added optional 'test' argument to send function to print JSON message instead of actually sending it

Version 0.1.1:
--------------
- Initial release 
