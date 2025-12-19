"""
URL configuration for tenders app
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, admin_views

app_name = 'tenders'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tenders/', views.tender_list, name='tender_list'),
    path('tenders/add/', views.tender_create, name='tender_create'),
    path('tenders/<int:pk>/', views.tender_detail, name='tender_detail'),
    path('tenders/<int:pk>/edit/', views.tender_edit, name='tender_edit'),
    path('tenders/<int:pk>/delete/', views.tender_delete, name='tender_delete'),
    
    # Contract URLs
    path('tenders/<int:tender_pk>/contract/add/', views.contract_create, name='contract_create'),
    path('tenders/<int:tender_pk>/contract/edit/', views.contract_edit, name='contract_edit'),
    path('tenders/<int:tender_pk>/contract/delete/', views.contract_delete, name='contract_delete'),
    
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='tenders/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='tenders:landing'), name='logout'),
    
    # Admin Panel URLs
    path('custom-admin/', admin_views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('custom-admin/bulk-upload/region/', admin_views.bulk_upload_region, name='bulk_upload_region'),
    path('custom-admin/bulk-upload/department/', admin_views.bulk_upload_department, name='bulk_upload_department'),
    path('custom-admin/bulk-upload/division/', admin_views.bulk_upload_division, name='bulk_upload_division'),
    path('custom-admin/bulk-upload/section/', admin_views.bulk_upload_section, name='bulk_upload_section'),
    path('custom-admin/bulk-upload/procurement-type/', admin_views.bulk_upload_procurement_type, name='bulk_upload_procurement_type'),
    path('custom-admin/bulk-upload/loa-status/', admin_views.bulk_upload_loa_status, name='bulk_upload_loa_status'),
    path('custom-admin/bulk-upload/contract-status/', admin_views.bulk_upload_contract_status, name='bulk_upload_contract_status'),
    path('custom-admin/bulk-upload/employee/', admin_views.bulk_upload_employee, name='bulk_upload_employee'),
    
    # User-Employee Management
    path('custom-admin/user-employee-links/', admin_views.manage_user_employee_links, name='manage_user_employee_links'),
    path('custom-admin/user-employee-links/<int:user_id>/link/', admin_views.link_user_to_employee, name='link_user_to_employee'),
]
