from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # super admin urls

    path('super-admin/dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('super-admin/users/', views.SuperAdminUserListView.as_view(), name='super_admin_users'),
    path('super-admin/users/add/', views.SuperAdminUserCreateView.as_view(), name='super_admin_add_user'),
    path('super-admin/users/<int:pk>/select-manager/', views.SuperAdminSelectManagerView.as_view(), name='super_admin_select_manager'),
    path('super-admin/users/<int:pk>/', views.SuperAdminUserDetailView.as_view(), name='super_admin_user'),
    path('super-admin/users/<int:pk>/edit/', views.SuperAdminUserUpdateView.as_view(), name='super_admin_edit_user'),
    path('super-admin/users/<int:pk>/delete/', views.SuperAdminUserDeleteView.as_view(), name='super_admin_delete_user'),
    path('super-admin/profiles/', views.SuperAdminProfileListView.as_view(), name='super_admin_profiles'),
    path('super-admin/profiles/<int:pk>/', views.SuperAdminProfileDetailView.as_view(), name='super_admin_profile'),
    path('super-admin/profiles/<int:pk>/edit/', views.SuperAdminProfileUpdateView.as_view(), name='super_admin_edit_profile'),
    path('super-admin/activities/', views.SuperAdminActivityListView.as_view(), name='super_admin_activities'),
    path('super-admin/activities/add/', views.super_admin_create_bulk_activity, name='super_admin_add_activity'),
    path('super-admin/activities/<int:pk>/', views.SuperAdminActivityDetailView.as_view(), name='super_admin_activity'),
    path('super-admin/activities/<int:pk>/edit/', views.SuperAdminActivityUpdateView.as_view(), name='super_admin_edit_activity'),
    path('super-admin/activities/<int:pk>/delete/', views.SuperAdminActivityDeleteView.as_view(), name='super_admin_delete_activity'),

    # manager urls

    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/users/', views.ManagerUserListView.as_view(), name='manager_users'),
    path('manager/users/<int:pk>/', views.ManagerUserDetailView.as_view(), name='manager_user'),
    path('manager/activities/my/', views.ManagerMyActivityListView.as_view(), name='manager_my_activities'),
    path('manager/activities/my/<int:pk>/', views.ManagerMyActivityDetailView.as_view(), name='manager_my_activity'),
    path('manager/activities/my/<int:pk>/is-completed/', views.ManagerMyActivityUpdateView.as_view(), name='manager_edit_my_activity'),
    path('manager/activities/employee/', views.ManagerActivityListView.as_view(), name='manager_activities'),
    path('manager/activities/employee/add/', views.manager_create_bulk_activity, name='manager_add_activity'),
    path('manager/activities/employee/<int:pk>/', views.ManagerActivityDetailView.as_view(), name='manager_activity'),

    # employee urls

    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/profiles/add/', views.EmployeeProfileCreateView.as_view(), name='employee_add_profile'),
    path('employee/profiles/<int:pk>/', views.EmployeeProfileDetailView.as_view(), name='employee_profile'),
    path('employee/profiles/<int:pk>/edit/', views.EmployeeProfileUpdateView.as_view(), name='employee_edit_profile'),
    path('employee/activities/', views.EmployeeActivityListView.as_view(), name='employee_activities'),
    path('employee/activities/<int:pk>/', views.EmployeeActivityDetailView.as_view(), name='employee_activity'),
    path('employee/activities/<int:pk>/is-completed/', views.EmployeeActivityUpdateView.as_view(), name='employee_edit_activity'),
]