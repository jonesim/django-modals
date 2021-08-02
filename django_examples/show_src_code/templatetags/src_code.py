from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.safestring import mark_safe
from django_modals.helper import show_modal as show_modal_helper, make_slug

register = template.Library()


@register.simple_tag(takes_context=True)
def show_src_code(context, modal, *args, button='Source Code', button_classes='btn btn-sm btn-outline-secondary',
                  **kwargs):
    slug = make_slug(*args, make_pk=True)
    slug += '-template-' + context.template.name.replace('/', ':')
    return mark_safe(show_modal_helper(modal, slug, button=button, button_classes=button_classes, **kwargs))


@register.simple_tag
def highlighjs_includes():
    return mark_safe(
        f'<link rel="stylesheet" href={static("show_src_code/highlightjs.css")}>'
        f'<script src="{static("show_src_code/highlightjs.js")}"></script>'
    )


@register.simple_tag
def highlighjs_includes_cdn():
    return mark_safe(
        f'<link rel="stylesheet" href="https://unpkg.com/@highlightjs/cdn-assets@11.0.1/styles/default.min.css">'
        f'<script src="https://unpkg.com/@highlightjs/cdn-assets@11.0.1/highlight.min.js"></script>'
    )
