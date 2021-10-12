PROCESS_CREATE = 0
PROCESS_EDIT = 1
PROCESS_VIEW = 2
PROCESS_DELETE = 3
PROCESS_EDIT_DELETE = 4     # Edit with delete button
PROCESS_VIEW_EDIT = 5       # View with edit button

PERMISSION_DISABLE = 2
PERMISSION_ON = 1
PERMISSION_OFF = 0
PERMISSION_AUTHENTICATED = 3
PERMISSION_STAFF = 4
PERMISSION_METHOD = 5


class ProcessSetup:
    def __init__(self, modal_title, django_permission, class_attribute, fallback):
        self.modal_title = modal_title
        self.django_permission = django_permission
        self.class_attribute = class_attribute
        self.fallback = fallback


process_data = {
    PROCESS_CREATE: ProcessSetup('New', ['add'], 'permission_create', None),
    PROCESS_EDIT: ProcessSetup('Edit', ['change'], 'permission_edit', PROCESS_VIEW),
    PROCESS_VIEW: ProcessSetup('View', ['view'], 'permission_view', None),
    PROCESS_DELETE: ProcessSetup('Delete', ['delete'], 'permission_delete', None),
    PROCESS_EDIT_DELETE: ProcessSetup('Edit', ['delete', 'change'], 'permission_delete', PROCESS_EDIT),
    PROCESS_VIEW_EDIT: ProcessSetup('View', ['change'], 'permission_edit', PROCESS_VIEW),
}


modal_url_type = {
    'view': PROCESS_VIEW,
    'viewedit': PROCESS_VIEW_EDIT,
    'edit': PROCESS_EDIT,
    'editdelete': PROCESS_EDIT_DELETE,
    'delete': PROCESS_DELETE,
}
