from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Movies
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/upcoming/', views.upcoming_movies, name='upcoming_movies'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('search/', views.search_movies, name='search_movies'),
    
    # Tickets
    path('purchase/<int:showtime_id>/', views.purchase_ticket, name='purchase_ticket'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    
    # Reviews
    path('movies/<int:movie_id>/review/', views.add_review, name='add_review'),
    
    # Admin functions
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/manage-shows/', views.manage_shows, name='manage_shows'),
    path('admin-dashboard/add-show/', views.add_show, name='add_show'),
    path('admin-dashboard/edit-show/<int:showtime_id>/', views.edit_show, name='edit_show'),
    path('admin-dashboard/delete-show/<int:showtime_id>/', views.delete_show, name='delete_show'),
]