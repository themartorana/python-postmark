__version__         = '0.4.7'
__author__          = "Dave Martorana (http://davemartorana.com), Richard Cooper (http://frozenskys.com), Bill Jones (oraclebill), Dmitry Golomidov (deeGraYve)"
__date__            = '2010-April-14'
__url__             = 'http://postmarkapp.com'
__copyright__       = "(C) 2009-2014 David Martorana, Wildbit LLC, Python Software Foundation."

#
# Imports (JSON library based on import try)

try:
    from email.mime.base import MIMEBase
except ImportError as e:
    from email import MIMEBase
    from httplib import HTTPConnection
    from urllib import urlencode
import sys
if sys.version_info[0] < 3:
    from urllib2 import Request, urlopen, HTTPError, URLError
else:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    from http.client import HTTPConnection
    from urllib.parse import urlencode

import collections
from contextlib import closing

try:
    import simplejson as json
except ImportError:
    try:
        # Try django first, for speedups, since we support the backend
        from django.utils import simplejson as json
    except ImportError:
        import json


#
#
class PMJSONEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if hasattr(o, '_proxy____str_cast') and isinstance(o._proxy____str_cast, collections.Callable):
                return o._proxy____str_cast()
            elif hasattr(o, '_proxy____text_cast') and isinstance(o._proxy____text_cast, collections.Callable):
                return o._proxy____text_cast()
            elif hasattr(o, '_proxy____unicode_cast'):
                return str(o)
        except:
            pass

        return super(PMJSONEncoder, self).default(o)

#
#
__POSTMARK_URL__ = 'https://api.postmarkapp.com/'


#
#
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
        to:             Who to send the email to, in either
                        "name@email.com" or "First Last <name@email.com>" format
                        Can be multiple values separated by commas (limit 20)
        cc:             Who to copy the email to, in either
                        "name@email.com" or "First Last <name@email.com>" format
                        Can be multiple values separated by commas (limit 20)
        bcc:            Who to blind copy the email to, in either
                        "name@email.com" or "First Last <name@email.com>" format
                        Can be multiple values separated by commas (limit 20)
        subject:        Subject of the email
        tag:            Use for adding categorizations to your email
        html_body:      Email message in HTML
        text_body:      Email message in plain text
        track_opens:    Whether or not to track if emails were opened or not
        custom_headers: A dictionary of key-value pairs of custom headers.
        attachments:    A list of tuples or email.mime.base.MIMEBase objects
                        describing attachments.
        '''
        # initialize properties
        self.__api_key = None
        self.__sender = None
        self.__reply_to = None
        self.__to = None
        self.__cc = None
        self.__bcc = None
        self.__subject = None
        self.__tag = None
        self.__html_body = None
        self.__text_body = None
        self.__track_opens = False
        self.__custom_headers = {}
        self.__attachments = []
        self.__message_id = None
        #self.__multipart = False

        acceptable_keys = (
            'api_key',
            'sender',
            'reply_to',
            'to', 'recipient', # 'recipient' is legacy
            'cc',
            'bcc',
            'subject',
            'tag',
            'html_body',
            'text_body',
            'track_opens',
            'custom_headers',
            'attachments',
            #'multipart'
        )

        for key in kwargs:
            if key in acceptable_keys:
                if key == 'recipient':
                    setattr(self, '_PMMail__to', kwargs[key])
                else:
                    setattr(self, '_PMMail__%s' % key, kwargs[key])

        # Set up the user-agent
        self.__user_agent = 'Python/%s (python-postmark library version %s)' % ('_'.join([str(var) for var in sys.version_info]), __version__)

        # Try to pull in the API key from Django
        try:
            from django import VERSION
            from django.conf import settings as django_settings
            self.__user_agent = '%s (Django %s)' % (self.__user_agent, '_'.join([str(var) for var in VERSION]))
            if not self.__api_key and hasattr(django_settings, 'POSTMARK_API_KEY'):
                self.__api_key = django_settings.POSTMARK_API_KEY
            if not self.__sender and hasattr(django_settings, 'POSTMARK_SENDER'):
                self.__sender = django_settings.POSTMARK_SENDER
            if not self.__track_opens and hasattr(django_settings, 'POSTMARK_TRACK_OPENS'):
                self.__track_opens = django_settings.POSTMARK_TRACK_OPENS
        except ImportError:
            pass

    #
    # Properties

    def _set_custom_headers(self, value):
        '''
        A special set function to ensure
        we're setting with a dictionary
        '''
        if value is None:
            setattr(self, '_PMMail__custom_headers', {})
        elif isinstance(value, dict):
            setattr(self, '_PMMail__custom_headers', value)
        else:
            raise TypeError('Custom headers must be a dictionary of key-value pairs')

    def _set_attachments(self, value):
        '''
        A special set function to ensure
        we're setting with a list
        '''
        if value is None:
            setattr(self, '_PMMail__attachments', [])
        elif isinstance(value, list):
            setattr(self, '_PMMail__attachments', value)
        else:
            raise TypeError('Attachments must be a list')

    api_key = property(
        lambda self: self.__api_key,
        lambda self, value: setattr(self, '_PMMail__api_key', value),
        lambda self: setattr(self, '_PMMail__api_key', None),
        '''
        The API Key for your rack server on Postmark
        '''
    )

    # "from" is a reserved word
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

    reply_to = property(
        lambda self: self.__reply_to,
        lambda self, value: setattr(self, '_PMMail__reply_to', value),
        lambda self: setattr(self, '_PMMail__reply_to', None),
        '''
        A reply-to address, in either "name@email.com" or "First Last <name@email.com>"
        format. The reply-to address does not have to be one of your Sender Signatures in Postmark.
        This allows a different reply-to address than sender address.
        '''
    )

    to = property(
        lambda self: self.__to,
        lambda self, value: setattr(self, '_PMMail__to', value),
        lambda self: setattr(self, '_PMMail__to', None),
        '''
        The recipients, in either "name@email.com" or "First Last <name@email.com>" formats
        '''
    )

    cc = property(
        lambda self: self.__cc,
        lambda self, value: setattr(self, '_PMMail__cc', value),
        lambda self: setattr(self, '_PMMail__cc', None),
        '''
        The cc recipients, in either "name@email.com" or "First Last <name@email.com>" formats
        '''
    )

    bcc = property(
        lambda self: self.__bcc,
        lambda self, value: setattr(self, '_PMMail__bcc', value),
        lambda self: setattr(self, '_PMMail__bcc', None),
        '''
        The bcc recipients, in either "name@email.com" or "First Last <name@email.com>" formats
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

    tag = property(
        lambda self: self.__tag,
        lambda self, value: setattr(self, '_PMMail__tag', value),
        lambda self: setattr(self, '_PMMail__tag', None),
        '''
        You can categorize outgoing email using the optional Tag property.
        If you use different tags for the different types of emails your application generates,
        you will be able to get detailed statistics for them through the Postmark user interface.
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

    track_opens = property(
        lambda self: self.__track_opens,
        lambda self, value: setattr(self, '_PMMail__track_opens', value),
        lambda self: setattr(self, '_PMMail__track_opens', None),
        '''
        Whether or not to track opens
        NOTE: Requires html_body to be set to work
        '''
    )

    custom_headers = property(
        lambda self: self.__custom_headers,
        _set_custom_headers,
        lambda self: setattr(self, '_PMMail__custom_headers', {}),
        '''
        Custom headers in a standard dictionary.
        NOTE: To change the reply to address, use the .reply_to
        property instead of a custom header.
        '''
    )

    attachments = property(
        lambda self: self.__attachments,
        _set_attachments,
        lambda self: setattr(self, '_PMMail__attachments', []),
        '''
        Attachments, Base64 encoded, in a list.
        '''
    )

    # multipart = property(
    #     lambda self: self.__multipart,
    #     lambda self, value: setattr(self, '_PMMail__multipart', value),
    #     'The API Key for one of your servers on Postmark'
    # )

    message_id = property(
        lambda self: self.__message_id,
        lambda self, value: setattr(self, '_PMMail__message_id', value),
        lambda self: setattr(self, '_PMMail__message_id', None),
        '''
        The email message ID, a UUID string.
        '''
    )
    
    #####################
    #
    # LEGACY SUPPORT
    #
    #####################

    recipient = property(
        lambda self: self.__to,
        lambda self, value: setattr(self, '_PMMail__to', value),
        lambda self: setattr(self, '_PMMail__to', None),
        '''
        The recipients, in either "name@email.com" or "First Last <name@email.com>" formats
        '''
    )

    #####################
    #
    # END LEGACY SUPPORT
    #
    #####################


    def _check_values(self):
        '''
        Make sure all values are of the appropriate
        type and are not missing.
        '''
        if not self.__api_key:
            raise PMMailMissingValueException('Cannot send an e-mail without a Postmark API Key')
        elif not self.__sender:
            raise PMMailMissingValueException('Cannot send an e-mail without a sender (.sender field)')
        elif not self.__to:
            raise PMMailMissingValueException('Cannot send an e-mail without at least one recipient (.to field)')
        elif not self.__subject:
            raise PMMailMissingValueException('Cannot send an e-mail without a subject')
        elif not self.__html_body and not self.__text_body:
            raise PMMailMissingValueException('Cannot send an e-mail without either an HTML or text version of your e-mail body')
        if self.__track_opens and not self.__html_body:
            print('WARNING: .track_opens set to True with no .html_body set. Tracking opens will not work; message will still send.')

    def to_json_message(self):
        json_message = {
            'From':     self.__sender,
            'To':       self.__to,
            'Subject':  self.__subject,
        }

        if self.__reply_to:
            json_message['ReplyTo'] = self.__reply_to

        if self.__cc:
            json_message['Cc'] = self.__cc

        if self.__bcc:
            json_message['Bcc'] = self.__bcc


        if self.__tag:
            json_message['Tag'] = self.__tag

        if self.__html_body:
            json_message['HtmlBody'] = self.__html_body

        if self.__text_body:
            json_message['TextBody'] = self.__text_body

        if self.__track_opens:
            json_message['TrackOpens'] = True

        if len(self.__custom_headers) > 0:
            cust_headers = []
            for key, value in self.__custom_headers.items():
                cust_headers.append({
                    'Name': key,
                    'Value': value
                })
            json_message['Headers'] = cust_headers

        if len(self.__attachments) > 0:
            attachments = []
            for attachment in self.__attachments:
                if isinstance(attachment, tuple):
                    attachments.append({
                            "Name": attachment[0],
                            "Content": attachment[1],
                            "ContentType": attachment[2],
                            })
                elif isinstance(attachment, MIMEBase):
                    attachments.append({
                            "Name": attachment.get_filename(),
                            "Content": attachment.get_payload(),
                            "ContentType": attachment.get_content_type(),
                            })
            json_message['Attachments'] = attachments

        return json_message

    def send(self, test=None):
        '''
        Send the email through the Postmark system.
        Pass test=True to just print out the resulting
        JSON message being sent to Postmark
        '''
        self._check_values()

        # Set up message dictionary
        json_message = self.to_json_message()

        # if (self.__html_body and not self.__text_body) and self.__multipart:
        #     # TODO: Set up regex to strip html
        #     pass

        # If test is not specified, attempt to read the Django setting
        if test is None:
            try:
                from django.conf import settings as django_settings
                test = getattr(django_settings, "POSTMARK_TEST_MODE", None)
            except ImportError:
                pass

        # If this is a test, just print the message
        if test:
            print('JSON message is:\n%s' % json.dumps(json_message, cls=PMJSONEncoder))
            return

        # Set up the url Request
        req = Request(
            __POSTMARK_URL__ + 'email',
            json.dumps(json_message, cls=PMJSONEncoder).encode('utf8'),
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.__api_key,
                'User-agent': self.__user_agent
            }
        )

        # Attempt send
        try:
            #print 'sending request to postmark: %s' % json_message
            result = urlopen(req)
            jsontxt = result.read().decode()
            result.close()
            if result.code == 200:
                self.message_id = json.loads(jsontxt).get('MessageID', None)
                return True
            else:
                raise PMMailSendException('Return code %d: %s' % (result.code, result.msg))
        except HTTPError as err:
            if err.code == 401:
                raise PMMailUnauthorizedException('Sending Unauthorized - incorrect API key.', err)
            elif err.code == 422:
                try:
                    jsontxt = err.read().decode()
                    jsonobj = json.loads(jsontxt)
                    desc = jsonobj['Message']
                except:
                    desc = 'Description not given'
                raise PMMailUnprocessableEntityException('Unprocessable Entity: %s' % desc)
            elif err.code == 500:
                raise PMMailServerErrorException('Internal server error at Postmark. Admins have been alerted.', err)
        except URLError as err:
            if hasattr(err, 'reason'):
                raise PMMailURLException('URLError: Failed to reach the server: %s (See "inner_exception" for details)' % err.reason, err)
            elif hasattr(err, 'code'):
                raise PMMailURLException('URLError: %d: The server couldn\'t fufill the request. (See "inner_exception" for details)' % err.code, err)
            else:
                raise PMMailURLException('URLError: The server couldn\'t fufill the request. (See "inner_exception" for details)', err)

# Simple utility that returns a generator to chunk up a list into equal parts
def _chunks(l, n):
    return (l[i:i+n] for i in range(0, len(l), n))

class PMBatchMail(object):
    # Maximum number of messages to be sent at once.
    # Ref: http://developer.postmarkapp.com/developer-build.html#batching-messages
    MAX_MESSAGES = 500

    def __init__(self, **kwargs):
        self.__api_key = None
        self.__messages = []

        acceptable_keys = (
            'api_key',
            'messages'
        )

        for key in kwargs:
            if key in acceptable_keys:
                setattr(self, '_PMBatchMail__%s' % key, kwargs[key])

        # Set up the user-agent
        self.__user_agent = 'Python/%s (python-postmark library version %s)' % ('_'.join([str(var) for var in sys.version_info]), __version__)

        # Try to pull in the API key from Django
        try:
            from django import VERSION
            from django.conf import settings as django_settings
            self.__user_agent = '%s (Django %s)' % (self.__user_agent, '_'.join([str(var) for var in VERSION]))
            if not self.__api_key and hasattr(django_settings, 'POSTMARK_API_KEY'):
                self.__api_key = django_settings.POSTMARK_API_KEY
        except ImportError:
            pass

    api_key = property(
        lambda self: self.__api_key,
        lambda self, value: setattr(self, '_PMBatchMail__api_key', value),
        lambda self: setattr(self, '_PMBatchMail__api_key', None),
        '''
        The API Key for your rack server on Postmark
        '''
    )

    messages = property(
        lambda self: self.__messages,
        lambda self, value: setattr(self, '_PMBatchMail__messages', value),
        lambda self: setattr(self, '_PMBatchMail__messages', None),
        '''
        Messages to send
        '''
    )

    def add_message(self, message):
        '''
        Add a message to the batch
        '''
        self.__messages.append(message)

    def remove_message(self, message):
        '''
        Remove a message from the batch
        '''
        if message in self.__messages:
            self.__messages.remove(message)

    def _check_values(self):
        '''
        Make sure all values are of the appropriate
        type and are not missing.
        '''
        for message in self.__messages:
            message._check_values()

    def send(self, test=None):
        # Check messages for completeness prior to attempting to send
        self._check_values()

        # If test is not specified, attempt to read the Django setting
        if test is None:
            try:
                from django.conf import settings as django_settings
                test = getattr(django_settings, "POSTMARK_TEST_MODE", None)
            except ImportError:
                pass

        # Split up into groups of 500 messages for sending
        for messages in _chunks(self.messages, PMBatchMail.MAX_MESSAGES):
            json_message = []
            for message in messages:
                json_message.append(message.to_json_message())

            req = Request(
                __POSTMARK_URL__ + 'email/batch',
                json.dumps(json_message, cls=PMJSONEncoder).encode('utf8'),
                {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Postmark-Server-Token': self.__api_key,
                    'User-agent': self.__user_agent
                }
            )

            # If this is a test, just print the message
            if test:
                print('JSON message is:\n%s' % json.dumps(json_message, cls=PMJSONEncoder))
                continue

            # Attempt send
            try:
                result = urlopen(req)
                jsontxt = result.read()
                result.close()
                if result.code == 200:
                    results = json.loads(jsontxt)
                    for i, res in enumerate(results):
                        self.__messages[i].message_id = res.get("MessageID", None)
                else:
                    raise PMMailSendException('Return code %d: %s' % (result.code, result.msg))
            except HTTPError as err:
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
            except URLError as err:
                if hasattr(err, 'reason'):
                    raise PMMailURLException('URLError: Failed to reach the server: %s (See "inner_exception" for details)' % err.reason, err)
                elif hasattr(err, 'code'):
                    raise PMMailURLException('URLError: %d: The server couldn\'t fufill the request. (See "inner_exception" for details)' % err.code, err)
                else:
                    raise PMMailURLException('URLError: The server couldn\'t fufill the request. (See "inner_exception" for details)', err)
        return True



class PMBounceManager(object):
    '''
    The Postmark Bounce object.
    '''
    def __init__(self, **kwargs):
        '''
        Keyword arguments are:
        api_key:        Your Postmark server API key
        '''
        # initialize properties
        self.__api_key = None


        acceptable_keys = (
            'api_key',
        )

        for key in kwargs:
            if key in acceptable_keys:
                setattr(self, '_PMBounceManager__%s' % key, kwargs[key])

        # Set up the user-agent
        self.__user_agent = 'Python/%s (python-postmark library version %s)' % ('_'.join([str(var) for var in sys.version_info]), __version__)

        # Try to pull in the API key from Django
        try:
            from django import VERSION
            from django.conf import settings as django_settings
            if not self.__api_key and hasattr(django_settings, 'POSTMARK_API_KEY'):
                self.__api_key = django_settings.POSTMARK_API_KEY
            self.__user_agent = '%s (Django %s)' % (self.__user_agent, '_'.join([str(var) for var in VERSION]))
        except ImportError:
            pass

    def _check_values(self):
        '''
        Make sure all values are of the appropriate
        type and are not missing.
        '''
        if not self.__api_key:
            raise PMMailMissingValueException('Cannot check bounces without a Postmark Server API Key')

    api_key = property(
        lambda self: self.__api_key,
        lambda self, value: setattr(self, '_PMMail__api_key', value),
        lambda self: setattr(self, '_PMMail__api_key', None),
        '''
        The API Key for your rack server on Postmark
        '''
    )

    def delivery_stats(self):
        '''
        Returns a summary of inactive emails and bounces by type.
        '''
        self._check_values()

        req = Request(
            __POSTMARK_URL__ + 'deliverystats',
            None,
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.__api_key,
                'User-agent': self.__user_agent
            }
        )

        # Attempt send
        try:
            #print 'sending request to postmark:'
            result = urlopen(req)
            with closing(result):
                if result.code == 200:
                    return json.loads(result.read())
                else:
                    raise PMMailSendException('Return code %d: %s' % (result.code, result.msg))

        except HTTPError as err:
            return err


    def get_all(self, inactive='', email_filter='', tag='', count=25, offset=0):
        '''
        Fetches a portion of bounces according to the specified input criteria. The count and offset
        parameters are mandatory. You should never retrieve all bounces as that could be excessively
        slow for your application. To know how many bounces you have, you need to request a portion
        first, usually the first page, and the service will return the count in the TotalCount property
        of the response.
        '''

        self._check_values()

        params = '?inactive=' + inactive + '&emailFilter=' + email_filter +'&tag=' + tag
        params += '&count=' + str(count) + '&offset=' + str(offset)

        req = Request(
            __POSTMARK_URL__ + 'bounces' + params,
            None,
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.__api_key,
                'User-agent': self.__user_agent
            }
        )

        # Attempt send
        try:
            #print 'sending request to postmark:'
            result = urlopen(req)
            with closing(result):
                if result.code == 200:
                    return json.loads(result.read())
                else:
                    raise PMMailSendException('Return code %d: %s' % (result.code, result.msg))

        except HTTPError as err:
            return err


    def get_single(self, bounce_id):
        '''
        Get details about a single bounce. Note that the bounce ID is a numeric value that you
        typically obtain after a getting a list of bounces.
        '''
        self._check_values()

        req = Request(
            __POSTMARK_URL__ + '/bounces/' + str(bounce_id),
            None,
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.__api_key,
                'User-agent': self.__user_agent
            }
        )

        # Attempt send
        try:
            #print 'sending request to postmark:'
            result = urlopen(req)
            with closing(result):
                if result.code == 200:
                    return json.loads(result.read())
                else:
                    raise PMMailSendException('Return code %d: %s' % (result.code, result.msg))

        except HTTPError as err:
            return err


    def get_dump(self, bounce_id):
        '''
        Returns the raw source of the bounce Postmark accepted. If Postmark does not have a dump for
        that bounce, it will return an empty string.
        '''
        self._check_values()

        req_url = __POSTMARK_URL__ + '/bounces/' + str(bounce_id) + '/dump'
        #print req_url

        req = Request(
        req_url,
            None,
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.__api_key,
                'User-agent': self.__user_agent
            }
        )

        # Attempt send
        try:
            print('sending request to postmark:')
            result = urlopen(req)
            with closing(result):
                if result.code == 200:
                    return json.loads(result.read())
                else:
                    raise PMMailSendException('Return code %d: %s' % (result.code, result.msg))

        except HTTPError as err:
            return err

    def get_tags(self):
        '''
        Returns a list of tags used for the current server.
        '''
        self._check_values()

        req = Request(
            __POSTMARK_URL__ + 'bounces/tags',
            None,
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.__api_key,
                'User-agent': self.__user_agent
            }
        )

        # Attempt send
        try:
            #print 'sending request to postmark:'
            result = urlopen(req)
            with closing(result):
                if result.code == 200:
                    return json.loads(result.read())
                else:
                    raise PMMailSendException('Return code %d: %s' % (result.code, result.msg))

        except HTTPError as err:
            return err

    def activate(self, bounce_id):
        '''
        Activates a deactivated bounce.
        '''
        self._check_values()
        req_url = '/bounces/' + str(bounce_id) + '/activate'
        #print req_url
        h1 = HTTPConnection('api.postmarkapp.com')
        dta = urlencode({"data":"blank"}).encode('utf8')
        req = h1.request('PUT',
        req_url,
            dta,
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.__api_key,
                'User-agent': self.__user_agent
            }
        )
        r=h1.getresponse()
        return json.loads(r.read())


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
