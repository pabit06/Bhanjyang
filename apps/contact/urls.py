from django.urls import path
from . import views

app_name = 'contact'  # This defines a namespace for the app's URLs

urlpatterns = [
    path('', views.contact_view, name='contact_view'),
    path('kym-form/', views.kym_form_view, name='kym_form'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
]
