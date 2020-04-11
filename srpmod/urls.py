from django.conf.urls import url
from . import views

app_name = 'srpmod'  # Put this before the actual module in the load order.

urlpatterns = [
    url(r'^set_char/(?P<fleet_id>(\w+))/$', views.srp_set_payment_character, name='set_char'),
    url(r'^set_char/$', views.srp_set_payment_character, name='set_char'),
    url(r'^open_id/(?P<id>(\w+))/$', views.srp_open_info, name='open_id'),
    
]