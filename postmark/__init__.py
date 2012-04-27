__version__         = '0.3.1'
__author__          = "Dave Martorana (http://davemartorana.com), Richard Cooper (http://frozenskys.com), Bill Jones (oraclebill), Dmitry Golomidov (deeGraYve)"
__date__            = '2011-January-31'
__url__             = 'http://postmarkapp.com'
__copyright__       = "(C) 2009-2010 David Martorana, Wildbit LLC, Python Software Foundation."
__contributors__    = "Dave Martorana (themartorana), Bill Jones (oraclebill), Richard Cooper (frozenskys), Miguel Araujo (maraujop), Patrick Lauber (digi604), Brian McFadden (brimcfadden), Joel Ryan (joelryan2k), Ben Hodgson (benhodgson), Dmitry Golomidov (deeGraYve)"

__doc__ = '''

    PMMail object for Postmark (http://postmarkapp.com)

    Version: ''' + __version__ + '''
    Author: ''' + __author__ + '''
    Last Updated: ''' + __date__ + '''
    Contributors: ''' + __contributors__ + '''

    USAGE:
        Make sure you have a Postmark account.  Visit
        http://postmarkapp.com to sign up for an account.
        Requires a Postmark API key.

        Import postmark.PMMail to use Postmark Sending.
        Check class documentation on PMMail object for
        more information.

        Import postmark.PMBatchMail object to send batches of
        messages. Either pass a "messages" argument or set
        the .messages property of the PMBatchMail object to an
        array of PMMail objects.

        Import postmark.PMBounceManager to use Postmark Bounce API.
        Check class documentation on PMBounceManager object for
        more information.

        Import postmark.PMInboundManager to parse the JSON data
        for each inbound email you want to process. Check class
        documentation on PMInboundManager for more information.

    DJANGO:
        The library can be used stand-alone with Django.  You can also
        add the setting

        POSTMARK_API_KEY = 'your-key'
        POSTMARK_SENDER = '<From Name> from@emailaddress.com'
        POSTMARK_TEST_MODE = True/False

        to your settings.py file, and when you create a new PMMail object,
        it will grab the API key automatically.

        Using POSTMARK_TEST_MODE=True will not actually send the email, but
        instead dump the JSON packet that would be sent to Postmarkapp.com.
        By default this setting is False, and if not specified, will
        be assumed to be False.

        To reoute all Django E-Mail functions like send_mail() and
        mail_admins() through postmark use the following setting:

        EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'

        But keep in mind that even when using standard Django functions
        the sender must be registered with postmarkapp.com.

    EXCEPTIONS:
        PMMailMissingValueException(Exception):
            One of the required values for attempting a send request is missing

        PMMailSendException(Exception):
            Base Postmark send exception

        PMMailUnauthorizedException(PMMailSendException):
            401: Unathorized sending due to bad API key

        PMMailUnprocessableEntityException(PMMailSendException):
            422: Unprocessable Entity - usually an exception with either the sender
            not having a matching Sender Signature in Postmark.  Read the message
            details for further information

        PMMailServerErrorException(PMMailSendException):
            500: Internal error - this is on the Postmark server side.  Errors are
            logged and recorded at Postmark.

        PMMailURLException(PMMailSendException):
            A URLError was caught - usually has to do with connectivity
            and the ability to reach the server.  The inner_exception will
            have the base URLError object.

    TODO:
        Add automatic multipart emails via regex stripping of HTML tags from html_body
        if the .multipart property is set to True

'''


from core import *
