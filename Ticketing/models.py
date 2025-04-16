from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.location}"

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    genre = models.CharField(max_length=100)
    release_date = models.DateField()
    is_currently_playing = models.BooleanField(default=True)
    poster = models.ImageField(upload_to='movie_posters/', blank=True, null=True)
    
    def __str__(self):
        return self.title

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='showtimes')
    datetime = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available_seats = models.IntegerField(default=100)
    
    def __str__(self):
        return f"{self.movie.title} at {self.theater.name} - {self.datetime}"
    
    class Meta:
        ordering = ['datetime']

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='tickets')
    quantity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    purchase_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    barcode = models.CharField(max_length=50, unique=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.user.username} - {self.showtime.movie.title}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.movie.title}"
    
    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_date']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"