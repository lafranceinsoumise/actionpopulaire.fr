from django.urls import path

from . import views

urlpatterns = [
    path('ses_bounce', views.SesBounceView().as_view(), name='ses_bounce'),
    path('sendgrid_bounce', views.SendgridBounceView().as_view(), name='sendgrid_bounce')
]
