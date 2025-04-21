from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('place_order/', views.place_order_view, name='place_order'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('history/', views.trade_history_view, name='trade_history'),
]