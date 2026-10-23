from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('resume/create/', views.resume_quick_create, name='resume_quick_create'),
    path('resume/<int:resume_id>/edit/', views.resume_edit, name='resume_edit'),
    path('resume/<int:resume_id>/save/', views.resume_save, name='resume_save'),
    path('resume/<int:resume_id>/delete/', views.resume_delete, name='resume_delete'),
    path('resume/<int:resume_id>/duplicate/', views.resume_duplicate, name='resume_duplicate'),
    path('resume/<int:resume_id>/preview-html/', views.resume_preview_ajax, name='resume_preview_ajax'),
    path('resume/<int:resume_id>/pdf/', views.resume_pdf, name='resume_pdf'),
    path('resume/<int:resume_id>/load-sample/', views.load_sample_data, name='load_sample_data'),
    path('resume/<int:resume_id>/ats-scan/', views.resume_ats_scan, name='resume_ats_scan'),
    path('resume/<int:resume_id>/export-json/', views.resume_export_json, name='resume_export_json'),
    path('resume/<int:resume_id>/import-json/', views.resume_import_json, name='resume_import_json'),
]
