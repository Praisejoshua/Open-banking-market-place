"""
Banking models for Open Banking integration.
Handles linked bank accounts and transactions (simulated Open Banking data).
"""
import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings


class BankAccount(models.Model):
    """Linked bank accounts via Open Banking."""
    
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('current', 'Current Account'),
        ('credit', 'Credit Card'),
        ('fixed_deposit', 'Fixed Deposit'),
        ('investment', 'Investment Account'),
        ('loan', 'Loan Account'),
    ]
    
    STATUS_CHOICES = [
        ('linked', 'Linked'),
        ('syncing', 'Syncing'),
        ('error', 'Error'),
        ('disconnected', 'Disconnected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_accounts'
    )
    
    # Bank information
    bank_id = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=200)
    
    # Account details (masked for security)
    account_number = models.CharField(max_length=20)  # Masked
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    currency = models.CharField(max_length=10, default='NGN')
    
    # Balance
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    account_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Open Banking
    consent_id = models.CharField(max_length=200, blank=True)
    consent_expires_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='linked')
    is_primary = models.BooleanField(default=False)
    
    # Metadata
    opened_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['bank_id']),
        ]
    
    def __str__(self):
        return f"{self.bank_name} - {self.masked_account_number}"
    
    @property
    def masked_account_number(self):
        """Return masked account number for display."""
        if len(self.account_number) > 4:
            return f"****{self.account_number[-4:]}"
        return "****"


class Transaction(models.Model):
    """Bank transactions retrieved via Open Banking."""
    
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('transfer', 'Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    ]
    
    CATEGORIES = [
        ('income', 'Income/Salary'),
        ('food', 'Food & Dining'),
        ('transport', 'Transportation'),
        ('shopping', 'Shopping'),
        ('utilities', 'Utilities'),
        ('entertainment', 'Entertainment'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('rent', 'Rent/Housing'),
        ('transfer', 'Transfer'),
        ('investment', 'Investment'),
        ('loan', 'Loan Payment'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True)
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Description
    description = models.CharField(max_length=500)
    category = models.CharField(max_length=30, choices=CATEGORIES, default='other')
    merchant_name = models.CharField(max_length=200, blank=True)
    
    # Balance after transaction
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # Metadata
    reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'transaction_date']),
            models.Index(fields=['account', 'transaction_date']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type.upper()} - N{self.amount:,.2f} - {self.description[:50]}"
