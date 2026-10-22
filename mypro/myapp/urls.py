from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.courses, name='courses'),
    path('registration/', views.registration, name='registration'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('staff-login/', views.staff_login, name='staff_login'),
    path('staff-logout/', views.staff_logout, name='staff_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-course-add/', views.course_add, name='admin_course_add'),
    path('course/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('course/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('batch/add/', views.batch_add, name='batch_add'),
    path('batch/<int:batch_id>/edit/', views.batch_edit, name='batch_edit'),
    path('batch/<int:batch_id>/delete/', views.batch_delete, name='batch_delete'),
    path('batch/<int:batch_id>/toggle-registration/', views.batch_registration_toggle, name='batch_registration_toggle'),
    path('course-note/add/', views.course_note_add, name='course_note_add'),
    path('course-note/<int:note_id>/edit/', views.course_note_edit, name='course_note_edit'),
    path('course-note/<int:note_id>/delete/', views.course_note_delete, name='course_note_delete'),
    path('announcement/add/', views.announcement_add, name='announcement_add'),
    path('announcement/<int:notice_id>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcement/<int:notice_id>/delete/', views.announcement_delete, name='announcement_delete'),
]
