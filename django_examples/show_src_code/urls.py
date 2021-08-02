from django.urls import path

from .modals import BaseSourceCodeModal

app_name = 'show_src_code'
urlpatterns = [
    path('modal/source_code/<str:slug>/', BaseSourceCodeModal.as_view(), name='source_code_modal'),
]
