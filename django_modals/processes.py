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


def user_has_perm(cls, user, process):
    permission_type = getattr(cls, process_data[process].class_attribute)
    if permission_type == PERMISSION_METHOD:
        permission = getattr(cls, 'permission')(user, process)
    elif permission_type == PERMISSION_OFF:
        permission = True
    elif permission_type == PERMISSION_DISABLE:
        permission = False
    elif permission_type == PERMISSION_AUTHENTICATED:
        permission = user.is_authenticated
    elif permission_type == PERMISSION_STAFF:
        permission = user.is_staff or user.is_superuser
    else:
        # noinspection PyProtectedMember
        perms = [f'{cls.model._meta.app_label}.{p}_{cls.model._meta.model_name}'
                 for p in process_data[process].django_permission]
        permission = user.has_perms(perms)
    return permission


def get_process(cls, user, process):
    while True:
        permission = user_has_perm(cls, user, process)
        if permission:
            break
        process = process_data[process].fallback
        if not process:
            break
    return permission, process
