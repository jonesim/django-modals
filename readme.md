[![PyPI version](https://badge.fury.io/py/django-nested-modals.svg)](https://badge.fury.io/py/django-nested-modals)

Add to installed apps in settings   
`'bootstrap_modals',`
    

Add to template  
`<script src="{% static 'django_modals/js/modals.js' %}"></script>` 
`<link rel="stylesheet" type="text/css" href="{% static 'django_modals/css/modals.css' %}"/>`


##### **Sample form and view**

    from crispy_forms.layout import Layout, Field   
    from django_modals.forms import ModelCrispyForm  
    from django_modals.view_mixins import BootstrapModelModalMixin   
    from .models import User

    class UserForm(ModelCrispyForm):
        class Meta:
            model = User
            fields = ['username']
            modal_title = ['Add user', 'Edit User']

        def post_init(self, *args, **kwargs):
            self.helper.layout = Layout(
                Field('username'),
                self.submit_button(css_class="btn-success"),
                self.cancel_button())
    
    class ModalUserForm(BootstrapModelModalMixin):
        form_class = UserForm

##### **Add modal URLS**
        path('modal/user/<slug:slug>/', modals.ModalUserForm.as_view(), name='usermodal')

##### **Generate javascript link in python**

    href_modal('usermodal', 'client-{}'.format(self.kwargs['pk']))
    onclick_modal('usermodal', 'client-{}'.format(self.kwargs['pk']))


###### **Adding different buttons**

 `self.button('Delete', [{'function': 'post_modal', 'button_name': 'delete'}], "btn-danger")`

in view the function button_buttonname will be called

`def button_delete(self, request, *args, **kwargs):`


The kwargs from the url are detemined in bootstrap_modals.views in split_slug

    if only one item split by -  
        'pk': item
    else
        'initial { even : odd }'                     
       
       
## **WIDGETS**

### Select2

In form 

    self.fields['field_name'].widget = Select2()`
            

**AJAX**

    self.fields['field_name'].widget = Select2(attrs={'ajax': True})       
    
Then in view

    def select2_field_name(self, request, *args, **kwargs):
        try:
            results = list(EventSubType.objects.filter(event_type_id=request.POST['field_name'])
                       .values('id').annotate(text=F('name'), value=F('id')))
        except ValueError:
            results = []
        return HttpResponse(json.dumps({'results': results}), content_type='application/json')     
