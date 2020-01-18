from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
import views

urlpatterns = [
    url(r'', views.test_email),
]
