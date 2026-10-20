from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # System monitoring
    path('health/', views.health_check, name='health_check'),
    
    # Authentication and profile
    path('', views.index, name='index'),
    path('auth-required/', views.auth_required, name='auth_required'),
    path('verify-email/resend/', views.resend_verification, name='resend_verification'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('register/', views.register, name='register'),
    path('register/social/', views.social_register, name='social_register'),
    path('admin-register/', views.admin_register, name='admin_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/clear-documents/', views.clear_all_documents, name='clear_all_documents'),
    
    # OAuth URLs
    path('auth/<str:provider>/initiate/', views.oauth_initiate, name='oauth_initiate'),
    path('auth/<str:provider>/callback/', views.oauth_callback, name='oauth_callback'),
    path('auth/set-password/', views.oauth_set_password, name='oauth_set_password'),
    path('auth/verify-code/', views.oauth_verify_code, name='oauth_verify_code'),
    path('auth/resend-code/', views.oauth_resend_code, name='oauth_resend_code'),
    
    # Password Reset URLs
    path('password_reset/', views.custom_password_reset, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Notification URLs
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/clear-all/', views.api_clear_all_notifications, name='api_clear_all_notifications'),
    
    # Programs and registrations
    path('programs/', views.program_list, name='program_list'),
    path('programs/<int:program_id>/', views.program_detail, name='program_detail'),
    path('programs/<int:program_id>/register/', views.program_register, name='program_register'),
    path('programs/<int:program_id>/apply/', views.apply_candidate, name='candidate_apply'),
    path('programs/<int:program_id>/registrants/', views.program_registrants, name='program_registrants'),
    path('registrations/<int:registration_id>/', views.registration_detail, name='registration_detail'),
    path('registrations/<int:registration_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('registrations/<int:registration_id>/status/<str:status>/', views.update_registration_status, name='update_registration_status'),
    
    # Export program registrants
    path('programs/<int:program_id>/export/registrants/csv/', views.export_registrants_csv, name='export_registrants_csv'),
    path('programs/<int:program_id>/export/registrants/excel/', views.export_registrants_excel, name='export_registrants_excel'),
    path('programs/<int:program_id>/export/registrants/pdf/', views.export_registrants_pdf, name='export_registrants_pdf'),
    
    # Candidates management
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/add/', views.add_candidate, name='add_candidate'),
    path('candidates/<int:candidate_id>/', views.view_candidate, name='view_candidate'),
    path('candidates/<int:candidate_id>/edit/', views.edit_candidate, name='edit_candidate'),
    path('candidates/<int:candidate_id>/delete/', views.delete_candidate, name='delete_candidate'),
    path('candidates/<int:candidate_id>/cancel/', views.cancel_application, name='cancel_application'),
    path('candidates/<int:candidate_id>/status/<str:status>/', views.update_candidate_status, name='update_candidate_status'),
    path('candidates/<int:candidate_id>/validate/', views.validate_candidate, name='validate_candidate'),
    path('candidates/<int:candidate_id>/send-status-email/', views.send_candidate_status_email, name='send_candidate_status_email'),
    
    # Export candidates
    path('candidates/export/csv/', views.export_candidates_csv, name='export_candidates_csv'),
    path('candidates/export/excel/', views.export_candidates_excel, name='export_candidates_excel'),
    path('candidates/export/pdf/', views.export_candidates_pdf, name='export_candidates_pdf'),
    
    # Export dashboard reports
    path('reports/export/', views.export_dashboard_report, name='export_dashboard_report'),
    
    # Static pages
    path('help/', views.help_page, name='help'),
    path('contact/', views.contact_page, name='contact'),
    
    # AJAX API endpoints
    path('api/check-username/', views.check_username, name='check_username'),
    path('api/ajax-login/', views.ajax_login, name='ajax_login'),
    path('api/ajax-register/', views.ajax_register, name='ajax_register'),
    path('api/user-applications/', views.get_user_applications, name='get_user_applications'),
    path('api/clear-oauth-session/', views.clear_oauth_session, name='clear_oauth_session'),
    
    # Modal views
    path('modal/login/', views.modal_login, name='modal_login'),
    path('modal/register/', views.modal_register, name='modal_register'),
    path('modal/admin-register/', views.modal_admin_register, name='modal_admin_register'),
    path('api/ajax-admin-register/', views.ajax_admin_register, name='ajax_admin_register'),
    
    # Admin Management (Custom Interface - not Django Admin)
    path('manage/users/', views.manage_users, name='manage_users'),
    path('manage/users/add/', views.manage_user_add, name='manage_user_add'),
    path('manage/users/<int:user_id>/edit/', views.manage_user_edit, name='manage_user_edit'),
    path('manage/users/<int:user_id>/delete/', views.manage_user_delete, name='manage_user_delete'),
    
    path('manage/programs/', views.manage_programs, name='manage_programs'),
    path('manage/programs/add/', views.manage_program_add, name='manage_program_add'),
    path('manage/programs/<int:program_id>/edit/', views.manage_program_edit, name='manage_program_edit'),
    path('manage/programs/<int:program_id>/delete/', views.manage_program_delete, name='manage_program_delete'),
    
    path('manage/registrations/', views.manage_registrations, name='manage_registrations'),
    path('manage/activity-logs/', views.manage_activity_logs, name='manage_activity_logs'),
]
