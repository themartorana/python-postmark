import sys
import StringIO
import unittest

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
        json_payload = StringIO.StringIO()
        json_payload.write('{"Message": "", "ErrorCode": 406}')
        json_payload.seek(0)

        message = PMMail(sender='from@example.com', to='to@example.com',
            subject='Subject', text_body='Body', api_key='test')

        with mock.patch('postmark.core.urlopen', side_effect=HTTPError('',
            422, '', {}, json_payload)):
            self.assertRaises(PMMailInactiveRecipientException, message.send)

    def test_422_error_unprocessable_entity(self):
        json_payload = StringIO.StringIO()
        json_payload.write('{"Message": "", "ErrorCode": 422}')
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

        json_payload = StringIO.StringIO()
        json_payload.write('{"Message": "", "ErrorCode": 406}')
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

        json_payload = StringIO.StringIO()
        json_payload.write('{"Message": "", "ErrorCode": 422}')
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
