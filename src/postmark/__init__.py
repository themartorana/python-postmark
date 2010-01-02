__version__ = '0.1.2'
__author__  = "David Martorana (themartorana@yahoo.com)"
__date__    = '2010-January-01'
__url__     = 'http://postmarkapp.com'
__copyright__ = "(C) 2009-2010 David Martorana, Wildbit LLC, Python Software Foundation."

__doc__ = '''

    PMMail object for Postmark (http://postmarkapp.com)

    Version: ''' + __version__ + '''
    Author: ''' + __author__ + '''
    Date: ''' + __date__ + '''

    CHANGE LOG:

        Version 0.1.3
            - Major fix to the way properties were being used, fixes doc strings in properties
            - "custom_headers" is now always a dict, even if set to None

        Version 0.1.2
            - Added 'custom_headers' property (must be a dictionary) to PMMail object
            - Added optional 'test' argument to send function to print JSON message instead of actually sending it
            
        Version 0.1.1:
            - Initial release

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
        POSTMARK_SENDER = '<From Name> from@emailaddress.com'
        
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
        raise Exception('Cannot use python-postmark library without Python 2.6 or greater, or Python 2.4 or 2.5 and the "simplejson" library')

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
        custom_headers: A dictionary of key-value pairs of custom headers.
                        For example, use "Reply-To" header to change the reply to
                        address of your message
        '''
        # initiate properties
        self.__api_key = None
        self.__sender = None
        self.__recipient = None
        self.__subject = None
        self.__html_body = None
        self.__text_body = None
        self.__custom_headers = {}
        #self.__multipart = False
        
        acceptable_keys = (
            'api_key', 
            'sender', 
            'recipient', 
            'subject', 
            'html_body', 
            'text_body', 
            'custom_headers',
            #'multipart'
        )
        
        for key in kwargs:
            if key in acceptable_keys:
                setattr(self, '_PMMail__%s' % key, kwargs[key])
                
        # Set up the user-agent
        self.__user_agent = 'Python/%s (python-postmark library version %s)' % ('_'.join([str(var) for var in sys.version_info]), __version__)
        
        # Try to pull in the API key from Django
        try:
            import django
            from django.conf import settings as django_settings
            self.__api_key = django_settings.POSTMARK_API_KEY
            self.__user_agent = '%s (Django %s)' % (self.__user_agent, '_'.join([str(var) for var in django.VERSION]))
            self.__sender = django_settings.POSTMARK_SENDER
        except ImportError:
            pass
        
    #
    # Properties
    
    def _set_custom_headers(self, value):
        '''
        A special set function to ensure 
        we're setting with a dictionary
        '''
        if value == None:
            setattr(self, '_PMMail__custom_headers', {})
        elif type(value) == dict:
            setattr(self, '_PMMail__custom_headers', value)
        else:
            raise TypeError('Custom headers must be a dictionary of key-value pairs')
    
    
    api_key = property(
        lambda self: self.__api_key,
        lambda self, value: setattr(self, '_PMMail__api_key', value),
        lambda self: setattr(self, '_PMMail__api_key', None), 
        '''
        The API Key for your rack server on Postmark
        '''
    )

    sender = property(
        lambda self: self.__sender,
        lambda self, value: setattr(self, '_PMMail__sender', value),
        lambda self: setattr(self, '_PMMail__sender', None),
        '''
        The sender, in either "name@email.com" or "First Last <name@email.com>" formats.  
        The address should match one of your Sender Signatures in Postmark.
        Specifying the address in the second fashion will allow you to replace
        the name of the sender as it appears in the recipient's email client.
        '''
    )
         
    recipient = property(
        lambda self: self.__recipient,
        lambda self, value: setattr(self, '_PMMail__recipient', value),
        lambda self: setattr(self, '_PMMail__recipient', None),
        '''
        The recipient, in either "name@email.com" or "First Last <name@email.com>" formats
        '''
    )

    subject = property(
        lambda self: self.__subject,
        lambda self, value: setattr(self, '_PMMail__subject', value),
        lambda self: setattr(self, '_PMMail__subject', None),
        '''
        The subject of your email message
        '''
    )
    
    html_body = property(
        lambda self: self.__html_body,
        lambda self, value: setattr(self, '_PMMail__html_body', value),
        lambda self: setattr(self, '_PMMail__html_body', None),
        '''
        The email message body, in html format
        '''
    )
    
    text_body = property(
        lambda self: self.__text_body,
        lambda self, value: setattr(self, '_PMMail__text_body', value),
        lambda self: setattr(self, '_PMMail__text_body', None),
        '''
        The email message body, in text format
        '''
    )
    
    custom_headers = property(
        lambda self: self.__custom_headers,
        _set_custom_headers, 
        lambda self: setattr(self, '_PMMail__custom_headers', {}),
        '''
        The email message body, in text format
        Reply-To: custom header will set a different reply-to address
        '''
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

    
    def send(self, test=False):
        '''
        Send the email through the Postmark system.  
        Pass test=True to just print out the resulting
        JSON message being sent to Postmark
        '''
        self._check_values()
        
        # Set up message dictionary
        json_message = {
            'From':     self.__sender,
            'To':       self.__recipient,
            'Subject':  self.__subject,
        }
        
        if self.__html_body:
            json_message['HtmlBody'] = self.__html_body
            
        if self.__text_body:
            json_message['TextBody'] = self.__text_body
            
        if len(self.__custom_headers) > 0:
            cust_headers = []
            for key in self.__custom_headers.keys():
                cust_headers.append({
                    'Name': key,
                    'Value': self.__custom_headers[key]
                })
            json_message['Headers'] = cust_headers
            
#         if (self.__html_body and not self.__text_body) and self.__multipart:
#             # TODO: Set up regex to strip html
#             pass
        
        # If this is a test, just print the message
        if test:
            print 'JSON message is:\n%s' % json.dumps(json_message)
            return
            
        
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






