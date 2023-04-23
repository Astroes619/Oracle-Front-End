from django.urls import path
from . import views
from . import service

urlpatterns = [
    path('', views.index, name='index'),
    path('live_feed/', views.live_feed, name='live_feed'), 
    path('dynamic_stream/', views.dynamic_stream, name='dynamic_stream'),
    path('eye_detection', views.eye_detection, name='eye_detection'),

]
