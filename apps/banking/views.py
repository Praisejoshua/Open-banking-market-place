"""
Views for the banking app.
Handles Open Banking account linking and transaction viewing.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta

from .models import BankAccount, Transaction
from apps.accounts.models import ActivityLog


@login_required
def linked_accounts(request):
    """View linked bank accounts."""
    accounts = BankAccount.objects.filter(user=request.user)
    
    context = {
        'accounts': accounts,
        'total_balance': accounts.filter(status='linked').aggregate(
            total=Sum('balance')
        )['total'] or 0,
    }
    return render(request, 'banking/linked_accounts.html', context)


@login_required
def link_account(request):
    """Link a new bank account (simulated Open Banking flow)."""
    from django.conf import settings
    
    banks = settings.OPEN_BANKING_CONFIG['SUPPORTED_BANKS']
    
    if request.method == 'POST':
        bank_id = request.POST.get('bank')
        account_number = request.POST.get('account_number')
        account_type = request.POST.get('account_type')
        
        # Find bank info
        bank_info = next((b for b in banks if b['id'] == bank_id), None)
        
        if bank_info and account_number:
            # Create linked account (simulated)
            import random
            from decimal import Decimal
            
            account = BankAccount.objects.create(
                user=request.user,
                bank_id=bank_id,
                bank_name=bank_info['name'],
                account_number=account_number,
                account_name=request.user.get_full_name(),
                account_type=account_type or 'savings',
                balance=Decimal(str(random.uniform(50000, 500000))),
                available_balance=Decimal(str(random.uniform(40000, 450000))),
                status='linked',
                consent_expires_at=timezone.now() + timedelta(days=90),
                last_synced_at=timezone.now(),
                opened_date=timezone.now() - timedelta(days=random.randint(365, 1825)),
            )
            
            # Generate sample transactions
            generate_sample_transactions(account)
            
            ActivityLog.objects.create(
                user=request.user,
                activity_type='bank_link',
                description=f'Linked {bank_info["name"]} account ending in {account_number[-4:]}'
            )
            
            messages.success(request, f'{bank_info["name"]} account linked successfully!')
            return redirect('banking:linked_accounts')
        else:
            messages.error(request, 'Please select a bank and enter your account number.')
    
    context = {
        'banks': banks,
        'account_types': BankAccount.ACCOUNT_TYPES,
    }
    return render(request, 'banking/link_account.html', context)


@login_required
def account_detail(request, pk):
    """View account details and transactions."""
    account = get_object_or_404(BankAccount, id=pk, user=request.user)
    
    # Get recent transactions
    transactions = Transaction.objects.filter(account=account).order_by('-transaction_date')[:50]
    
    # Transaction summary
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_transactions = Transaction.objects.filter(
        account=account,
        transaction_date__gte=thirty_days_ago
    )
    
    total_income = recent_transactions.filter(
        transaction_type='credit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_expenses = recent_transactions.filter(
        transaction_type='debit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Category breakdown
    category_breakdown = recent_transactions.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'account': account,
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_flow': total_income - total_expenses,
        'category_breakdown': category_breakdown,
    }
    return render(request, 'banking/account_detail.html', context)


@login_required
def disconnect_account(request, pk):
    """Disconnect a linked bank account."""
    account = get_object_or_404(BankAccount, id=pk, user=request.user)
    
    if request.method == 'POST':
        account.status = 'disconnected'
        account.save()
        messages.success(request, f'{account.bank_name} account disconnected.')
        return redirect('banking:linked_accounts')
    
    return render(request, 'banking/disconnect_confirm.html', {'account': account})


@login_required
def transactions(request):
    """View all transactions across accounts."""
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')
    
    # Filter by account
    account_id = request.GET.get('account')
    if account_id:
        transactions = transactions.filter(account_id=account_id)
    
    # Filter by type
    tx_type = request.GET.get('type')
    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        transactions = transactions.filter(category=category)
    
    context = {
        'transactions': transactions[:100],
        'accounts': BankAccount.objects.filter(user=request.user),
        'categories': Transaction.CATEGORIES,
    }
    return render(request, 'banking/transactions.html', context)


def generate_sample_transactions(account):
    """Generate sample transactions for a linked account."""
    import random
    from decimal import Decimal
    
    categories = {
        'income': ['Monthly Salary', 'Freelance Payment', 'Bonus', 'Investment Return'],
        'food': ['Grocery Store', 'Restaurant', 'Fast Food', 'Cafe'],
        'transport': ['Uber Ride', 'Fuel Station', 'Bus Fare', 'Car Service'],
        'shopping': ['Online Store', 'Electronics Shop', 'Clothing Store', 'Supermarket'],
        'utilities': ['Electric Bill', 'Water Bill', 'Internet Subscription', 'Phone Bill'],
        'entertainment': ['Movie Tickets', 'Streaming Service', 'Concert', 'Game Purchase'],
        'healthcare': ['Pharmacy', 'Doctor Visit', 'Health Insurance', 'Dental'],
        'education': ['Course Fee', 'Books', 'Online Learning', 'Exam Fee'],
        'rent': ['House Rent', 'Office Rent'],
        'transfer': ['Transfer to Savings', 'Family Support', 'Friend Transfer'],
    }
    
    # Generate 3 months of transactions
    for day_offset in range(90, 0, -1):
        tx_date = timezone.now() - timedelta(days=day_offset)
        
        # 1-3 transactions per day
        for _ in range(random.randint(1, 3)):
            tx_type = random.choice(['credit', 'debit'])
            
            if tx_type == 'credit':
                category = 'income'
                amount = Decimal(str(random.uniform(50000, 500000)))
            else:
                category = random.choice([
                    'food', 'transport', 'shopping', 'utilities',
                    'entertainment', 'healthcare', 'education', 'rent', 'transfer'
                ])
                amount = Decimal(str(random.uniform(500, 50000)))
            
            description = random.choice(categories.get(category, ['Transaction']))
            
            Transaction.objects.create(
                account=account,
                user=account.user,
                transaction_id=f"TXN{random.randint(1000000000, 9999999999)}",
                transaction_date=tx_date.date(),
                transaction_type=tx_type,
                amount=amount,
                description=description,
                category=category,
                balance_after=Decimal(str(random.uniform(10000, 500000))),
                status='completed',
            )
