__version__ = '0.1.1'
__author__  = "David Martorana (themartorana@yahoo.com)"
__date__    = '2009-December-2'
__url__     = 'http://postmarkapp.com'
__copyright__ = "(C) 2009 David Martorana, Wildbit LLC, Python Software Foundation."

__doc__ = '''

    PMMail object for Postmark (http://postmarkapp.com)

    Version: ''' + __version__ + '''
    Author: ''' + __author__ + '''
    Date: ''' + __date__ + '''

    CHANGE LOG:

       Version 0.1.1:
           Initial release

    USEAGE:
        Make sure you have a Postmark account.  Visit
        http://postmarkapp.com to sign up for an account.
        Requires a Postmark API key.
    
        Import postmark.PMMail to use Postmark.  Check
        class documentation on PMMail object for more 
        information.
        
    DJANGO:
        The library can be used stand-alone with Django.  You can also
        add the setting 
        
        POSTMARK_API_KEY = 'your-key'
        
        to your settings.py file, and when you create a new PMMail object,
        it will grab the API key automatically.
        

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

#
# Imports (JSON library based on import try)

import sys
import urllib
import urllib2

try:
    import json                     
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise Exception('Cannot use PMMail without Python 2.6 or greater, or Python 2.4 or 2.5 and the "simplejson" library')

#
#
__POSTMARK_URL__ = 'http://api.postmarkapp.com/email'

class PMMail(object):
    '''
    The Postmark Mail object.
    '''
    def __init__(self, **kwargs):
        '''
        Keyword arguments are:
        api_key:        Your Postmark server API key
        sender:         Who the email is coming from, in either
                        "name@email.com" or "First Last <name@email.com>" format
        recipient:      Who to send the email to, in either
                        "name@email.com" or "First Last <name@email.com>" format
        subject:        Subject of the email
        html_body:      Email message in HTML
        text_body:      Email message in plain text
        '''
        # initiate properties
        self.__api_key = None
        self.__sender = None
        self.__recipient = None
        self.__subject = None
        self.__html_body = None
        self.__text_body = None
        #self.__multipart = False
        
        acceptable_keys = (
            'api_key', 
            'sender', 
            'recipient', 
            'subject', 
            'html_body', 
            'text_body', 
            #'multipart'
        )
        
        for key in kwargs:
            if key in acceptable_keys:
                setattr(self, '_PMMail__%s' % key, kwargs[key])
                
        # Set up the user-agent
        self.__user_agent = 'Python/%s (Postmark PMMail Library version %s)' % ('_'.join([str(var) for var in sys.version_info]), __version__)
        
        # Try to pull in the API key from Django
        try:
            import django
            from django.conf import settings as django_settings
            self.__api_key = django_settings.POSTMARK_API_KEY
            self.__user_agent = '%s (Django %s)' % (self.__user_agent, '_'.join([str(var) for var in django.VERSION]))
        except ImportError:
            pass
        
    #
    # Properties
    
    api_key = property(
        lambda self: self.__api_key,
        lambda self, value: setattr(self, '_PMMail__api_key', value),
        "The API Key for your server on Postmark"
    )

    sender = property(
        lambda self: self.__sender,
        lambda self, value: setattr(self, '_PMMail__sender', value),
        '''
        The sender, in either "name@email.com" or "First Last <name@email.com>" formats.  
        The address should match one of your Sender Signatures in Postmark.
        '''
    )
         
    recipient = property(
        lambda self: self.__recipient,
        lambda self, value: setattr(self, '_PMMail__recipient', value),
        'The recipient, in either "name@email.com" or "First Last <name@email.com>" formats'
    )

    subject = property(
        lambda self: self.__subject,
        lambda self, value: setattr(self, '_PMMail__subject', value),
        'The subject of your email message'
    )
    
    html_body = property(
        lambda self: self.__html_body,
        lambda self, value: setattr(self, '_PMMail__html_body', value),
        'The email message body, in html format'
    )
    
    text_body = property(
        lambda self: self.__text_body,
        lambda self, value: setattr(self, '_PMMail__text_body', value),
        'The email message body, in text format'
    )
    
#     multipart = property(
#         lambda self: self.__multipart,
#         lambda self, value: setattr(self, '_PMMail__multipart', value),
#         'The API Key for one of your servers on Postmark'
#     )
    
    def _check_values(self):
        '''
        Make sure all values are of the appropriate
        type and are not missing.
        '''
        if not self.__api_key:
            raise PMMailMissingValueException('Cannot send an e-mail without an Postmark API Key')
        elif not self.__sender:
            raise PMMailMissingValueException('Cannot send an e-mail without a sender')
        elif not self.__recipient:
            raise PMMailMissingValueException('Cannot send an e-mail without a recipient')
        elif not self.__subject:
            raise PMMailMissingValueException('Cannot send an e-mail without a subject')
        elif not self.__html_body and not self.__text_body:
            raise PMMailMissingValueException('Cannot send an e-mail without either an HTML or text version of your e-mail body')

    
    def send(self):
        '''
        Send the email through the Postmark system
        '''
        self._check_values()
        
        # Set up message dictionary
        json_message = {
            'From':     self.__sender,
            'To':       self.__recipient,
            'Subject':  self.__subject,
        }
        
        if self.__html_body:
            has_html = True
            json_message['HtmlBody'] = self.__html_body
            
        if self.__text_body:
            has_text = True
            json_message['TextBody'] = self.__text_body
            
#         if (self.__html_body and not self.__text_body) and self.__multipart:
#             # TODO: Set up regex to strip html
#             pass
        
        # Set up the url Request
        req = urllib2.Request(
            __POSTMARK_URL__,
            json.dumps(json_message),
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.__api_key,
                'User-agent': self.__user_agent
            }
        )
        
        # Attempt send
        try:
            result = urllib2.urlopen(req)
            result.close()
            if result.code == 200:
                return True
            else:
                raise PMMainSendException('Return code %d: %s' % (result.code, result.msg))
        except urllib2.HTTPError, err:
            if err.code == 401:
                raise PMMailUnauthorizedException('Sending Unauthorized - incorrect API key.', err)
            elif err.code == 422:
                try:
                    jsontxt = err.read()
                    jsonobj = json.loads(jsontxt)
                    desc = jsonobj['Message']
                except:
                    desc = 'Description not given'
                raise PMMailUnprocessableEntityException('Unprocessable Entity: %s' % desc)
            elif err.code == 500:
                raise PMMailServerErrorException('Internal server error at Postmark. Admins have been alerted.', err)
        except urllib2.URLError, err:
            if hasattr(err, 'reason'):
                raise PMMailURLException('URLError: Failed to reach the server: %s (See "inner_exception" for details)' % err.reason, err)
            elif hasattr(err, 'code'):
                raise PMMailURLException('URLError: %d: The server couldn\'t fufill the request. (See "inner_exception" for details)' % err.code, err)
            else:
                raise PMMailURLException('URLError: The server couldn\'t fufill the request. (See "inner_exception" for details)', err)
        

#
# Exceptions

class PMMailMissingValueException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class PMMailSendException(Exception):
    '''
    Base Postmark send exception
    '''
    def __init__(self, value, inner_exception=None):
        self.parameter = value
        self.inner_exception = inner_exception
    def __str__(self):
        return repr(self.parameter)

class PMMailUnauthorizedException(PMMailSendException):
    '''
    401: Unathorized sending due to bad API key
    '''
    pass

class PMMailUnprocessableEntityException(PMMailSendException):
    '''
    422: Unprocessable Entity - usually an exception with either the sender
    not having a matching Sender Signature in Postmark.  Read the message
    details for further information
    '''
    pass
    
class PMMailServerErrorException(PMMailSendException):
    '''
    500: Internal error - this is on the Postmark server side.  Errors are
    logged and recorded at Postmark.
    '''
    pass

class PMMailURLException(PMMailSendException):
    '''
    A URLError was caught - usually has to do with connectivity
    and the ability to reach the server.  The inner_exception will
    have the base URLError object.
    '''
    pass






