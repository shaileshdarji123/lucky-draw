from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload-staff/', views.upload_staff, name='upload_staff'),
    path('scan-qr/', views.scan_qr, name='scan_qr'),
    path('process-qrs-scan/', views.process_qr_scan, name='process_qr_scan'),
    path('draw-winner/', views.draw_winner, name='draw_winner'),
    path('view-checkins/', views.view_checkins, name='view_checkins'),
    path('download-day1-excel/', views.download_day1_excel, name='download_day1_excel'),
    path('download-day2-excel/', views.download_day2_excel, name='download_day2_excel'),
    path('view-winners/', views.view_winners, name='view_winners'),
    path('download-qr-codes/', views.download_qr_codes, name='download_qr_codes'),
    path('download-qr-with-label/<int:staff_id>/', views.download_qr_with_label, name='download_qr_with_label'),
    path('preview-qr-svg/<int:staff_id>/', views.preview_qr_svg, name='preview_qr_svg'),
    path('set-event-dates/', views.set_event_dates, name='set_event_dates'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('clear-database/', views.clear_database, name='clear_database'),
    path('download-template-image/<int:day>/', views.download_template_image, name='download_template_image'),
]