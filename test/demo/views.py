from django.shortcuts import render_to_response
from forms import EmailForm

def test_email(request):
    if request.method == 'GET':
        form = EmailForm()
    else:
        form = EmailForm(data=request.POST) 
        if form.is_valid():
            form.save()
    return render_to_response('mail.html', {'form': form})
            