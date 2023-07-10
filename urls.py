from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chat'),
    path('process_prompt', views.process_prompt, name='process_prompt'),
]
