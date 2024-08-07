from ajax_helpers.utils import ajax_command
from crispy_forms.layout import HTML
from django import forms
from django.forms.models import _get_foreign_key
from django_menus.menu import MenuItem

from django_modals.modals import MultiForm
from django_modals.forms import ModelCrispyForm, CrispyForm


class FormSetItemForm(ModelCrispyForm):

    def post_init(self, *args, **kwargs):
        return [*self.fields, HTML('<hr>')]


class FormSetManagerForm(CrispyForm):

    def ajax_button(self, text, function):
        return MenuItem(ajax_command('post_modal', button={'button': function, 'form_id': self.form_id}), text,
                              link_type=MenuItem.AJAX_COMMAND, css_classes='btn-sm btn-outline-secondary mr-2')

    def post_init(self, *args, **kwargs):
        self.fields['no_forms'] = forms.IntegerField(initial=1, widget=forms.HiddenInput())
        items =  ['no_forms', HTML(self.ajax_button('Add', 'add_form').render())]
        if int(kwargs.get('data', {}).get('no_forms', 1)) > 1:
            items.append(HTML(self.ajax_button('Remove', 'remove_form').render()))
        return items


class MultiFormFormSet:

    def __init__(self, multi_form, model, fields=None, no_forms=1, item_form=None, parent_model=None,
                 through_model=None, instance_ids=None ):
        self.model = model
        self.no_forms = int(multi_form.form_data.get(self.manager_id, {}).get('no_forms', no_forms))
        self.fields = fields
        self.item_form = item_form if item_form else FormSetItemForm
        self.parent_model = parent_model
        self.through_model = through_model
        self.fk = _get_foreign_key(parent_model, model).attname if parent_model else None
        self.forms = None
        self.instance_ids = instance_ids
        multi_form.form_sets[self.manager_id] = self

    @property
    def manager_id(self):
        return self.model.__name__ + 'Manager'

    def get_forms(self):
        if self.instance_ids:
            form_set = [MultiForm(self.model, self.fields, form_class=self.item_form, pk=i) for i in self.instance_ids]
        else:
            form_set = [MultiForm(self.model, self.fields, form_class=self.item_form) for c in range(0, self.no_forms)]
        form_set.append(MultiForm(self.model, [], form_id=self.manager_id, form_class=FormSetManagerForm))
        return form_set

    @staticmethod
    def form_number(form_id):
        number = form_id.split('_')[-1]
        return int(number) if number.isnumeric() else 0

    def base_name(self):
        return self.model.__name__ + 'Form'

    def form_ids(self):
        ids = []
        if self.no_forms > 0:
            ids.append(self.base_name())
        for i in range(1, self.no_forms):
            ids.append(f'{self.base_name()}_{i}')
        return ids

    def link_forms(self, forms_dict):
        self.forms = [forms_dict[i] for i in self.form_ids()]

    def save_instances(self, owner=None, through_link=None):
        if self.through_model:
            through_fk = _get_foreign_key(through_link.__class__, self.through_model).attname
            child_fk = _get_foreign_key(self.model, self.through_model).attname
        for f in self.forms[:-1]:
            if self.fk:
                setattr(f.instance, self.fk, owner.id)
            f.instance.save()
            if self.through_model:
                self.through_model(**{through_fk:through_link.id, child_fk:f.instance.id}).save()

    @staticmethod
    def valid_forms(modal, forms_dict):
        for fs in modal.form_sets.values():
            fs.link_forms(forms_dict)
