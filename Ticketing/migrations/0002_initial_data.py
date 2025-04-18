# ticketing/migrations/0002_initial_data.py

from django.db import migrations
from django.utils import timezone
import datetime
from django.contrib.auth.hashers import make_password

def create_theaters(apps, schema_editor):
    Theater = apps.get_model('Ticketing', 'Theater')
    
    theaters = [
        {
            'name': 'West Texas Cinema',
            'location': 'Lubbock',
            'address': '123 Main St, Lubbock, TX 79401'
        },
        {
            'name': 'Star Movies',
            'location': 'Amarillo',
            'address': '456 Broadway Ave, Amarillo, TX 79101'
        },
        {
            'name': 'Levelland Cinemas',
            'location': 'Levelland',
            'address': '789 College Ave, Levelland, TX 79336'
        },
        {
            'name': 'Plainview Theater',
            'location': 'Plainview',
            'address': '321 Main St, Plainview, TX 79072'
        },
        {
            'name': 'Snyder Movie House',
            'location': 'Snyder',
            'address': '654 Western Ave, Snyder, TX 79549'
        },
        {
            'name': 'Abilene Films',
            'location': 'Abilene',
            'address': '987 Pine St, Abilene, TX 79601'
        }
    ]
    
    for theater_data in theaters:
        Theater.objects.create(**theater_data)

def create_sample_users_and_movies(apps, schema_editor):
    # Get models
    User = apps.get_model('auth', 'User')
    Movie = apps.get_model('Ticketing', 'Movie')
    Theater = apps.get_model('Ticketing', 'Theater')
    Showtime = apps.get_model('Ticketing', 'Showtime')
    Review = apps.get_model('Ticketing', 'Review')
    UserProfile = apps.get_model('Ticketing', 'UserProfile')
    
    # Create users
    users = []
    user_data = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_staff': False
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'is_staff': False
        },
        {
            'username': 'mike_wilson',
            'email': 'mike@example.com',
            'password': 'password123',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'is_staff': False
        },
        {
            'username': 'susan_brown',
            'email': 'susan@example.com',
            'password': 'password123',
            'first_name': 'Susan',
            'last_name': 'Brown',
            'is_staff': False
        },
        {
            'username': 'admin_user',
            'email': 'admin@example.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True
        }
    ]
    
    for user_item in user_data:
        # Check if user already exists
        try:
            user = User.objects.get(username=user_item['username'])
        except User.DoesNotExist:
            # Create a hashed password
            hashed_password = make_password(user_item['password'])
            
            # Create user with hashed password
            user = User.objects.create(
                username=user_item['username'],
                email=user_item['email'],
                password=hashed_password,
                first_name=user_item['first_name'],
                last_name=user_item['last_name'],
                is_staff=user_item['is_staff']
            )
            
            # Create user profile
            UserProfile.objects.create(
                user_id=user.id,
                phone_number=f"555-{user.id}00-0000",
                address=f"{user.id}23 Main St, Lubbock, TX"
            )
        
        users.append(user)
    
    # Create movies - some currently playing, some upcoming
    today = timezone.now().date()
    next_month = today + datetime.timedelta(days=30)
    last_month = today - datetime.timedelta(days=30)
    
    movies = [
        # Currently playing movies
        Movie.objects.create(
            title="The Last Adventure",
            description="An epic adventure film about explorers searching for a lost city.",
            duration=120,
            genre="Adventure",
            release_date=last_month,
            is_currently_playing=True
        ),
        Movie.objects.create(
            title="Midnight Mystery",
            description="A detective tries to solve a murder that occurred in a locked room.",
            duration=105,
            genre="Mystery",
            release_date=last_month,
            is_currently_playing=True
        ),
        Movie.objects.create(
            title="Comedy Hour",
            description="A stand-up comedian's life takes an unexpected turn when they become famous overnight.",
            duration=95,
            genre="Comedy",
            release_date=last_month,
            is_currently_playing=True
        ),
        # Upcoming movies
        Movie.objects.create(
            title="Space Odyssey 2050",
            description="Astronauts embark on a journey to a newly discovered planet that might support human life.",
            duration=150,
            genre="Sci-Fi",
            release_date=next_month,
            is_currently_playing=False
        ),
        Movie.objects.create(
            title="Love in Paris",
            description="A romantic story of two strangers who meet in Paris and fall in love.",
            duration=110,
            genre="Romance",
            release_date=next_month,
            is_currently_playing=False
        )
    ]
    
    # Add showtimes for the movies
    theaters = list(Theater.objects.all())
    if theaters:
        # Create showtimes for currently playing movies
        for movie in movies[:3]:  # First 3 are currently playing
            for theater in theaters[:3]:  # Use first 3 theaters
                # Add multiple showtimes
                for day in range(7):  # Next 7 days
                    for hour in [14, 17, 20]:  # 2 PM, 5 PM, 8 PM
                        showtime_date = timezone.now() + datetime.timedelta(days=day)
                        showtime_datetime = datetime.datetime.combine(
                            showtime_date.date(),
                            datetime.time(hour, 0)
                        )
                        Showtime.objects.create(
                            movie=movie,
                            theater=theater,
                            datetime=showtime_datetime,
                            price=10.00 + (hour - 14) * 2,  # Later shows cost more
                            available_seats=100
                        )
    
    # Create reviews
    review_texts = [
        "Absolutely loved it! Great acting and the story kept me engaged throughout.",
        "Decent movie, but the plot was a bit predictable. Still worth watching.",
        "Not what I expected, but in a good way. The cinematography was stunning.",
        "One of the best films I've seen this year. Highly recommended!",
        "The first half was slow, but it picked up in the second half. Overall good experience.",
        "Wonderful performances by the entire cast. The ending was perfect.",
        "A bit disappointed. The trailer promised more than the movie delivered.",
        "Great date night movie. My partner and I both enjoyed it."
    ]
    
    # Add reviews for the first 3 movies (currently playing)
    for i, movie in enumerate(movies[:3]):
        # Each user reviews the movies
        for j, user in enumerate(users):
            # Only add reviews for some combinations to make it realistic
            if (i + j) % 3 != 0:  # Skip some to make it more realistic
                rating = ((i + j) % 5) + 1  # Ratings 1-5
                Review.objects.create(
                    user_id=user.id,
                    movie=movie,
                    rating=rating,
                    comment=review_texts[(i + j) % len(review_texts)]
                )

def delete_theaters(apps, schema_editor):
    Theater = apps.get_model('Ticketing', 'Theater')
    Theater.objects.all().delete()

def delete_sample_data(apps, schema_editor):
    Movie = apps.get_model('Ticketing', 'Movie')
    Review = apps.get_model('Ticketing', 'Review')
    Showtime = apps.get_model('Ticketing', 'Showtime')
    
    Movie.objects.filter(title__in=[
        "The Last Adventure", 
        "Midnight Mystery", 
        "Comedy Hour", 
        "Space Odyssey 2050", 
        "Love in Paris"
    ]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('Ticketing', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_theaters, delete_theaters),
        migrations.RunPython(create_sample_users_and_movies, delete_sample_data),
    ]