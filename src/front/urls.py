from django.conf.urls import url

from . import views

urlpatterns = [
    url('^inscription/$', views.SimpleSubscriptionView.as_view(), name='subscription'),
    url('^inscription/etranger/$', views.OverseasSubscriptionView.as_view(), name='subscription_overseas'),
    url('^inscription/success/$', views.SubscriptionSuccessView.as_view(), name='subscription_success')
]
