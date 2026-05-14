"""
Loans models for Open Banking Marketplace.
Core loan processing models including LoanProduct, LoanApplication, CreditScore, and LoanOffer.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class LoanProduct(models.Model):
    """Loan products offered by lenders."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
    ]
    
    LOAN_TYPE_CHOICES = [
        ('personal', 'Personal Loan'),
        ('business', 'Business Loan'),
        ('education', 'Education Loan'),
        ('medical', 'Medical Loan'),
        ('home_improvement', 'Home Improvement'),
        ('debt_consolidation', 'Debt Consolidation'),
        ('agriculture', 'Agriculture Loan'),
        ('travel', 'Travel Loan'),
        ('wedding', 'Wedding Loan'),
        ('emergency', 'Emergency Loan'),
        ('startup', 'Startup Funding'),
        ('equipment', 'Equipment Financing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_products',
        limit_choices_to={'role': 'lender'}
    )
    name = models.CharField(max_length=200)
    loan_type = models.CharField(max_length=30, choices=LOAN_TYPE_CHOICES)
    description = models.TextField()
    
    # Loan terms
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('5000'))])
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('5000'))])
    min_duration_months = models.PositiveIntegerField(default=1)
    max_duration_months = models.PositiveIntegerField(default=12)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text='Annual interest rate in %')
    
    # Fees
    processing_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    late_payment_penalty = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'))
    early_repayment_penalty = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), blank=True)
    
    # Eligibility criteria
    min_credit_score = models.PositiveIntegerField(default=300)
    min_annual_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    max_debt_to_income_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('50.00'))
    requires_collateral = models.BooleanField(default=False)
    collateral_description = models.TextField(blank=True)
    
    # Features
    features = models.JSONField(default=list, blank=True, help_text='List of key features')
    requirements = models.JSONField(default=list, blank=True, help_text='List of required documents')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    approvals_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Loan Product'
        verbose_name_plural = 'Loan Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'loan_type']),
            models.Index(fields=['lender', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.lender.company_name or self.lender.get_full_name()}"
    
    @property
    def interest_rate_display(self):
        return f"{self.interest_rate}%"
    
    @property
    def amount_range(self):
        return f"N{self.min_amount:,.0f} - N{self.max_amount:,.0f}"
    
    @property
    def duration_range(self):
        if self.min_duration_months == self.max_duration_months:
            return f"{self.min_duration_months} months"
        return f"{self.min_duration_months}-{self.max_duration_months} months"


class LoanApplication(models.Model):
    """Loan applications submitted by borrowers."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('credit_check', 'Credit Check in Progress'),
        ('pending_documents', 'Pending Documents'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
        ('disbursed', 'Disbursed'),
        ('in_repayment', 'In Repayment'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_applications',
        limit_choices_to={'role': 'borrower'}
    )
    
    # Loan details
    loan_product = models.ForeignKey(
        LoanProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications'
    )
    loan_type = models.CharField(max_length=30, choices=LoanProduct.LOAN_TYPE_CHOICES)
    purpose = models.TextField(help_text='Purpose of the loan')
    amount_requested = models.DecimalField(max_digits=15, decimal_places=2)
    duration_months = models.PositiveIntegerField()
    
    # Financial details
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2)
    monthly_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    existing_debt = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Employment verification
    employer_name = models.CharField(max_length=200, blank=True)
    employer_address = models.TextField(blank=True)
    employment_verified = models.BooleanField(default=False)
    
    # Application status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    status_notes = models.TextField(blank=True, help_text='Internal notes about the application status')
    
    # Credit assessment
    credit_score = models.PositiveIntegerField(null=True, blank=True)
    risk_category = models.CharField(max_length=20, blank=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Approval details
    amount_approved = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    interest_rate_approved = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_repayment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_applications',
        limit_choices_to={'role': 'lender'}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Disbursement
    disbursement_date = models.DateField(null=True, blank=True)
    disbursement_reference = models.CharField(max_length=100, blank=True)
    
    # Documents
    supporting_documents = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Loan Application'
        verbose_name_plural = 'Loan Applications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['borrower', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['loan_type']),
        ]
    
    def __str__(self):
        return f"Application #{str(self.id)[:8]} - {self.borrower.get_full_name()}"
    
    @property
    def debt_to_income_ratio(self):
        if self.monthly_income == 0:
            return Decimal('0')
        return (self.monthly_expenses + self.existing_debt) / self.monthly_income * 100
    
    @property
    def application_age_days(self):
        if self.submitted_at:
            return (timezone.now() - self.submitted_at).days
        return 0
    
    def submit(self):
        """Submit the loan application for review."""
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()
    
    def approve(self, approved_by, amount=None, interest_rate=None):
        """Approve the loan application."""
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        if amount:
            self.amount_approved = amount
        if interest_rate:
            self.interest_rate_approved = interest_rate
        # Calculate monthly payment
        if self.amount_approved and self.interest_rate_approved and self.duration_months:
            r = self.interest_rate_approved / 100 / 12  # Monthly rate
            n = self.duration_months
            if r > 0:
                self.monthly_payment = self.amount_approved * (r * (1 + r)**n) / ((1 + r)**n - 1)
            else:
                self.monthly_payment = self.amount_approved / n
            self.total_repayment = self.monthly_payment * n
        self.save()
    
    def reject(self, notes=''):
        """Reject the loan application."""
        self.status = 'rejected'
        if notes:
            self.status_notes = notes
        self.save()


class CreditScore(models.Model):
    """Credit scores computed for borrowers."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_score_record',
        limit_choices_to={'role': 'borrower'}
    )
    
    # Score components
    base_score = models.PositiveIntegerField(default=300)
    payment_history_score = models.PositiveIntegerField(default=0)
    credit_utilization_score = models.PositiveIntegerField(default=0)
    credit_history_length_score = models.PositiveIntegerField(default=0)
    credit_mix_score = models.PositiveIntegerField(default=0)
    new_credit_score = models.PositiveIntegerField(default=0)
    
    # Final score
    total_score = models.PositiveIntegerField(validators=[MinValueValidator(300), MaxValueValidator(850)])
    
    # Risk assessment
    risk_category = models.CharField(max_length=20)
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
        ('very_high', 'Very High Risk'),
    ])
    default_probability = models.DecimalField(max_digits=5, decimal_places=2, help_text='Probability of default in %')
    
    # Factors
    positive_factors = models.JSONField(default=list, blank=True)
    negative_factors = models.JSONField(default=list, blank=True)
    
    # Computed from
    computed_from_accounts = models.PositiveIntegerField(default=0)
    computed_from_transactions = models.PositiveIntegerField(default=0)
    
    # Metadata
    computed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Credit Score'
        verbose_name_plural = 'Credit Scores'
        ordering = ['-computed_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Score: {self.total_score}"
    
    def get_risk_category_display(self):
        categories = {
            'excellent': 'Excellent (750-850)',
            'good': 'Good (670-749)',
            'fair': 'Fair (580-669)',
            'poor': 'Poor (300-579)',
        }
        return categories.get(self.risk_category, self.risk_category)
    
    @property
    def score_color(self):
        colors = {
            'excellent': '#27ae60',
            'good': '#2980b9',
            'fair': '#f39c12',
            'poor': '#e74c3c',
        }
        return colors.get(self.risk_category, '#95a5a6')


class LoanOffer(models.Model):
    """Loan offers made by lenders to borrowers."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    lender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_offers',
        limit_choices_to={'role': 'lender'}
    )
    loan_product = models.ForeignKey(
        LoanProduct,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    
    # Offer terms
    amount_offered = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    duration_months = models.PositiveIntegerField()
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2)
    total_repayment = models.DecimalField(max_digits=15, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Offer details
    offer_message = models.TextField(blank=True)
    special_conditions = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Expiry
    expires_at = models.DateTimeField()
    
    # Response
    responded_at = models.DateTimeField(null=True, blank=True)
    response_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Loan Offer'
        verbose_name_plural = 'Loan Offers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['application', 'status']),
            models.Index(fields=['lender', 'status']),
        ]
    
    def __str__(self):
        return f"Offer from {self.lender.company_name or self.lender.get_full_name()} - N{self.amount_offered:,.0f}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def total_cost(self):
        return self.total_repayment + self.processing_fee


class LoanRepayment(models.Model):
    """Loan repayment records."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('late', 'Late'),
        ('missed', 'Missed'),
        ('partial', 'Partial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='repayments'
    )
    installment_number = models.PositiveIntegerField()
    amount_due = models.DecimalField(max_digits=15, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    penalty_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    payment_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Loan Repayment'
        verbose_name_plural = 'Loan Repayments'
        ordering = ['installment_number']
        unique_together = ['application', 'installment_number']
    
    def __str__(self):
        return f"Repayment #{self.installment_number} - {self.application}"
