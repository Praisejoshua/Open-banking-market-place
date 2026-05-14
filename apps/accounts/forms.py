"""
Forms for the accounts app.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from .models import User, UserDocument, UserPreference


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    
    ROLE_CHOICES = [
        ('borrower', 'I want to apply for a loan (Borrower)'),
        ('lender', 'I want to offer loans (Lender)'),
    ]
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-control'}),
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Enter a valid phone number.')]
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'role-radio'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'})
    )
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the Terms and Conditions and Privacy Policy'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    def generate_username(self):
        
        first_name = self.cleaned_data.get('first_name', '').lower().strip().replace(' ', '')
        last_name = self.cleaned_data.get('last_name', '').lower().strip().replace(' ', '')
        if not first_name or not last_name:
            # Fallback to email prefix
            email = self.cleaned_data.get('email', '')
            username = email.split('@')[0].replace('.', '_')
        else:
            username = f'{first_name}.{last_name}'
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.generate_username()
        if commit:
            user.save()
        self.save_m2m()
        return user


class UserLoginForm(AuthenticationForm):
    """Form for user login."""
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Remember me'
    )


class BorrowerProfileForm(forms.ModelForm):
    """Form for borrowers to complete their profile."""
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'gender', 'address', 'city', 'state', 'profile_picture',
            'annual_income', 'employment_status', 'employer_name',
            'job_title', 'years_employed', 'bvn', 'nin'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'annual_income': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'employer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'years_employed': forms.NumberInput(attrs={'class': 'form-control'}),
            'bvn': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '11'}),
            'nin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '11'}),
        }


class LenderProfileForm(forms.ModelForm):
    """Form for lenders to complete their profile."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'company_name',
            'company_registration', 'license_number', 'address', 'city',
            'state', 'profile_picture'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_registration': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class UserPreferenceForm(forms.ModelForm):
    """Form for user preferences."""
    
    class Meta:
        model = UserPreference
        fields = [
            'email_notifications', 'sms_notifications', 'push_notifications',
            'marketing_emails', 'language', 'currency', 'timezone'
        ]
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'marketing_emails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
        }


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading verification documents."""
    
    class Meta:
        model = UserDocument
        fields = ['document_type', 'document_file', 'document_number', 'issue_date', 'expiry_date']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class PasswordUpdateForm(PasswordChangeForm):
    """Form for updating password."""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )
