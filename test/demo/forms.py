
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy 

class EmailForm(forms.Form):
    
    sender  = forms.EmailField(max_length=100, initial=settings.POSTMARK_SENDER)
    to      = forms.CharField(initial='bill@averline.com')
    subject = forms.CharField(initial='test email')    
    body    = forms.CharField(widget=forms.Textarea, initial='this is a test')    

    def save(self, fail_silently=False):
        """
        Build and send the email message.
        """
        send_mail(subject=ugettext_lazy(self.cleaned_data['subject']),
                  message=self.cleaned_data['body'], 
                  from_email=self.cleaned_data['sender'],
                  recipient_list=[addr.strip() for addr in self.cleaned_data['to'].split(',')],
                  fail_silently=fail_silently)



