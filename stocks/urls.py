from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_view, name='stock_view'),
    path('chart/', views.chart_view, name='chart'),
    path('get_stock_data/', views.get_stock_data, name='get_stock_data'),
]
