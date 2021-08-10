import sys
import inspect
from django.urls import path
from django_modals.modals import BaseModal, ModelFormModal


# Can create all url patterns in a module that are subclasses of BaseModal

# Add the modal view module to url_patterns e.g
# path('modal/classes/', include('examples.views.basic_modals')),

# and place the line below at the end of the file with the modal views
# urlpatterns = get_urls(__name__)

def get_urls(module_name):
    urls = []
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isclass(obj) and obj.__module__ == module_name and issubclass(obj, (BaseModal, ModelFormModal)):
            urls.append(path(f'{name}/<slug:slug>/', obj.as_view(), name=name))
    return urls
