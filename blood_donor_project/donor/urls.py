from django.urls import path
from . import views

urlpatterns = [

    path('',views.home,name='home'),

    path('register/',views.register_donor,name='register'),

    path('donors/',views.donor_list,name='donors'),

    path('search/',views.search_donor,name='search'),

    path('request-blood/',views.blood_request,name='request_blood'),

    path('edit/<int:id>/', views.edit_donor, name='edit_donor'),

    path('delete/<int:id>/', views.delete_donor, name='delete_donor'),
    
    path('dashboard/', views.dashboard, name='dashboard'),

    path('export-pdf/', views.export_pdf, name='export_pdf'),

    path('export-excel/', views.export_excel, name='export_excel'),

    path('login/', views.login_user, name='login'),
path('logout/', views.logout_user, name='logout'),
path('about/', views.about, name='about'),
path('contact/', views.contact, name='contact'),

]