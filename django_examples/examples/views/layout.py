from django.forms.fields import CharField

from django_modals.forms import ModelCrispyForm
from django_modals.fields import FieldEx, MultiFieldRow
from django_modals.widgets.select2 import Select2
from django_modals.form_helpers import SmallHelper, TwoColumnHelper, RegularHelper, HorizontalHelper, \
    TwoColumnRegularHelper, NoLabelsRegularHelper

from show_src_code.modals import ModelFormModal

from examples.models import Person, Note

from .views import MainMenuTemplateView


class Layout(MainMenuTemplateView):
    template_name = 'example_views/layout.html'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            'regular,-',
            ('regular_2c,-', 'Regular 2 column'),
            ('layout2,-', 'Table Form'),
            ('nolabels,-', 'No labels'),
        )

        self.add_menu('horizontal_forms', 'buttons', ).add_items(
            'horizontal,-',
            ('horizontal_placeholder,-', 'Horizontal Placeholder'),
            ('notefield,-', 'Note Field'),
        )

        self.add_menu('manual', 'buttons', ).add_items(
            'manual,-',
        )

        self.add_menu('size', 'buttons', ).add_items(
            ('small,size-sm', 'Small'),
            ('small,size-md', 'Medium '),
            ('small,size-lg', 'Large'),
            ('small,size-xl', 'Extra Large'),
            ('small,size-lg2', 'Large - 2 Columns'),
        )


class ModalRegular(ModelFormModal):
    model = Person
    form_fields = ['title', 'first_name', ('surname', {'form_show_labels': False}), 'company']
    widgets = {'title': Select2, 'company': Select2}
    helper_class = RegularHelper


class ModalRegular2C(ModelFormModal):
    model = Person
    form_fields = ['title', 'first_name', 'surname', 'company']
    widgets = {'title': Select2, 'company': Select2}
    helper_class = TwoColumnRegularHelper


class NormaFormModal(ModelFormModal):
    model = Person
    form_fields = [
        ('title', {'wrapper_class': 'col-sm-2', 'widget': Select2}),
        ('first_name', {'wrapper_class': 'col-sm-5'}),
        ('surname', {'wrapper_class': 'col-sm-5'}),
        'company'
    ]
    helper_class = TwoColumnRegularHelper


class NoLabelsModal(ModelFormModal):
    model = Person
    form_fields = ['title', 'first_name', 'surname', 'company']
    widgets = {'title': Select2, 'company': Select2}
    helper_class = NoLabelsRegularHelper


# *********************************
# Horizontal Forms
# *********************************


class Layout1Form(ModelCrispyForm):

    field_extra = CharField(max_length=20)

    class Meta:
        model = Person
        fields = ['first_name', 'surname', 'title', 'company']
        widgets = {'title': Select2}

    def post_init(self, *args, **kwargs):
        return FieldEx('title', 'first_name', 'surname', 'company', 'field_extra'),


class ModalHorizontal(ModelFormModal):
    form_class = Layout1Form
    model = Person
    modal_title = ['New Person', 'Edit Person']


class HorizontalPlaceholderHelper(HorizontalHelper):
    auto_placeholder = True


class HorizontalPlaceholder(ModelFormModal):
    model = Person
    form_fields = [('title', {'widget': Select2}), 'first_name', 'surname',
                   ('company', {'widget': Select2, 'placeholder': 'Enter Company'}),
                   ]
    helper_class = HorizontalPlaceholderHelper


class ModalNoteField(ModelFormModal):
    model = Note
    form_fields = [
        'company',
        'date',
        ('notes', dict(label_class='col-3 col-form-label-sm', field_class='col-12 input-group-sm', rows=20))
    ]
    helper_class = HorizontalHelper


# *********************************
# Manual setup
# *********************************


class SmallPlacementHelper(SmallHelper):
    auto_placeholder = True


class ManualFieldsModal(ModelFormModal):
    model = Person
    form_fields = [('title', {'widget': Select2}), 'first_name', 'surname', 'company']

    helper_class = SmallPlacementHelper

    @staticmethod
    def form_setup(_form, *_args, **_kwargs):
        return [
            MultiFieldRow('Name', FieldEx('title', style='width:100px'), FieldEx('first_name', style='width:200px'),
                          'surname'),
            FieldEx('company')
        ]


# *********************************
# Sizes
# *********************************


class ModalSizes(ModelFormModal):
    model = Person
    modal_title = ['New Person', 'Edit Person']
    form_fields = ['title', 'company', 'first_name', 'surname']
    widgets = {'title': Select2, 'company': Select2}
    helper_class = HorizontalHelper

    def get_context_data(self, **kwargs):
        if self.slug['size'] == 'lg':
            self.size = 'lg'
        elif self.slug['size'] == 'sm':
            self.size = 'sm'
            self.helper_class = SmallHelper
        elif self.slug['size'] == 'md':
            self.size = 'md'
            self.helper_class = SmallHelper
        elif self.slug['size'] == 'xl':
            self.size = 'xl'
        elif self.slug['size'] == 'lg2':
            self.size = 'lg'
            self.helper_class = TwoColumnHelper
        return super().get_context_data()


class ModalNoButtons(ModelFormModal):
    form_class = Layout1Form

    # Can be set via kwargs or in Meta of form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['no_buttons'] = True
        return kwargs
