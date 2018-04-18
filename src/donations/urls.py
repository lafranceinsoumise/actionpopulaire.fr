from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^dons/$', views.AskAmountView.as_view(), name='donation_amount'),
    url(r'^dons/informations/$', views.PersonalInformationView.as_view(), name='donation_information')
]
