import json
import sys
import unittest
from email.mime.image import MIMEImage

from io import BytesIO

from django.core import mail
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.test import TestCase

from postmark.django_backend import EmailBackend

if sys.version_info[0] < 3:
    from StringIO import StringIO
    from urllib2 import HTTPError
else:
    from io import StringIO
    from urllib.error import HTTPError

import mock

from postmark import (
    PMBatchMail, PMMail, PMMailInactiveRecipientException,
    PMMailUnprocessableEntityException, PMMailServerErrorException,
    PMMailMissingValueException, PMBounceManager
)

from django.conf import settings


class PMMailTests(unittest.TestCase):
    def test_406_error_inactive_recipient(self):
        json_payload = BytesIO()
        json_payload.write(b'{"Message": "", "ErrorCode": 406}')
        json_payload.seek(0)

        message = PMMail(sender='from@example.com', to='to@example.com',
            subject='Subject', text_body='Body', api_key='test')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            422, '', {}, json_payload)):
            self.assertRaises(PMMailInactiveRecipientException, message.send)

    def test_422_error_unprocessable_entity(self):
        json_payload = BytesIO()
        json_payload.write(b'{"Message": "", "ErrorCode": 422}')
        json_payload.seek(0)

        message = PMMail(sender='from@example.com', to='to@example.com',
            subject='Subject', text_body='Body', api_key='test')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            422, '', {}, json_payload)):
            self.assertRaises(PMMailUnprocessableEntityException, message.send)

    def test_500_error_server_error(self):
        message = PMMail(sender='from@example.com', to='to@example.com',
            subject='Subject', text_body='Body', api_key='test')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            500, '', {}, None)):
            self.assertRaises(PMMailServerErrorException, message.send)

    def assert_missing_value_exception(self, message_func, error_message):
        with self.assertRaises(PMMailMissingValueException) as cm:
            message_func()
        self.assertEqual(error_message, cm.exception.parameter)

    def test_send(self):
        # Confirm send() still works as before use_template was added
        message = PMMail(sender='from@example.com', to='to@example.com',
            subject='Subject', text_body='Body', api_key='test')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            200, '', {}, None)):
            message.send()

    def test_missing_subject(self):
        # No subject should raise exception when using send()
        message = PMMail(sender='from@example.com', to='to@example.com',
                         text_body='Body', api_key='test')
        self.assert_missing_value_exception(
            message.send,
            'Cannot send an e-mail without a subject'
        )

    def test_missing_recipient_fields(self):
        # No recipient should raise exception when using send()
        message = PMMail(sender='from@example.com', subject='test',
                         text_body='Body', api_key='test')
        self.assert_missing_value_exception(
            message.send,
            'Cannot send an e-mail without at least one recipient (.to field or .bcc field)'
        )

    def test_missing_to_field_but_populated_bcc_field(self):
        # No to field but populated bcc field should not raise exception when using send()
        message = PMMail(sender='from@example.com', subject='test', bcc='to@example.com',
                         text_body='Body', api_key='test')
        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('', 200, '', {}, None)):
            message.send()

    def test_check_values_bad_template_data(self):
        # Try sending with template ID only
        message = PMMail(api_key='test', sender='from@example.com', to='to@example.com', template_id=1)
        self.assert_missing_value_exception(
            message.send,
            'Cannot send a template e-mail without a both template_id and template_model set'
        )

    def test_send_with_template(self):
        # Both template_id and template_model are set, so send should work.
        message = PMMail(api_key='test', sender='from@example.com', to='to@example.com',
                         template_id=1, template_model={'junk': 'more junk'})
        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            200, '', {}, None)):
            message.send()

    def test_inline_attachments(self):
        image = MIMEImage(b'image_file', 'png', name='image.png')
        image_with_id = MIMEImage(b'inline_image_file', 'png', name='image_with_id.png')
        image_with_id.add_header('Content-ID', '<image2@postmarkapp.com>')
        inline_image = MIMEImage(b'inline_image_file', 'png', name='inline_image.png')
        inline_image.add_header('Content-ID', '<image3@postmarkapp.com>')
        inline_image.add_header('Content-Disposition', 'inline', filename='inline_image.png')

        expected = [
            {'Name': 'TextFile', 'Content': 'content', 'ContentType': 'text/plain'},
            {'Name': 'InlineImage', 'Content': 'image_content', 'ContentType': 'image/png', 'ContentID': 'cid:image@postmarkapp.com'},
            {'Name': 'image.png', 'Content': 'aW1hZ2VfZmlsZQ==', 'ContentType': 'image/png'},
            {'Name': 'image_with_id.png', 'Content': 'aW5saW5lX2ltYWdlX2ZpbGU=', 'ContentType': 'image/png', 'ContentID': 'image2@postmarkapp.com'},
            {'Name': 'inline_image.png', 'Content': 'aW5saW5lX2ltYWdlX2ZpbGU=', 'ContentType': 'image/png', 'ContentID': 'cid:image3@postmarkapp.com'},
        ]
        json_message = PMMail(
            sender='from@example.com', to='to@example.com', subject='Subject', text_body='Body', api_key='test',
            attachments=[
                ('TextFile', 'content', 'text/plain'),
                ('InlineImage', 'image_content', 'image/png', 'cid:image@postmarkapp.com'),
                image,
                image_with_id,
                inline_image,
            ]
        ).to_json_message()
        assert len(json_message['Attachments']) == len(expected)
        for orig, attachment in zip(expected, json_message['Attachments']):
            for k, v in orig.items():
                assert orig[k] == attachment[k].rstrip()

    def test_send_metadata(self):
        message = PMMail(api_key='test', sender='from@example.com', to='to@example.com',
                         subject='test', text_body='test', metadata={'test': 'test'})
        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            200, '', {}, None)):
            message.send()

    def test_send_metadata_invalid_format(self):
        self.assertRaises(TypeError, PMMail, api_key='test', sender='from@example.com', to='to@example.com',
                         subject='test', text_body='test', metadata={'test': {}})


class PMBatchMailTests(unittest.TestCase):
    def test_406_error_inactive_recipient(self):
        messages = [
            PMMail(
                sender='from@example.com', to='to@example.com',
                subject='Subject', text_body='Body', api_key='test'
            ),
            PMMail(
                sender='from@example.com', to='to@example.com',
                subject='Subject', text_body='Body', api_key='test'
            ),
        ]

        json_payload = BytesIO()
        json_payload.write(b'{"Message": "", "ErrorCode": 406}')
        json_payload.seek(0)

        batch = PMBatchMail(messages=messages, api_key='test')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            422, '', {}, json_payload)):
            self.assertRaises(PMMailInactiveRecipientException, batch.send)

    def test_422_error_unprocessable_entity(self):
        messages = [
            PMMail(
                sender='from@example.com', to='to@example.com',
                subject='Subject', text_body='Body', api_key='test'
            ),
            PMMail(
                sender='from@example.com', to='to@example.com',
                subject='Subject', text_body='Body', api_key='test'
            ),
        ]

        json_payload = BytesIO()
        json_payload.write(b'{"Message": "", "ErrorCode": 422}')
        json_payload.seek(0)

        batch = PMBatchMail(messages=messages, api_key='test')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            422, '', {}, json_payload)):
            self.assertRaises(PMMailUnprocessableEntityException, batch.send)

    def test_500_error_server_error(self):
        messages = [
            PMMail(
                sender='from@example.com', to='to@example.com',
                subject='Subject', text_body='Body', api_key='test'
            ),
            PMMail(
                sender='from@example.com', to='to@example.com',
                subject='Subject', text_body='Body', api_key='test'
            ),
        ]

        batch = PMBatchMail(messages=messages, api_key='test')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            500, '', {}, None)):
            self.assertRaises(PMMailServerErrorException, batch.send)


class PMBounceManagerTests(unittest.TestCase):
    def test_activate(self):
        bounce = PMBounceManager(api_key='test')

        with mock.patch('postmark.core.HTTPConnection.getresponse') as mock_response:
            mock_response.return_value = StringIO('{"test": "test"}')
            self.assertEqual(bounce.activate(1), {'test': 'test'})


class EmailBackendTests(TestCase):

    def test_send_multi_alternative_html_email(self):
        # build a message and send it
        message = EmailMultiAlternatives(
            connection=EmailBackend(api_key='dummy'),
            from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='hello there'
        )
        message.attach_alternative('<b>hello</b> there', 'text/html')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('', 200, '', {}, None)) as transport:
            message.send()
            data = json.loads(transport.call_args[0][0].data.decode('utf-8'))
            self.assertEqual('hello there', data['TextBody'])
            self.assertEqual('<b>hello</b> there', data['HtmlBody'])

    def test_send_content_subtype_email(self):
        # build a message and send it
        message = EmailMessage(
            connection=EmailBackend(api_key='dummy'),
            from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='<b>hello</b> there'
        )
        message.content_subtype = 'html'

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('', 200, '', {}, None)) as transport:
            message.send()
            data = json.loads(transport.call_args[0][0].data.decode('utf-8'))
            self.assertEqual('<b>hello</b> there', data['HtmlBody'])
            self.assertFalse('TextBody' in data)

    def test_send_multi_alternative_with_subtype_html_email(self):
        """
        Client uses EmailMultiAlternative but instead of specifying a html alternative they insert html content
        into the main message and specify message_subtype
        :return:
        """
        message = EmailMultiAlternatives(
            connection=EmailBackend(api_key='dummy'),
            from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='<b>hello</b> there'
        )
        # NO alternatives attached.  subtype specified instead
        message.content_subtype = 'html'

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('', 200, '', {}, None)) as transport:
            message.send()
            data = json.loads(transport.call_args[0][0].data.decode('utf-8'))
            self.assertFalse('TextBody' in data)
            self.assertEqual('<b>hello</b> there', data['HtmlBody'])

    def test_message_count_single(self):
        """Test backend returns count sending single message."""
        with self.settings(POSTMARK_RETURN_MESSAGE_ID=False):
            message = EmailMessage(
                connection=EmailBackend(api_key='dummy'),
                from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='<b>hello</b> there'
            )
            
            with mock.patch('postmark.core.urlopen') as transport:
                transport.return_value.read.return_value.decode.return_value = """
                    {
                      "To": "recipient@test.com",
                      "SubmittedAt": "2014-02-17T07:25:01.4178645-05:00",
                      "MessageID": "0a129aee-e1cd-480d-b08d-4f48548ff48d",
                      "ErrorCode": 0,
                      "Message": "OK"
                    }
                    """
                transport.return_value.code = 200
                response = message.send()
                self.assertEqual(response, 1)

    def test_message_count_batch(self):
        """Test backend returns count sending batch messages."""
        with self.settings(POSTMARK_RETURN_MESSAGE_ID=False):

            message1 = EmailMessage(
                connection=EmailBackend(api_key='dummy'),
                from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='<b>hello</b> there'
            )
            message2 = EmailMessage(
                connection=EmailBackend(api_key='dummy'),
                from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='<b>hello</b> there'
            )

            with mock.patch('postmark.core.urlopen') as transport:
                transport.return_value.read.return_value.decode.return_value = """
                    [
                      {
                        "ErrorCode": 0,
                        "Message": "OK",
                        "MessageID": "b7bc2f4a-e38e-4336-af7d-e6c392c2f817",
                        "SubmittedAt": "2010-11-26T12:01:05.1794748-05:00",
                        "To": "receiver1@example.com"
                      },
                      {
                        "ErrorCode": 0,
                        "Message": "OK",
                        "MessageID": "e2ecbbfc-fe12-463d-b933-9fe22915106d",
                        "SubmittedAt": "2010-11-26T12:01:05.1794748-05:00",
                        "To": "receiver2@example.com"
                      }
                    ]
                    """
                transport.return_value.code = 200

                # Directly send bulk mail via django
                connection = mail.get_connection()
                sent_messages = connection.send_messages([message1, message2])
                self.assertEqual(sent_messages, 2)

    def test_message_id_single(self):
        """Test backend returns message sending single message with setting True"""
        with self.settings(POSTMARK_RETURN_MESSAGE_ID=True):
            message = EmailMessage(
                connection=EmailBackend(api_key='dummy'),
                from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='<b>hello</b> there'
            )
            
            with mock.patch('postmark.core.urlopen') as transport:
                transport.return_value.read.return_value.decode.return_value = """
                    {
                      "To": "recipient@test.com",
                      "SubmittedAt": "2014-02-17T07:25:01.4178645-05:00",
                      "MessageID": "0a129aee-e1cd-480d-b08d-4f48548ff48d",
                      "ErrorCode": 0,
                      "Message": "OK"
                    }
                    """
                transport.return_value.code = 200
                message_ids = message.send()
                self.assertEqual(message_ids[0], "0a129aee-e1cd-480d-b08d-4f48548ff48d")

    def test_message_id_batch(self):
        """Test backend returns message sending batch messages with setting True"""
        with self.settings(POSTMARK_RETURN_MESSAGE_ID=True):

            message1 = EmailMessage(
                connection=EmailBackend(api_key='dummy'),
                from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='<b>hello</b> there'
            )
            message2 = EmailMessage(
                connection=EmailBackend(api_key='dummy'),
                from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='<b>hello</b> there'
            )

            with mock.patch('postmark.core.urlopen') as transport:
                transport.return_value.read.return_value.decode.return_value = """
                    [
                      {
                        "ErrorCode": 0,
                        "Message": "OK",
                        "MessageID": "b7bc2f4a-e38e-4336-af7d-e6c392c2f817",
                        "SubmittedAt": "2010-11-26T12:01:05.1794748-05:00",
                        "To": "receiver1@example.com"
                      },
                      {
                        "ErrorCode": 0,
                        "Message": "OK",
                        "MessageID": "e2ecbbfc-fe12-463d-b933-9fe22915106d",
                        "SubmittedAt": "2010-11-26T12:01:05.1794748-05:00",
                        "To": "receiver2@example.com"
                      }
                    ]
                    """
                transport.return_value.code = 200

                # Directly send bulk mail via django
                connection = mail.get_connection()
                sent_messages = connection.send_messages([message1, message2])
                self.assertIn('b7bc2f4a-e38e-4336-af7d-e6c392c2f817', sent_messages)
                self.assertIn('e2ecbbfc-fe12-463d-b933-9fe22915106d', sent_messages)

    def test_send_attachment_bytes(self):
        message = EmailMultiAlternatives(
            connection=EmailBackend(api_key='dummy'),
            from_email='from@test.com', to=['recipient@test.com'], subject='html test', body='hello there'
        )

        f = StringIO(u'1,2,3')
        message.attach('filename.csv', f.read(), 'text/csv')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('', 200, '', {}, None)):
            message.send()
    


if __name__ == '__main__':
    if not settings.configured:
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:'
                }
            },
            INSTALLED_APPS=[
            ],
            MIDDLEWARE_CLASSES=[],
            EMAIL_BACKEND = 'postmark.django_backend.EmailBackend',
            POSTMARK_API_KEY='dummy',
        )

    unittest.main()
