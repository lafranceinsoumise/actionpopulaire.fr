from django.conf.urls import url

from . import views

urlpatterns = [
    url('^ses_bounce$', views.SesBounceView().as_view(), name='ses_bounce'),
    url('^sendgrid_bounce$', views.SendgridBounceView().as_view(), name='sendgrid_bounce')
]
