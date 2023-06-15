from django.contrib import admin

from modal_examples.models import Company, Note


class NoteInline(admin.TabularInline):
    model = Note



@admin.register(Company)
class SavedStateAdmin(admin.ModelAdmin):
    inlines = [NoteInline,
               ]
    list_display = ('name',
                    )