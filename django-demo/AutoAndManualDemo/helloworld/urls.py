from django.urls import path

from . import views

urlpatterns = [
    path('', views.hello_world_view, name='helloworld'),
    path('auto/', views.auto_instrumentation, name='auto'),
]