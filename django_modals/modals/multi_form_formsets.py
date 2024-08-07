from ajax_helpers.utils import ajax_command
from crispy_forms.layout import HTML
from django import forms
from django.forms.models import _get_foreign_key
from django_menus.menu import MenuItem
from html_classes.html import HtmlDiv

from django_modals.form_helpers import InlineFormset
from django_modals.forms import ModelCrispyForm, CrispyForm
from django_modals.modals import MultiForm


class FormSetItemForm(ModelCrispyForm):

    def ajax_button(self, text, function):
        return MenuItem(ajax_command('post_modal', button={'button': function, 'form_id': self.form_id}), text,
                              link_type=MenuItem.AJAX_COMMAND, css_classes='btn-sm btn-outline-secondary mr-2',
                        font_awesome='fas fa-trash')

    def post_init(self, *args, **kwargs):
        return [*self.fields, HTML(HtmlDiv(self.ajax_button('Delete', 'delete_form').render(),
                                           css_classes='text-right').render() +  '<hr>')]


class FormSetManagerForm(CrispyForm):

    def __init__(self, *args, length=None, manager_formset=None, **kwargs):
        self.length = length
        self.formset = manager_formset
        super().__init__(*args,  **kwargs)

    def ajax_button(self, text, function):
        return MenuItem(ajax_command('post_modal', button={'button': function, 'form_id': self.form_id}), text,
                              link_type=MenuItem.AJAX_COMMAND, css_classes='btn-sm btn-outline-secondary mr-2')

    def post_init(self, *args, **kwargs):
        self.fields['no_forms'] = forms.IntegerField(initial=self.length, widget=forms.HiddenInput)
        items = ['no_forms']
        if self.formset.max_no is None or self.length < self.formset.max_no:
            items.append(HTML(self.ajax_button('Add', 'add_form').render()))
        if self.length > self.formset.min_no:
            items.append(HTML(self.ajax_button('Remove', 'remove_form').render()))
        return items


class MultiFormFormSet:

    def __init__(self, multi_form, model, fields=None, no_forms=1, item_form=None, parent_model=None,
                 through_model=None, instance_ids=None, parent_id=None, min_no=0, max_no=None, table=False,
                 helper_class=None, **kwargs):
        self.model = model
        self.no_forms = int(multi_form.form_data.get(self.manager_id, {}).get('no_forms', no_forms))
        self.fields = fields
        self.item_form = item_form if item_form else FormSetItemForm
        self.parent_model = parent_model
        self.through_model = through_model
        self.fk = _get_foreign_key(parent_model, model).attname if parent_model else None
        self.forms = []
        self.manager = None
        self.instance_ids = instance_ids
        self.parent_id = parent_id
        self.min_no = min_no
        self.max_no = max_no
        self.kwargs = kwargs
        self.table = table
        self.helper_class = helper_class if helper_class else (InlineFormset if table else None)
        if self.parent_id and self.instance_ids is None and self.fk:
            self.instance_ids = self.model.objects.filter(**{self.fk:self.parent_id}).values_list('id', flat=True)

    @property
    def manager_id(self):
        return self.model.__name__ + 'Manager'

    def get_set_forms(self, form_data):
        if self.manager_id in form_data:
            self.no_forms = int(form_data[self.manager_id]['no_forms'])
        std_kwargs = dict(form_class=self.item_form, formset=self, **self.kwargs)
        if self.helper_class:
            std_kwargs['helper_class'] = self.helper_class
        if self.instance_ids:
            form_set = [MultiForm(self.model, self.fields + [HTML('delete')], pk=i, **std_kwargs)
                        for i in self.instance_ids]
            form_set += [MultiForm(self.model, self.fields, **std_kwargs)
                         for _c in range(0, self.no_forms - len(self.instance_ids))]
        else:
            form_set = [MultiForm(self.model, self.fields, **std_kwargs) for _c in range(0, self.no_forms)]
        manager = MultiForm(self.model, [], form_id=self.manager_id, length=len(form_set),
                            formset=self, manager_formset=self, form_class=FormSetManagerForm)
        self.manager = manager
        form_set.append(manager)
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
