from django.urls import path
import examples.views as views
import examples.modals as modals

urlpatterns = [

    path('modal/company/<slug:slug>/', modals.ModalCompanyForm.as_view(), name='company_modal'),
    path('modal/company1/<slug:slug>/', modals.ModalCompanyFormExtraField.as_view(), name='extra_field_modal'),
    path('modal/company2/<slug:slug>/', modals.ModalCompanyFormPeople.as_view(), name='company_people_modal'),
    path('modal/company3/<slug:slug>/', modals.ModalCompanySeparateForm.as_view(), name='separate_form_modal'),
    path('modal/multiform/<slug:slug>/', modals.ModalCompanyPerson.as_view(), name='multi_form_modal'),

    path('modal/person/<slug:slug>/', modals.ModalPersonForm.as_view(), name='person_modal'),
    path('modal/person1/<slug:slug>/', modals.ModalPersonNoCompanyForm.as_view(), name='person_nocompany_modal'),
    path('modal/person2/<slug:slug>/', modals.ModalPersonSeparateForm.as_view(), name='separate_person_modal'),

    path('modal/hello/<slug:slug>/', modals.HelloModal.as_view(), name='hello_modal'),
    path('modal/buttons/<slug:slug>/', modals.ModalButtons.as_view(), name='button_modal'),

    path('modal/form/<slug:slug>/', modals.FormModal.as_view(), name='form_modal'),

    path('', views.Example1.as_view()),
    path('<int:pk>', views.CompanyView.as_view(), name='company'),
    path('example-1', views.Example1.as_view(), name='example1'),
    path('example-2/<int:pk>/', views.Example2.as_view(), name='example2'),
    path('example-2/', views.Example2.as_view(), name='example2'),
]
