from django.urls import path, include
from django.views.generic.base import RedirectView

import modal_examples.views.file_upload as file_upload
import modal_examples.views.basic as basic
import modal_examples.views.model as model_modals
import modal_examples.views.users as users
import modal_examples.views.permissions as permissions
import modal_examples.views.widgets as widgets
import modal_examples.views.layout as layout
import modal_examples.views.adaptive as adaptive
import modal_examples.views.multi_form as multi_form
import modal_examples.views.crud as crud
import modal_examples.views.unbound_forms as unbound_forms
import modal_examples.views.no_modal as no_modal
import modal_examples.views.ajax as ajax


urlpatterns = [
    path('modal-redirect/', RedirectView.as_view(pattern_name='basic'), name='django-nested-modals'),
    path('modal/classes/', include('modal_examples.views.basic')),
    path('modal/classes/models/', include('modal_examples.views.model')),

    path('modal/upload/', file_upload.UploadModal.as_view(), name='upload_modal'),

    path('modal/unbound1/', unbound_forms.UnboundModal.as_view(), name='unbound_modal'),
    path('modal/unbound2/', unbound_forms.UnboundPaymentModal.as_view(), name='unbound_payment'),
    path('modal/unbound3/', unbound_forms.UnboundLayoutModal.as_view(), name='unbound_layout'),
    path('modal/unbound4/', unbound_forms.UnboundPaymentModal.as_view(), name='unbound_field_view'),

    path('modal/crud_source_code/<str:slug>/', crud.SourceCodeModal.as_view(), name='crud_source_code'),

    path('modal/crud1/<str:slug>/', crud.CrudRead.as_view(), name='crud_read'),
    path('modal/crud2/<str:slug>/', crud.CrudEdit.as_view(), name='crud_edit'),
    path('modal/crud3/<str:slug>/', crud.CrudEditDelete.as_view(), name='crud_edit_delete'),

    path('modal/adaptive/', adaptive.AdaptiveModal.as_view(), name='adaptive_modal'),
    path('modal/adaptive1/', adaptive.AdaptiveBooleanModal.as_view(), name='adaptive_modal_boolean'),
    path('modal/adaptive2/', adaptive.AdaptiveSelectModal.as_view(), name='adaptive_modal_select'),

    path('modal/layout/<str:slug>/', layout.ModalHorizontal.as_view(), name='horizontal'),
    path('modal/layout1/<str:slug>/', layout.ModalSizes.as_view(), name='small'),
    path('modal/layout2/<str:slug>/', layout.NormaFormModal.as_view(), name='layout2'),
    path('modal/layout3/<str:slug>/', layout.HorizontalPlaceholder.as_view(), name='horizontal_placeholder'),
    path('modal/layout4/<str:slug>/', layout.ModalRegular.as_view(), name='regular'),
    path('modal/layout5/<str:slug>/', layout.ModalRegular2C.as_view(), name='regular_2c'),
    path('modal/layout6/<str:slug>/', layout.ModalNoteField.as_view(), name='notefield'),
    path('modal/layout7/<str:slug>/', layout.NoLabelsModal.as_view(), name='nolabels'),
    path('modal/layout8/<str:slug>/', layout.ManualFieldsModal.as_view(), name='manual'),
    path('modal/layout9/<str:slug>/', layout.ModalNoButtons.as_view(), name='no_buttons'),

    path('modal/widgets/<str:slug>/', widgets.ModalCompanyForm.as_view(), name='widgets_company'),
    path('modal/widgets1/<str:slug>/', widgets.TagsCompanyForm.as_view(), name='tags_company'),
    path('modal/widgets2/<str:slug>/', widgets.TagsCompanyFormAddValues.as_view(), name='tags_company_add'),
    path('modal/widgets3/<str:slug>/', widgets.ModalCompanyFormAdd.as_view(), name='company_tags_add'),
    path('modal/widgets4/<str:slug>/', widgets.AjaxTagsCompanyForm.as_view(), name='ajax_widgets_company'),
    path('modal/widgets5/<str:slug>/', widgets.ToggleForm.as_view(), name='toggle_company'),
    path('modal/widgets6/<str:slug>/', widgets.NoteForm.as_view(), name='company_note'),
    path('modal/widgets7/<str:slug>/', widgets.DatatableWidgetExample.as_view(), name='datatable_ex'),
    path('modal/widgets8/<str:slug>/', widgets.DatatableReorderWidgetExample.as_view(), name='datatable_reorder'),
    path('modal/widgets9/<str:slug>/', widgets.DatatableWidgetReverseExample.as_view(), name='datatable_rev'),
    path('modal/widgets10/<str:slug>/', widgets.AjaxPersonCompanyForm.as_view(), name='people_ajax'),
    path('modal/widgets11/<str:slug>/', widgets.Select2PersonCompanyForm.as_view(), name='people_select2'),

    path('modal/perms/<str:slug>/', permissions.DefaultCompany.as_view(), name='perms_default'),
    path('modal/perms1/<str:slug>/', permissions.DeleteCompany.as_view(), name='perms_delete'),
    path('modal/perms2/<str:slug>/', permissions.CompanyPermissions.as_view(), name='perms_on'),
    path('modal/perms_user/<str:slug>/', permissions.PermUser.as_view(), name='perms_user'),
    path('modal/perms_auth/<str:slug>/', permissions.AuthenticatedStaffPermissions.as_view(), name='perms_auth'),
    path('modal/perms_method/<str:slug>/', permissions.MethodPermissions.as_view(), name='perms_method'),

    path('modal/user/<str:slug>/', users.ModalUser.as_view(), name='user_modal'),
    path('modal/user_source_code/<str:slug>/', users.SourceCodeModal.as_view(), name='user_source_code'),
    path('modal/group/<str:slug>/', users.ModalGroup.as_view(), name='group_modal'),

    path('modal/company/<str:slug>/', model_modals.ModalCompanyForm.as_view(), name='company_modal'),
    path('modal/company1/<slug:slug>/', model_modals.ModalCompanyFormExtraField.as_view(), name='extra_field_modal'),
    path('modal/company2/<slug:slug>/', model_modals.ModalCompanyFormPeople.as_view(), name='company_people_modal'),
    path('modal/company3/<slug:slug>/', model_modals.ModalCompanySeparateForm.as_view(), name='separate_form_modal'),

    path('modal/person1/<slug:slug>/', model_modals.ModalPersonNoCompanyForm.as_view(), name='person_nocompany_modal'),

    path('modal/multiform/<slug:slug>/', multi_form.ModalCompanyPerson.as_view(), name='multi_form_modal'),

    path('modal/person/<slug:slug>/', model_modals.ModalPersonForm.as_view(), name='person_modal'),
    path('modal/person-filter/<slug:slug>/', model_modals.ModalPersonFilter.as_view(), name='person_filter'),

    path('modal/hello/', basic.HelloModal.as_view(), name='hello_modal'),
    path('modal/hello_title/', basic.HelloTitleModal.as_view(), name='hello_title_modal'),

    path('modal/template/<slug:slug>/', basic.TemplateModalExample.as_view(), name='template_modal'),
    path('modal/template_ajax/<slug:slug>/', basic.TemplateModalAjax.as_view(), name='template_modal_ajax'),
    path('modal/template_buttons/<slug:slug>/', basic.TemplateModalButtons.as_view(), name='template_modal_buttons'),

    path('modal/forward/<slug:slug>/', basic.ForwardingExample.as_view(), name='forward_example'),
    path('modal/forward1/<slug:slug>/', basic.ForwardingExample1.as_view(), name='forward_example1'),
    path('modal/forward2/<slug:slug>/', basic.ForwardingExample2.as_view(), name='forward_example2'),

    path('multi-form', multi_form.MultiFormExampleView.as_view(), name='multi_form'),
    path('adaptive', adaptive.AdaptiveView.as_view(), name='adaptive'),

    path('Basic', basic.Basic.as_view(), name='basic'),
    path('Model', model_modals.ModelExamples.as_view(), name='model'),
    path('Users', users.UserExamples.as_view(), name='users'),
    path('Permissions', permissions.PermissionExamples.as_view(), name='permissions'),
    path('Widgets', widgets.WidgetExamples.as_view(), name='widgets'),
    path('layout', layout.Layout.as_view(), name='layout'),
    path('crud', crud.CrudExamples.as_view(), name='crud'),
    path('unbound', unbound_forms.UnboundExamples.as_view(), name='unbound'),
    path('Upload', file_upload.Upload.as_view(), name='upload'),
    path('Ajax', ajax.AjaxExamples.as_view(), name='ajax'),

    path('nomodal/<slug:slug>', no_modal.NoModal.as_view(), name='no_modal'),
    path('', RedirectView.as_view(url='Basic')),
]
