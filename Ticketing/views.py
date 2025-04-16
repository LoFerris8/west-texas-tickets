from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
import uuid
from .forms import CustomUserCreationForm 

from .models import Movie, Theater, Showtime, Ticket, Review, UserProfile
from .forms import UserProfileForm, ReviewForm, TicketPurchaseForm, ShowtimeForm

def home(request):
    current_movies = Movie.objects.filter(is_currently_playing=True)[:6]
    upcoming_movies = Movie.objects.filter(is_currently_playing=False, 
                                          release_date__gt=timezone.now().date())[:6]
    theaters = Theater.objects.all()
    
    return render(request, 'home.html', {
        'current_movies': current_movies,
        'upcoming_movies': upcoming_movies,
        'theaters': theaters,
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    recent_tickets = request.user.tickets.order_by('-purchase_date')[:5]
    
    return render(request, 'auth/profile.html', {
        'form': form,
        'recent_tickets': recent_tickets
    })

def movie_list(request):
    movies = Movie.objects.filter(is_currently_playing=True)
    return render(request, 'movies/movie_list.html', {'movies': movies, 'title': 'Now Playing'})

def upcoming_movies(request):
    movies = Movie.objects.filter(is_currently_playing=False, 
                                  release_date__gt=timezone.now().date())
    return render(request, 'movies/movie_list.html', {'movies': movies, 'title': 'Upcoming Movies'})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    showtimes = movie.showtimes.filter(datetime__gt=timezone.now()).order_by('datetime')
    theaters = Theater.objects.all()
    reviews = movie.reviews.all()[:5]  # Get 5 most recent reviews
    
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'showtimes': showtimes,
        'theaters': theaters,
        'reviews': reviews,
        'avg_rating': avg_rating
    })

def search_movies(request):
    query = request.GET.get('q', '')
    if query:
        movies = Movie.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(genre__icontains=query)
        )
    else:
        movies = Movie.objects.none()
    
    return render(request, 'movies/search_results.html', {
        'movies': movies,
        'query': query
    })

@login_required
def purchase_ticket(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    
    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            if quantity > 10:
                messages.error(request, 'Maximum 10 tickets per purchase.')
                return redirect('purchase_ticket', showtime_id=showtime_id)
            
            if showtime.available_seats < quantity:
                messages.error(request, 'Not enough seats available.')
                return redirect('purchase_ticket', showtime_id=showtime_id)
            
            # Create ticket
            total_price = showtime.price * quantity
            barcode = str(uuid.uuid4())
            
            ticket = Ticket.objects.create(
                user=request.user,
                showtime=showtime,
                quantity=quantity,
                total_price=total_price,
                barcode=barcode
            )
            
            # Update available seats
            showtime.available_seats -= quantity
            showtime.save()
            
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketPurchaseForm()
    
    return render(request, 'tickets/purchase.html', {
        'showtime': showtime,
        'form': form
    })

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def my_tickets(request):
    tickets = request.user.tickets.order_by('-purchase_date')
    return render(request, 'tickets/my_tickets.html', {'tickets': tickets})

@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Check if user already reviewed this movie
    existing_review = Review.objects.filter(user=request.user, movie=movie).first()
    
    if request.method == 'POST':
        if existing_review:
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            form = ReviewForm(request.POST)
            
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('movie_detail', movie_id=movie_id)
    else:
        if existing_review:
            form = ReviewForm(instance=existing_review)
        else:
            form = ReviewForm()
    
    return render(request, 'movies/add_review.html', {
        'form': form,
        'movie': movie,
        'editing': existing_review is not None
    })

# Admin views (require staff status)
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    total_tickets = Ticket.objects.count()
    total_revenue = Ticket.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    movies_playing = Movie.objects.filter(is_currently_playing=True).count()
    recent_tickets = Ticket.objects.order_by('-purchase_date')[:10]
    
    return render(request, 'admin/dashboard.html', {
        'total_tickets': total_tickets,
        'total_revenue': total_revenue,
        'movies_playing': movies_playing,
        'recent_tickets': recent_tickets
    })

@user_passes_test(lambda u: u.is_staff)
def manage_shows(request):
    showtimes = Showtime.objects.all().order_by('datetime')
    return render(request, 'admin/manage_shows.html', {'showtimes': showtimes})

@user_passes_test(lambda u: u.is_staff)
def add_show(request):
    if request.method == 'POST':
        form = ShowtimeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Show added successfully!')
            return redirect('manage_shows')
    else:
        form = ShowtimeForm()
    
    return render(request, 'admin/show_form.html', {'form': form, 'title': 'Add Show'})

@user_passes_test(lambda u: u.is_staff)
def edit_show(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    
    if request.method == 'POST':
        form = ShowtimeForm(request.POST, instance=showtime)
        if form.is_valid():
            form.save()
            messages.success(request, 'Show updated successfully!')
            return redirect('manage_shows')
    else:
        form = ShowtimeForm(instance=showtime)
    
    return render(request, 'admin/show_form.html', {'form': form, 'title': 'Edit Show'})

@user_passes_test(lambda u: u.is_staff)
def delete_show(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    showtime.delete()
    messages.success(request, 'Show deleted successfully!')
    return redirect('manage_shows')