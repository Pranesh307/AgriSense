from django.contrib.auth import views
from django.urls import path

from farm import  views

urlpatterns = [
    path('dashboard/',views.dashboard_view,name='dashboard'),
    #crops
    path('list_crops/',views.crop_list_view,name='my_crops'),
    path('add_crops/',views.crop_create_view, name='crop_create'),
    path('edit_crops/<int:pk>',views.crop_update_view, name='crop_update'),
    path('delete_crops/<int:pk>',views.crop_delete_view, name='crop_delete'),
    path('detail_crops/<int:pk>',views.crop_detail_view, name='crop_detail'),
    #expenses
    path('crops_expenses/<int:crop_pk>',views.expense_create_view, name='expense_create'),
    path('crops_sales/<int:crop_pk>',views.sale_create_view, name='sale_create'),
path('profile/',views.profile,name='profile'),
]