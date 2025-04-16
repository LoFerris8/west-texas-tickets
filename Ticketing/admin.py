from django.contrib import admin
from .models import Theater, Movie, Showtime, Ticket, Review, UserProfile

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'address')
    search_fields = ('name', 'location')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration', 'release_date', 'is_currently_playing')
    list_filter = ('is_currently_playing', 'genre')
    search_fields = ('title', 'description')

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'theater', 'datetime', 'price', 'available_seats')
    list_filter = ('theater', 'datetime')
    search_fields = ('movie__title', 'theater__name')
    date_hierarchy = 'datetime'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'showtime', 'quantity', 'total_price', 'purchase_date', 'is_used')
    list_filter = ('is_used', 'purchase_date')
    search_fields = ('user__username', 'showtime__movie__title')
    readonly_fields = ('barcode',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_date')
    list_filter = ('rating', 'created_date')
    search_fields = ('user__username', 'movie__title', 'comment')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')