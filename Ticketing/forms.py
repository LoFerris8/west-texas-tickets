from django import forms
from .models import UserProfile, Review, Showtime, Movie, Theater, Ticket
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form with additional styling
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2')


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
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']

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
    card_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Card Number'}))
    expiration_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}))
    cvv = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'CVV'}))
    
    # Venmo field
    venmo_username = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Venmo Username'}))
    
    # PayPal field
    paypal_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder': 'PayPal Email'}))
    
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
        fields = ['title', 'description', 'duration', 'genre', 'release_date', 'is_currently_playing', 'poster']
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
            'address': forms.Textarea(attrs={'rows': 3}),
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