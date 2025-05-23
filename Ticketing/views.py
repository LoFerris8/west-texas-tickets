from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.urls import reverse_lazy
import uuid
from .forms import CustomUserCreationForm, MovieForm, TheaterForm, UserProfileAdminForm, ReviewAdminForm, TicketAdminForm, CustomAuthenticationForm
from .utils import encrypt_payment_data
from .models import Movie, Theater, Showtime, Ticket, Review, UserProfile, User, Payment
from .forms import UserProfileForm, ReviewForm, TicketPurchaseForm, ShowtimeForm

import logging

logger = logging.getLogger(__name__)

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

    next_url = request.GET.get('next')

    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                logger.info(f"User {user.username} signed up and logged in successfully")
                return redirect('home')
            except Exception as e:
                logger.error(f"Error during signup: {e}")
                form.add_error(None, f"Error during signup: {str(e)}")
        else:
            logger.error(f"Form validation failed: {form.errors}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})

def logout_view(request):
    """
    Handle user logout and redirect to the login page.
    """
    logger.info(f"Logging out user: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    logout(request)
    logger.info("User logged out successfully")
    return redirect('login')  # Redirect to the login page (ensure 'login' URL name exists)
"""
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
"""
@login_required
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            # Update the User fields except for username/email
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            # No longer update the username/email
            # user.username = form.cleaned_data['username'] - remove this line
            user.save()

            # Update the UserProfile fields
            form.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=user)

    recent_tickets = user.tickets.order_by('-purchase_date')[:5]

    return render(request, 'auth/profile.html', {
        'form': form,
        'recent_tickets': recent_tickets
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important: update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('profile')

def movie_list(request):
    theater_id = request.GET.get('theater')
    genre_filter = request.GET.get('genre')

    movies = Movie.objects.filter(is_currently_playing=True)

    selected_theater = None

    if theater_id:
        movies = movies.filter(showtimes__theater_id=theater_id)
        try:
            selected_theater = Theater.objects.get(id=theater_id)
        except Theater.DoesNotExist:
            selected_theater = None

    if genre_filter:
        movies = movies.filter(genre=genre_filter)

    movies = movies.distinct()  # Movies can have multiple showtimes and thus appear more than once - we use distinct() to remove dups.

    theaters = Theater.objects.all()
    genres = Movie.objects.values_list('genre', flat=True).distinct()

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'selected_theater': selected_theater,
        'genres': genres,
        'title': 'Now Playing'
    })

def upcoming_movies(request):
    movies = Movie.objects.filter(is_currently_playing=False, 
                                  release_date__gt=timezone.now().date())
    
    theater_id = request.GET.get('theater')
    genre_filter = request.GET.get('genre')

    if theater_id:
        movies = movies.filter(showtimes__theater_id=theater_id)

    if genre_filter:
        movies = movies.filter(genre=genre_filter)

    movies = movies.distinct()

    theaters = Theater.objects.all()
    genres = Movie.objects.values_list('genre', flat=True).distinct()

    return render(request, 'movies/movie_list.html', {
    'movies': movies,
    'theaters': theaters,
    'genres': genres,
    'title': 'Upcoming Movies'
    })


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theater_id = request.GET.get('theater')
    showtimes = movie.showtimes.filter(datetime__gt=timezone.now()).order_by('datetime')
    dates = sorted(set(showtime.datetime.date() for showtime in showtimes))
    times = sorted(set(showtime.datetime.time() for showtime in showtimes))
    
    if theater_id:
        showtimes = showtimes.filter(theater_id = theater_id)
        try:
            selected_theater = Theater.objects.get(id=theater_id)
        except Theater.DoesNotExist:
            selected_theater = None
    else:
        selected_theater = None

    reviews = movie.reviews.all()[:5]  # Get 5 most recent reviews
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'showtimes': showtimes,
        'selected_theater': selected_theater,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'dates': dates,
        'times': times,
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
        'results': movies,
        'query': query
    })

@login_required
def purchase_ticket(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    
    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST)
        
        # Store the selected payment method for re-rendering if validation fails
        selected_payment_method = request.POST.get('payment_method')
        
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            payment_method = form.cleaned_data['payment_method']
            
            if quantity > 10:
                messages.error(request, 'Maximum 10 tickets per purchase.')
                return redirect('purchase_ticket', showtime_id=showtime_id)
            
            if showtime.available_seats < quantity:
                messages.error(request, 'Not enough seats available.')
                return redirect('purchase_ticket', showtime_id=showtime_id)
            
            # Process payment details based on payment method
            payment_data = {
                'method': payment_method
            }
            
            if payment_method == 'credit_card':
                card_number = form.cleaned_data['card_number']
                expiration_date = form.cleaned_data['expiration_date']
                cvv = form.cleaned_data['cvv']
                
                # Validate credit card details
                if not card_number or len(card_number.strip()) != 16:
                    messages.error(request, 'Please enter a valid card number.')
                    # Preserve payment method when re-rendering form
                    form.data = form.data.copy()
                    form.data['payment_method'] = payment_method
                    return render(request, 'tickets/purchase.html', {'showtime': showtime, 'form': form})
                
                if not expiration_date or len(expiration_date.strip()) < 4:
                    messages.error(request, 'Please enter a valid expiration date.')
                    form.data = form.data.copy()
                    form.data['payment_method'] = payment_method
                    return render(request, 'tickets/purchase.html', {'showtime': showtime, 'form': form})
                
                if not cvv or len(cvv.strip()) < 3:
                    messages.error(request, 'Please enter a valid CVV.')
                    form.data = form.data.copy()
                    form.data['payment_method'] = payment_method
                    return render(request, 'tickets/purchase.html', {'showtime': showtime, 'form': form})
                
                # Add credit card details to payment data
                payment_data.update({
                    'card_number': card_number,
                    'expiration_date': expiration_date,
                    'cvv': cvv
                })
                
            elif payment_method == 'venmo':
                venmo_username = form.cleaned_data['venmo_username']
                
                # Validate Venmo username
                if not venmo_username or len(venmo_username.strip()) < 3 or not venmo_username.strip().startswith('@'):
                    messages.error(request, 'Please enter a valid Venmo username.')
                    # Preserve payment method when re-rendering form
                    form.data = form.data.copy()
                    form.data['payment_method'] = payment_method
                    return render(request, 'tickets/purchase.html', {'showtime': showtime, 'form': form})
                
                # Add Venmo details to payment data
                payment_data.update({
                    'venmo_username': venmo_username
                })
                
            elif payment_method == 'paypal':
                paypal_email = form.cleaned_data['paypal_email']
                
                # Validate PayPal email
                if not paypal_email or '@' not in paypal_email:
                    messages.error(request, 'Please enter a valid PayPal email.')
                    form.data = form.data.copy()
                    form.data['payment_method'] = payment_method
                    return render(request, 'tickets/purchase.html', {'showtime': showtime, 'form': form})
                
                # Add PayPal details to payment data
                payment_data.update({
                    'paypal_email': paypal_email
                })
            
            # Encrypt payment data
            encrypted_payment_details = encrypt_payment_data(payment_data)
            
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
            
            # Save payment information using the Payment model
            Payment.objects.create(
                ticket=ticket,
                payment_method=payment_method,
                encrypted_payment_details=encrypted_payment_details
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
    if request.user.is_staff:
        # Admins can view any ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)
    else:
        # Regular users can only view their own tickets
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def my_tickets(request):
    tickets = request.user.tickets.order_by('-purchase_date')
    return render(request, 'tickets/my_tickets.html', {'tickets': tickets})

@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if not movie.is_currently_playing:
        messages.error(request, "You can only review movies that are currently playing.")
        return redirect('movie_detail', movie_id=movie_id)
    
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

# Admin views
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
def manage_show(request):
    # Get filter parameters
    search = request.GET.get('search', '')
    status = request.GET.get('status', 'all')
    
    # Base queryset
    showtimes = Showtime.objects.all()
    
    # Apply search filter if provided
    if search:
        showtimes = showtimes.filter(
            Q(movie__title__icontains=search) |
            Q(theater__name__icontains=search) |
            Q(theater__location__icontains=search)
        )
    
    # Apply status filter if provided
    now = timezone.now()
    if status == 'upcoming':
        showtimes = showtimes.filter(datetime__gt=now)
    elif status == 'past':
        showtimes = showtimes.filter(datetime__lte=now)
    
    # Order by datetime
    showtimes = showtimes.order_by('datetime')
    
    # Add current datetime to context
    return render(request, 'admin/manage_shows.html', {
        'showtimes': showtimes,
        'now': now,
    })

@user_passes_test(lambda u: u.is_staff)
def add_show(request):
    if request.method == 'POST':
        form = ShowtimeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Show added successfully!')
            return redirect('manage_show')
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
            return redirect('manage_show')
    else:
        form = ShowtimeForm(instance=showtime)
    
    return render(request, 'admin/show_form.html', {'form': form, 'title': 'Edit Show'})

@user_passes_test(lambda u: u.is_staff)
def delete_show(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    showtime.delete()
    messages.success(request, 'Show deleted successfully!')
    return redirect('manage_show')

@user_passes_test(lambda u: u.is_staff)
def manage_movies(request):
    """View to list and manage movies"""
    movies = Movie.objects.all().order_by('-release_date')
    return render(request, 'admin/manage_movies.html', {'movies': movies})

@user_passes_test(lambda u: u.is_staff)
def add_movie(request):
    """View to add a new movie"""
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Movie added successfully!')
            return redirect('manage_movies')
    else:
        form = MovieForm()
    
    return render(request, 'admin/movie_form.html', {
        'form': form,
        'title': 'Add Movie'
    })

@user_passes_test(lambda u: u.is_staff)
def edit_movie(request, movie_id):
    """View to edit an existing movie"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Movie updated successfully!')
            return redirect('manage_movies')
    else:
        form = MovieForm(instance=movie)
    
    return render(request, 'admin/movie_form.html', {
        'form': form,
        'title': 'Edit Movie'
    })

@user_passes_test(lambda u: u.is_staff)
def delete_movie(request, movie_id):
    """View to delete a movie with improved error handling"""
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        movie_title = movie.title  # Save the title before deletion
        movie.delete()
        messages.success(request, f'Movie "{movie_title}" deleted successfully!')
    except Movie.DoesNotExist:
        messages.error(request, f'Unable to delete movie with ID {movie_id}. It may have already been deleted.')
    except Exception as e:
        messages.error(request, f'Error deleting movie: {str(e)}')
    
    return redirect('manage_movies')
@user_passes_test(lambda u: u.is_staff)
def manage_theaters(request):
    """View to list and manage theaters"""
    theaters = Theater.objects.all().order_by('location')
    return render(request, 'admin/manage_theaters.html', {'theaters': theaters})

@user_passes_test(lambda u: u.is_staff)
def add_theater(request):
    """View to add a new theater"""
    if request.method == 'POST':
        form = TheaterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Theater added successfully!')
            return redirect('manage_theaters')
    else:
        form = TheaterForm()
    
    return render(request, 'admin/theater_form.html', {
        'form': form,
        'title': 'Add Theater'
    })

@user_passes_test(lambda u: u.is_staff)
def edit_theater(request, theater_id):
    """View to edit an existing theater"""
    theater = get_object_or_404(Theater, id=theater_id)
    
    if request.method == 'POST':
        form = TheaterForm(request.POST, instance=theater)
        if form.is_valid():
            form.save()
            messages.success(request, 'Theater updated successfully!')
            return redirect('manage_theaters')
    else:
        form = TheaterForm(instance=theater)
    
    return render(request, 'admin/theater_form.html', {
        'form': form,
        'title': 'Edit Theater'
    })

@user_passes_test(lambda u: u.is_staff)
def delete_theater(request, theater_id):
    """View to delete a theater"""
    theater = get_object_or_404(Theater, id=theater_id)
    theater.delete()
    messages.success(request, 'Theater deleted successfully!')
    return redirect('manage_theaters')

@user_passes_test(lambda u: u.is_staff)
def manage_users(request):
    """View to list and manage users"""
    user_profiles = UserProfile.objects.all().select_related('user').order_by('user__username')
    return render(request, 'admin/manage_users.html', {'user_profiles': user_profiles})

@user_passes_test(lambda u: u.is_staff)
def view_user(request, user_id):
    """View to see user details and activity"""
    user = get_object_or_404(User, id=user_id)
    user_profile = UserProfile.objects.get(user=user)
    tickets = Ticket.objects.filter(user=user).order_by('-purchase_date')
    reviews = Review.objects.filter(user=user).order_by('-created_date')
    
    return render(request, 'admin/user_detail.html', {
        'user': user,
        'profile': user_profile,
        'tickets': tickets,
        'reviews': reviews
    })

@user_passes_test(lambda u: u.is_staff)
def edit_user(request, user_id):
    """View to edit a user's profile"""
    user = get_object_or_404(User, id=user_id)
    user_profile = UserProfile.objects.get(user=user)
    
    if request.method == 'POST':
        form = UserProfileAdminForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'User profile updated successfully!')
            return redirect('manage_users')
    else:
        form = UserProfileAdminForm(instance=user_profile)
    
    return render(request, 'admin/user_form.html', {
        'form': form,
        'user': user,
        'title': 'Edit User Profile'
    })

@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_id):
    """View to delete a user"""
    user = get_object_or_404(User, id=user_id)
    user.delete()  # This will also delete the associated profile due to CASCADE
    messages.success(request, 'User deleted successfully!')
    return redirect('manage_users')

@user_passes_test(lambda u: u.is_staff)
def manage_reviews(request):
    """View to list and manage reviews"""
    reviews = Review.objects.all().select_related('user', 'movie').order_by('-created_date')
    return render(request, 'admin/manage_reviews.html', {'reviews': reviews})

@user_passes_test(lambda u: u.is_staff)
def add_review_admin(request):
    """View for admin to add a review"""
    if request.method == 'POST':
        form = ReviewAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review added successfully!')
            return redirect('manage_reviews')
    else:
        form = ReviewAdminForm()
    
    return render(request, 'admin/review_form.html', {
        'form': form,
        'title': 'Add Review'
    })

@user_passes_test(lambda u: u.is_staff)
def edit_review(request, review_id):
    """View to edit an existing review"""
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'POST':
        form = ReviewAdminForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('manage_reviews')
    else:
        form = ReviewAdminForm(instance=review)
    
    return render(request, 'admin/review_form.html', {
        'form': form,
        'title': 'Edit Review'
    })

@user_passes_test(lambda u: u.is_staff)
def delete_review(request, review_id):
    """View to delete a review"""
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, 'Review deleted successfully!')
    return redirect('manage_reviews')

@user_passes_test(lambda u: u.is_staff)
def manage_tickets(request):
    """View to list and manage tickets"""
    tickets = Ticket.objects.all().select_related('user', 'showtime__movie', 'showtime__theater').order_by('-purchase_date')
    return render(request, 'admin/manage_tickets.html', {'tickets': tickets})

@user_passes_test(lambda u: u.is_staff)
def add_ticket_admin(request):
    """View for admin to add a ticket"""
    if request.method == 'POST':
        form = TicketAdminForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            
            # Update available seats
            showtime = ticket.showtime
            if showtime.available_seats < ticket.quantity:
                messages.error(request, 'Not enough seats available!')
                return render(request, 'admin/ticket_form.html', {
                    'form': form,
                    'title': 'Add Ticket'
                })
                
            showtime.available_seats -= ticket.quantity
            showtime.save()
            
            # Generate barcode if not provided
            if not ticket.barcode:
                ticket.barcode = str(uuid.uuid4())
                
            # The purchase_date will be set automatically by the model
            ticket.save()
            messages.success(request, 'Ticket added successfully!')
            return redirect('manage_tickets')
    else:
        form = TicketAdminForm()
    
    return render(request, 'admin/ticket_form.html', {
        'form': form,
        'title': 'Add Ticket'
    })

@user_passes_test(lambda u: u.is_staff)
def edit_ticket(request, ticket_id):
    """View to edit an existing ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    original_quantity = ticket.quantity
    
    if request.method == 'POST':
        form = TicketAdminForm(request.POST, instance=ticket)
        if form.is_valid():
            updated_ticket = form.save(commit=False)
            
            # Update available seats if quantity changed
            quantity_diff = updated_ticket.quantity - original_quantity
            if quantity_diff != 0:
                showtime = updated_ticket.showtime
                if quantity_diff > 0 and showtime.available_seats < quantity_diff:
                    messages.error(request, 'Not enough seats available!')
                    return render(request, 'admin/ticket_form.html', {
                        'form': form,
                        'title': 'Edit Ticket'
                    })
                
                showtime.available_seats -= quantity_diff
                showtime.save()
            
            updated_ticket.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('manage_tickets')
    else:
        form = TicketAdminForm(instance=ticket)
    
    return render(request, 'admin/ticket_form.html', {
        'form': form,
        'title': 'Edit Ticket'
    })

@user_passes_test(lambda u: u.is_staff)
def delete_ticket(request, ticket_id):
    """View to delete a ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Return seats to inventory
    showtime = ticket.showtime
    showtime.available_seats += ticket.quantity
    showtime.save()
    
    ticket.delete()
    messages.success(request, 'Ticket deleted successfully!')
    return redirect('manage_tickets')

@user_passes_test(lambda u: u.is_staff)
def mark_ticket_used(request, ticket_id):
    """View to mark a ticket as used"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.is_used = True
    ticket.save()
    messages.success(request, 'Ticket marked as used!')
    return redirect('manage_tickets')

@login_required
def delete_user_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    review = get_object_or_404(Review, user=request.user, movie=movie)
    
    # Delete the review
    review.delete()
    messages.success(request, 'Your review has been deleted.')
    return redirect('movie_detail', movie_id=movie_id)