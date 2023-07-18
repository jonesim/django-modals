from django.db.models import CharField
from django_modals.widgets.colour_picker import ColourPickerWidget


class ColourField(CharField):

    def formfield(self, **kwargs):
        widget = ColourPickerWidget
        return super().formfield(
            **{
                **({} if self.choices is not None else {"widget": widget}),
                **kwargs,
            }
        )

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super().__init__(*args, **kwargs)
