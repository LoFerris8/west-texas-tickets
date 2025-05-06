# West Texas Tickets

A full-featured movie ticketing system built with Django for West Texas theaters. This application allows users to browse movies, view showtimes, purchase tickets, and write reviews.

## Features

### User Features
- **Movie Browsing**: View currently playing and upcoming movies with filtering options
- **Theater Selection**: Choose from multiple theater locations across West Texas
- **Ticket Purchasing**: Buy tickets online with multiple payment options
- **User Accounts**: Register, login, and manage profile information
- **Movie Reviews**: Rate and review movies after watching
- **Ticket Management**: View purchased tickets with scannable barcodes

### Admin Features
- **Dashboard**: View sales statistics and recent activity
- **Content Management**: Add, edit, and delete movies, showtimes, and theaters
- **User Management**: Manage user accounts and permissions
- **Review Moderation**: Monitor and manage user reviews
- **Ticket Administration**: View and manage ticket sales

## Tech Stack

- **Backend**: Django 5.2
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **CSS Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Barcode Generation**: JsBarcode

## Installation

1. Activate a virtual environment:
   ```
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Run migrations:
   ```
   python manage.py migrate
   ```

3. Run the development server:
   ```
   python manage.py runserver
   ```

9. Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

- **Ticketing/**: Main application with models, views, forms, etc.
- **templates/**: HTML templates organized by feature
- **static/**: CSS, JavaScript, and image files
- **media/**: User-uploaded content (movie posters)
- **West_Texas_Tickets/**: Project settings and main URL configuration

## Database Models

- **Theater**: Movie theater locations across West Texas
- **Movie**: Film details including title, description, genre, etc.
- **Showtime**: Specific screening times linking movies and theaters
- **Ticket**: Purchased tickets linked to users and showtimes
- **Review**: User reviews and ratings for movies
- **UserProfile**: Extended user information (phone, address)
- **Payment**: Secure storage of payment information

## Security Features

- Password hashing using Django's default security
- CSRF protection for all forms
- Payment data encryption
- Admin-only access to sensitive management features
