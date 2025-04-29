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
    path('movies/search/', views.search_movies, name='search_movies'),
    path('movies/<int:movie_id>/delete-review/', views.delete_user_review, name='delete_user_review'),
    
    # Tickets
    path('purchase/<int:showtime_id>/', views.purchase_ticket, name='purchase_ticket'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    
    # Reviews
    path('movies/<int:movie_id>/review/', views.add_review, name='add_review'),
    
    # Admin functions
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/manage-show/', views.manage_show, name='manage_show'),
    path('admin-dashboard/add-show/', views.add_show, name='add_show'),
    path('admin-dashboard/edit-show/<int:showtime_id>/', views.edit_show, name='edit_show'),
    path('admin-dashboard/delete-show/<int:showtime_id>/', views.delete_show, name='delete_show'),
    path('admin-dashboard/manage-movies/', views.manage_movies, name='manage_movies'),
    path('admin-dashboard/add-movie/', views.add_movie, name='add_movie'),
    path('admin-dashboard/edit-movie/<int:movie_id>/', views.edit_movie, name='edit_movie'),
    path('admin-dashboard/delete-movie/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('admin-dashboard/manage-theaters/', views.manage_theaters, name='manage_theaters'),
    path('admin-dashboard/add-theater/', views.add_theater, name='add_theater'),
    path('admin-dashboard/edit-theater/<int:theater_id>/', views.edit_theater, name='edit_theater'),
    path('admin-dashboard/delete-theater/<int:theater_id>/', views.delete_theater, name='delete_theater'),
    path('admin-dashboard/manage-users/', views.manage_users, name='manage_users'),
    path('admin-dashboard/view-user/<int:user_id>/', views.view_user, name='view_user'),
    path('admin-dashboard/edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('admin-dashboard/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin-dashboard/manage-reviews/', views.manage_reviews, name='manage_reviews'),
    path('admin-dashboard/add-review-admin/', views.add_review_admin, name='add_review_admin'),
    path('admin-dashboard/edit-review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('admin-dashboard/delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('admin-dashboard/manage-tickets/', views.manage_tickets, name='manage_tickets'),
    path('admin-dashboard/add-ticket-admin/', views.add_ticket_admin, name='add_ticket_admin'),
    path('admin-dashboard/edit-ticket/<int:ticket_id>/', views.edit_ticket, name='edit_ticket'),
    path('admin-dashboard/delete-ticket/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('admin-dashboard/mark-ticket-used/<int:ticket_id>/', views.mark_ticket_used, name='mark_ticket_used'),
]