from django.conf.urls import url

from . import views

urlpatterns = [
    url('^inscription/$', views.SimpleSubscriptionView.as_view(), name='subscription'),
    url('^inscription/etranger/$', views.OverseasSubscriptionView.as_view(), name='subscription_overseas'),
    url('^inscription/succes/$', views.SubscriptionSuccessView.as_view(), name='subscription_success'),
    url('^evenement/creer/$', views.CreateEventView.as_view(), name='create_event'),
    url('^evenement/creer/succes/$', views.CreateEventSuccessView, name='create_event_success'),
    url('^evenement/modifier/(?P<pk>[0-9a-f-]+)/', views.UpdateEventView.as_view(), name='edit_event'),
    url('^evenement/modifier/succes/', views.UpdateEventSuccessView.as_view(), name='update_event_success'),
]
