import sys
import unittest
from email.mime.image import MIMEImage

from io import BytesIO

if sys.version_info[0] < 3:
    from urllib2 import HTTPError
else:
    from urllib.error import HTTPError

import mock

from postmark import (
    PMBatchMail, PMMail, PMMailInactiveRecipientException,
    PMMailUnprocessableEntityException, PMMailServerErrorException
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

    def test_inline_attachments(self):
        image = MIMEImage('image_file', 'png', name='image.png')
        image_with_id = MIMEImage('inline_image_file', 'png', name='image_with_id.png')
        image_with_id.add_header('Content-ID', '<image2@postmarkapp.com>')
        inline_image = MIMEImage('inline_image_file', 'png', name='inline_image.png')
        inline_image.add_header('Content-ID', '<image3@postmarkapp.com>')
        inline_image.add_header('Content-Disposition', 'inline', filename='inline_image.png')

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
        assert json_message['Attachments'] == [
            {'Name': 'TextFile', 'Content': 'content', 'ContentType': 'text/plain'},
            {'Name': 'InlineImage', 'Content': 'image_content', 'ContentType': 'image/png', 'ContentID': 'cid:image@postmarkapp.com'},
            {'Name': 'image.png', 'Content': 'aW1hZ2VfZmlsZQ==\n', 'ContentType': 'image/png'},
            {'Name': 'image_with_id.png', 'Content': 'aW5saW5lX2ltYWdlX2ZpbGU=\n', 'ContentType': 'image/png', 'ContentID': 'image2@postmarkapp.com'},
            {'Name': 'inline_image.png', 'Content': 'aW5saW5lX2ltYWdlX2ZpbGU=\n', 'ContentType': 'image/png', 'ContentID': 'cid:image3@postmarkapp.com'},
        ]


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


if __name__ == '__main__':
    if not settings.configured:
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                }
            },
            INSTALLED_APPS=[
            ],
            MIDDLEWARE_CLASSES=[],
        )

    unittest.main()
