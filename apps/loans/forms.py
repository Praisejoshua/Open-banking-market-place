"""
Forms for the loans app.
"""
from django import forms
from decimal import Decimal
from .models import LoanApplication, LoanProduct, LoanOffer


class LoanApplicationForm(forms.ModelForm):
    """Form for submitting a loan application."""
    
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I confirm that all information provided is accurate and agree to the terms and conditions'
    )
    
    class Meta:
        model = LoanApplication
        fields = [
            'loan_type', 'purpose', 'amount_requested', 'duration_months',
            'monthly_income', 'monthly_expenses', 'existing_debt',
            'employer_name', 'employer_address'
        ]
        widgets = {
            'loan_type': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the purpose of this loan'}),
            'amount_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'min': '5000'}),
            'duration_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '60'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            'monthly_expenses': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            'existing_debt': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            'employer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current employer'}),
            'employer_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Employer address'}),
        }
    
    def clean_amount_requested(self):
        amount = self.cleaned_data.get('amount_requested')
        if amount and amount < 5000:
            raise forms.ValidationError('Minimum loan amount is N5,000.')
        return amount
    
    def clean_duration_months(self):
        duration = self.cleaned_data.get('duration_months')
        if duration and (duration < 1 or duration > 60):
            raise forms.ValidationError('Loan duration must be between 1 and 60 months.')
        return duration


class LoanProductForm(forms.ModelForm):
    """Form for creating/editing loan products (lenders)."""
    
    features = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter features, one per line'}),
        required=False,
        help_text='Enter each feature on a new line'
    )
    requirements = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter requirements, one per line'}),
        required=False,
        help_text='Enter each requirement on a new line'
    )
    
    class Meta:
        model = LoanProduct
        fields = [
            'name', 'loan_type', 'description',
            'min_amount', 'max_amount', 'min_duration_months', 'max_duration_months',
            'interest_rate', 'processing_fee_percent', 'late_payment_penalty',
            'early_repayment_penalty', 'min_credit_score', 'min_annual_income',
            'max_debt_to_income_ratio', 'requires_collateral', 'collateral_description',
            'features', 'requirements', 'status', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'loan_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'min_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'max_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'min_duration_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '60'}),
            'max_duration_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '60'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1', 'max': '100'}),
            'processing_fee_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'late_payment_penalty': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'early_repayment_penalty': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'min_credit_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '300', 'max': '850'}),
            'min_annual_income': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'max_debt_to_income_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'max': '100'}),
            'requires_collateral': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'collateral_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')
        min_duration = cleaned_data.get('min_duration_months')
        max_duration = cleaned_data.get('max_duration_months')
        
        if min_amount and max_amount and min_amount > max_amount:
            raise forms.ValidationError('Minimum amount cannot be greater than maximum amount.')
        
        if min_duration and max_duration and min_duration > max_duration:
            raise forms.ValidationError('Minimum duration cannot be greater than maximum duration.')
        
        # Process features and requirements from text to list
        features_text = cleaned_data.get('features', '')
        if features_text:
            cleaned_data['features'] = [f.strip() for f in features_text.split('\n') if f.strip()]
        else:
            cleaned_data['features'] = []
        
        requirements_text = cleaned_data.get('requirements', '')
        if requirements_text:
            cleaned_data['requirements'] = [r.strip() for r in requirements_text.split('\n') if r.strip()]
        else:
            cleaned_data['requirements'] = []
        
        return cleaned_data


class LoanOfferForm(forms.ModelForm):
    """Form for lenders to make loan offers."""
    
    class Meta:
        model = LoanOffer
        fields = ['amount_offered', 'interest_rate', 'duration_months', 'offer_message', 'special_conditions']
        widgets = {
            'amount_offered': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duration_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'offer_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Personalized message to the borrower'}),
            'special_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any special terms or conditions'}),
        }


class LoanApplicationReviewForm(forms.ModelForm):
    """Form for reviewing loan applications (lenders/admins)."""
    
    class Meta:
        model = LoanApplication
        fields = ['status', 'amount_approved', 'interest_rate_approved', 'status_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'amount_approved': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'interest_rate_approved': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ApplicationFilterForm(forms.Form):
    """Form for filtering loan applications."""
    
    STATUS_CHOICES = [('', 'All Statuses')] + LoanApplication.STATUS_CHOICES
    LOAN_TYPE_CHOICES = [('', 'All Types')] + LoanProduct.LOAN_TYPE_CHOICES
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    loan_type = forms.ChoiceField(choices=LOAN_TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or ID'}))
