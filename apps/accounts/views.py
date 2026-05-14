"""
Views for the accounts app.
Handles authentication, registration, profile management, and user settings.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Count, Q

from .models import User, UserDocument, ActivityLog, UserPreference
from .forms import (
    UserRegistrationForm, UserLoginForm, BorrowerProfileForm,
    LenderProfileForm, UserPreferenceForm, DocumentUploadForm, PasswordUpdateForm
)


class RegisterView(CreateView):
    """Handle user registration."""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
# User preferences created by signal
        # Log activity
        ActivityLog.objects.create(
            user=self.object,
            activity_type='login',
            description='Account created successfully'
        )
        messages.success(self.request, 'Registration successful! Please log in.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('marketplace:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get('remember_me')
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Your account has been deactivated.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                login(request, user)
                user.last_activity = timezone.now()
                user.save(update_fields=['last_activity'])
                
                # Log activity
                ActivityLog.objects.create(
                    user=user,
                    activity_type='login',
                    description=f'User logged in from {request.META.get("REMOTE_ADDR", "unknown")}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                if not remember_me:
                    request.session.set_expiry(0)
                
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('marketplace:dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            activity_type='logout',
            description='User logged out'
        )
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Display and edit user profile."""
    user = request.user
    documents = user.documents.all()
    activity_logs = user.activity_logs.all()[:10]
    
    # Determine which profile form to use
    if user.is_lender:
        profile_form_class = LenderProfileForm
    else:
        profile_form_class = BorrowerProfileForm
    
    if request.method == 'POST':
        profile_form = profile_form_class(request.POST, request.FILES, instance=user)
        if profile_form.is_valid():
            profile_form.save()
            ActivityLog.objects.create(
                user=user,
                activity_type='profile_update',
                description='Profile updated'
            )
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = profile_form_class(instance=user)
    
    context = {
        'profile_form': profile_form,
        'documents': documents,
        'activity_logs': activity_logs,
        'profile_completion': user.profile_completion,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def upload_document(request):
    """Handle document upload."""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            ActivityLog.objects.create(
                user=request.user,
                activity_type='document_upload',
                description=f'Uploaded {document.get_document_type_display()}'
            )
            messages.success(request, 'Document uploaded successfully!')
            return redirect('accounts:profile')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'accounts/upload_document.html', {'form': form})


@login_required
def settings_view(request):
    """Handle user settings and preferences."""
    user = request.user
    
    # Get or create preferences
    preferences, created = UserPreference.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        pref_form = UserPreferenceForm(request.POST, instance=preferences)
        if pref_form.is_valid():
            pref_form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('accounts:settings')
    else:
        pref_form = UserPreferenceForm(instance=preferences)
    
    context = {
        'pref_form': pref_form,
    }
    return render(request, 'accounts/settings.html', context)


@login_required
def activity_log_view(request):
    """Display user activity log."""
    logs = request.user.activity_logs.all()
    
    # Filter by activity type
    activity_type = request.GET.get('type')
    if activity_type:
        logs = logs.filter(activity_type=activity_type)
    
    context = {
        'logs': logs,
        'activity_types': ActivityLog.ACTIVITY_TYPES,
    }
    return render(request, 'accounts/activity_log.html', context)


class LandingPageView(TemplateView):
    """Display the landing page."""
    template_name = 'accounts/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.filter(is_active=True).count()
        context['total_borrowers'] = User.objects.filter(role='borrower', is_active=True).count()
        context['total_lenders'] = User.objects.filter(role='lender', is_active=True).count()
        return context
