from django import forms
from .models import UserProfile, Review, Showtime, Movie, Theater
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.forms import UserCreationForm
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
        fields = ('username', 'email', 'password1', 'password2')

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