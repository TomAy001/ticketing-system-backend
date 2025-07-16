from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<str:ticket_id>/update-status/', views.update_ticket_status, name='update_ticket_status'),
    path('tickets/<str:ticket_id>/assign/', views.assign_ticket, name='assign_ticket'),
    path('ticket/<str:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('get-student-info/', views.get_student_info, name='get_student_info'),
]

handler400 = 'tickets.views.custom_bad_request'
handler403 = 'tickets.views.custom_permission_denied'
handler404 = 'tickets.views.custom_page_not_found'
handler500 = 'tickets.views.custom_server_error'
