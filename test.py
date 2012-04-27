import os.path
import unittest
from postmark import PMInboundManager as PostmarkInbound


class PostmarkInboundTest(unittest.TestCase):

    def setUp(self):
        json_data = open('test/inbound/fixtures/valid_http_post.json').read()
        self.inbound = PostmarkInbound(json=json_data)

    def tearDown(self):
        if os.path.exists('./test/inbound/chart.png'):
            os.remove('./test/inbound/chart.png')
        if os.path.exists('./test/inbound/chart2.png'):
            os.remove('./test/inbound/chart2.png')

    def test_should_have_a_subject(self):
        assert 'Hi There' == self.inbound.subject()

    def test_should_have_a_bcc(self):
        assert 'hi@fbi.com' == self.inbound.bcc()

    def test_should_have_a_cc(self):
        assert 'sample.cc@emailDomain.com' == self.inbound.cc()[0]['Email']

    def test_should_have_a_reply_to(self):
        assert 'new-comment+sometoken@yeah.com' == self.inbound.reply_to()

    def test_should_have_a_mailbox_hash(self):
        assert 'moitoken' == self.inbound.mailbox_hash()

    def test_should_have_a_tag(self):
        assert 'yourit' == self.inbound.tag()

    def test_should_have_a_message_id(self):
        assert 'a8c1040e-db1c-4e18-ac79-bc5f64c7ce2c' == self.inbound.message_id()

    def test_should_be_from_someone(self):
        assert self.inbound.sender()['Name'] == 'Bob Bobson' and \
            self.inbound.sender()['Email'] == 'bob@bob.com'

    def test_should_have_a_html_body(self):
        assert '<p>We no speak americano</p>' == self.inbound.html_body()

    def test_should_have_a_text_body(self):
        assert '\nThis is awesome!\n\n' == self.inbound.text_body()

    def test_should_be_to_someone(self):
        assert 'api-hash@inbound.postmarkapp.com' == self.inbound.to()[0]['Email']

    def test_should_have_header_mime_version(self):
        assert '1.0' == self.inbound.headers('MIME-Version')

    def test_should_have_header_received_spf(self):
        assert 'Pass (sender SPF authorized) identity=mailfrom; client-ip=209.85.160.180; helo=mail-gy0-f180.google.com; envelope-from=myUser@theirDomain.com; receiver=451d9b70cf9364d23ff6f9d51d870251569e+ahoy@inbound.postmarkapp.com' == self.inbound.headers('Received-SPF')

    def test_should_have_spam_version(self):
        assert 'SpamAssassin 3.3.1 (2010-03-16) onrs-ord-pm-inbound1.wildbit.com' == self.inbound.headers('X-Spam-Checker-Version')

    def test_should_have_spam_status(self):
        assert 'No' == self.inbound.headers('X-Spam-Status')

    def test_should_have_spam_score(self):
        assert '-0.1' == self.inbound.headers('X-Spam-Score')

    def test_should_have_spam_test(self):
        assert 'DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,SPF_PASS' == self.inbound.headers('X-Spam-Tests')

    def test_should_have_two_attachments(self):
        assert 2 == len(self.inbound.attachments())

    def test_should_have_attachment(self):
        assert True == self.inbound.has_attachments()

    def test_attachment_should_have_content_length(self):
        for a in self.inbound.attachments():
            assert a.content_length() is not None

    def test_attachment_should_have_conent_type(self):
        for a in self.inbound.attachments():
            assert a.content_type() is not None

    def test_attachment_should_have_name(self):
        for a in self.inbound.attachments():
            assert a.name() is not None

    def test_attachment_should_download(self):
        for a in self.inbound.attachments():
            a.download('./test/inbound/')

        assert True == os.path.exists('./test/inbound/chart.png')
        assert True == os.path.exists('./test/inbound/chart2.png')

    def test_send_date(self):
        assert 2012 == self.inbound.send_date().year

if __name__ == "__main__":
    unittest.main()
