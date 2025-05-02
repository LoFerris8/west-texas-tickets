from django import forms
from .models import UserProfile, Review, Showtime, Movie, Theater, Ticket
from django.core.validators import MaxValueValidator, MinValueValidator, EmailValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form with additional styling and fields for phone number and home address
    """
    phone_number = forms.CharField(max_length=15, required=True, label="Phone Number")
    home_address = forms.CharField(max_length=255, required=True, label="Home Address")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required and add CSS class
        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'phone_number', 'home_address', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        logger.debug(f"Validating phone_number: {phone_number}")
        if not phone_number or phone_number.strip() == "":
            raise forms.ValidationError("Phone number is required and cannot be empty.")
        return phone_number

    def clean_home_address(self):
        home_address = self.cleaned_data.get('home_address')
        logger.debug(f"Validating home_address: {home_address}")
        if not home_address or home_address.strip() == "":
            raise forms.ValidationError("Home address is required and cannot be empty.")
        return home_address
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        logger.debug(f"Validating username (email): {username}")
        
        # Check if empty
        if not username or username.strip() == "":
            raise forms.ValidationError("Email is required and cannot be empty.")
        
        # Use Django's EmailValidator to validate email format
        email_validator = EmailValidator(message="Enter a valid email address.")
        try:
            email_validator(username)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate all fields are not empty
        for field_name, field_value in cleaned_data.items():
            if field_name not in ['password1', 'password2']:  # Skip password fields as they have their own validation
                if not field_value or (isinstance(field_value, str) and field_value.strip() == ""):
                    self.add_error(field_name, f"{field_name.replace('_', ' ').title()} is required.")
    
        return cleaned_data

    def save(self, commit=True):
        """
        Save the user and create/update the UserProfile with phone_number and home_address.
        Ensures data is written to Ticketing_userprofile with validation and verification.
        """
        user = super().save(commit=False)
        logger.info(f"Attempting to save user: {user.username}, commit={commit}")

        if commit:
            try:
                with transaction.atomic():
                    # Save the User instance (updates auth_user)
                    user.save()
                    logger.info(f"User saved successfully to auth_user: {user.username}")

                    # Validate cleaned_data
                    phone_number = self.cleaned_data.get('phone_number')
                    home_address = self.cleaned_data.get('home_address')
                    logger.info(f"Raw cleaned_data - phone_number: {phone_number!r}, home_address: {home_address!r}")

                    if not phone_number or not home_address:
                        logger.error(f"Invalid data: phone_number={phone_number!r}, home_address={home_address!r}")
                        raise ValueError("Phone number and home address are required and cannot be empty")

                    # Check if UserProfile exists (may have been created by signal)
                    try:
                        profile = UserProfile.objects.get(user=user)
                        logger.info(f"UserProfile exists for user: {user.username}, updating fields")
                        created = False
                    except UserProfile.DoesNotExist:
                        logger.info(f"No UserProfile exists for user: {user.username}, creating new")
                        created = True
                        profile = None

                    # Update or create UserProfile (updates Ticketing_userprofile)
                    if created:
                        profile = UserProfile.objects.create(
                            user=user,
                            phone_number=phone_number,
                            address=home_address
                        )
                        logger.info(f"Created UserProfile in Ticketing_userprofile: phone_number={profile.phone_number!r}, address={profile.address!r}")
                    else:
                        profile.phone_number = phone_number
                        profile.address = home_address
                        profile.save()
                        logger.info(f"Updated UserProfile in Ticketing_userprofile: phone_number={profile.phone_number!r}, address={profile.address!r}")

                    # Verify the data was saved
                    saved_profile = UserProfile.objects.get(user=user)
                    if saved_profile.phone_number != phone_number or saved_profile.address != home_address:
                        logger.error(f"Final verification failed: expected phone_number={phone_number!r}, address={home_address!r}, got phone_number={saved_profile.phone_number!r}, address={saved_profile.address!r}")
                        raise ValueError("Failed to save UserProfile data to Ticketing_userprofile")

            except IntegrityError as e:
                logger.error(f"IntegrityError saving User or UserProfile: {e}")
                raise
            except ValueError as e:
                logger.error(f"Validation error: {e}")
                raise
            except UserProfile.DoesNotExist:
                logger.error("UserProfile not found after save attempt")
                raise
            except Exception as e:
                logger.error(f"Unexpected error saving UserProfile: {e}")
                raise

        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        label="Password"
    )

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="First Name"
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Last Name"
    )

    username = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Email"
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['username'].initial = user.username

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'placeholder': 'Share your thoughts about the movie...'})
        }

class TicketPurchaseForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('credit_card', 'Credit Card'),
            ('venmo', 'Venmo'),
            ('paypal', 'PayPal'),
        ],
        widget=forms.RadioSelect
    )
    
    # Credit Card fields
    card_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Card Number', 'class': 'form-control'}))
    expiration_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'class': 'form-control'}))
    cvv = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'CVV', 'class': 'form-control'}))
    
    # Venmo field
    venmo_username = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '@venmo-username', 'class': 'form-control'}))
    
    # PayPal field
    paypal_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder': 'PayPal Email', 'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'credit_card':
            if not cleaned_data.get('card_number'):
                raise forms.ValidationError('Card number is required for credit card payment')
            if not cleaned_data.get('expiration_date'):
                raise forms.ValidationError('Expiration date is required for credit card payment')
            if not cleaned_data.get('cvv'):
                raise forms.ValidationError('CVV is required for credit card payment')
                
        elif payment_method == 'venmo':
            if not cleaned_data.get('venmo_username'):
                raise forms.ValidationError('Venmo username is required for Venmo payment')
                
        elif payment_method == 'paypal':
            if not cleaned_data.get('paypal_email'):
                raise forms.ValidationError('PayPal email is required for PayPal payment')
                
        return cleaned_data

class ShowtimeForm(forms.ModelForm):
    class Meta:
        model = Showtime
        fields = ['movie', 'theater', 'datetime', 'price', 'available_seats']
        widgets = {
            'datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'price': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'available_seats': forms.NumberInput(attrs={'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all active movies available in the dropdown
        self.fields['movie'].queryset = Movie.objects.filter(is_currently_playing=True)
        # Add custom classes or attributes if needed
        for field_name, field in self.fields.items():
            if field_name != 'datetime':  # Skip datetime field as it already has type
                field.widget.attrs.update({'class': 'form-control'})
                
class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'duration', 'genre', 'release_date', 'is_currently_playing', 'poster', 'cast']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter movie description...'}),
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'is_currently_playing': forms.CheckboxInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes
        for field_name, field in self.fields.items():
            if field_name != 'is_currently_playing':  # Skip checkbox
                field.widget.attrs.update({'class': 'form-control'})

class TheaterForm(forms.ModelForm):
    class Meta:
        model = Theater
        fields = ['name', 'location', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': '3'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class UserProfileAdminForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    is_staff = forms.BooleanField(required=False, label="Staff Status")
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add user fields if instance exists
        if self.instance and self.instance.pk:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['is_staff'].initial = self.instance.user.is_staff
        
        # Add bootstrap classes
        for field_name, field in self.fields.items():
            if field_name != 'is_staff':  # Skip checkbox
                field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update associated user
        if self.instance and self.instance.pk:
            user = profile.user
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.is_staff = self.cleaned_data['is_staff']
            if commit:
                user.save()
        
        if commit:
            profile.save()
        
        return profile

class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['user', 'movie', 'rating', 'comment']  # Remove 'created_date'
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class TicketAdminForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['user', 'showtime', 'quantity', 'total_price', 'barcode', 'is_used']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes
        for field_name, field in self.fields.items():
            if field_name != 'is_used':  # Skip checkbox
                field.widget.attrs.update({'class': 'form-control'})