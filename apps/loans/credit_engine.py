"""
Credit Scoring Engine for Open Banking Marketplace.
Implements AI-driven credit scoring using machine learning simulation.
"""
import random
import math
from decimal import Decimal
from django.utils import timezone
from django.conf import settings

from .models import CreditScore, LoanApplication
from apps.banking.models import BankAccount, Transaction


class CreditScoringEngine:
    """
    Credit scoring engine that evaluates borrower creditworthiness.
    Uses a combination of financial data analysis and ML-inspired scoring.
    """
    
    def __init__(self):
        self.weights = settings.CREDIT_SCORING_CONFIG['WEIGHTS']
        self.min_score = settings.CREDIT_SCORING_CONFIG['MIN_SCORE']
        self.max_score = settings.CREDIT_SCORING_CONFIG['MAX_SCORE']
    
    def calculate_score(self, user):
        """
        Calculate comprehensive credit score for a user.
        Returns a CreditScore object.
        """
        # Get user's bank accounts and transactions
        accounts = BankAccount.objects.filter(user=user)
        transactions = Transaction.objects.filter(account__user=user)
        
        # Calculate component scores
        payment_history_score = self._calculate_payment_history(transactions)
        credit_utilization_score = self._calculate_credit_utilization(accounts)
        credit_history_length_score = self._calculate_credit_history_length(accounts)
        credit_mix_score = self._calculate_credit_mix(accounts)
        new_credit_score = self._calculate_new_credit(user)
        
        # Weighted total
        total_score = (
            payment_history_score * self.weights['payment_history'] +
            credit_utilization_score * self.weights['credit_utilization'] +
            credit_history_length_score * self.weights['credit_history_length'] +
            credit_mix_score * self.weights['credit_mix'] +
            new_credit_score * self.weights['new_credit']
        )
        
        # Scale to 300-850 range
        total_score = int(self.min_score + (total_score / 100) * (self.max_score - self.min_score))
        total_score = max(self.min_score, min(self.max_score, total_score))
        
        # Determine risk category
        risk_category = self._get_risk_category(total_score)
        risk_level = self._get_risk_level(total_score)
        default_probability = self._calculate_default_probability(total_score)
        
        # Generate factors
        positive_factors, negative_factors = self._generate_factors(
            payment_history_score, credit_utilization_score,
            credit_history_length_score, credit_mix_score, new_credit_score
        )
        
        # Create or update credit score
        credit_score, created = CreditScore.objects.update_or_create(
            user=user,
            defaults={
                'base_score': 300,
                'payment_history_score': int(payment_history_score * 100),
                'credit_utilization_score': int(credit_utilization_score * 100),
                'credit_history_length_score': int(credit_history_length_score * 100),
                'credit_mix_score': int(credit_mix_score * 100),
                'new_credit_score': int(new_credit_score * 100),
                'total_score': total_score,
                'risk_category': risk_category,
                'risk_level': risk_level,
                'default_probability': Decimal(str(default_probability)),
                'positive_factors': positive_factors,
                'negative_factors': negative_factors,
                'computed_from_accounts': accounts.count(),
                'computed_from_transactions': transactions.count(),
            }
        )
        
        return credit_score
    
    def score_application(self, application):
        """Score a loan application and update the application."""
        credit_score = self.calculate_score(application.borrower)
        
        application.credit_score = credit_score.total_score
        application.risk_category = credit_score.risk_category
        application.risk_score = Decimal(str(credit_score.default_probability))
        
        # Auto-advance status based on score
        if credit_score.total_score >= 580:
            application.status = 'under_review'
        else:
            application.status = 'credit_check'
        
        application.save()
        return credit_score
    
    def _calculate_payment_history(self, transactions):
        """Calculate payment history score (0-100)."""
        if not transactions.exists():
            return 50  # Neutral score for no history
        
        # Analyze transaction patterns
        total_transactions = transactions.count()
        incoming = transactions.filter(transaction_type='credit').count()
        outgoing = transactions.filter(transaction_type='debit').count()
        
        # Check for regular income patterns
        regular_income = self._detect_regular_income(transactions)
        
        # Check for late payments or bounced transactions
        bounced = transactions.filter(status='failed').count()
        bounce_rate = bounced / total_transactions if total_transactions > 0 else 0
        
        # Score calculation
        score = 70  # Base score
        score += min(20, regular_income * 10)  # Up to +20 for regular income
        score -= min(30, bounce_rate * 100)  # Up to -30 for bounced transactions
        
        # Consistency bonus
        if total_transactions > 50:
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_credit_utilization(self, accounts):
        """Calculate credit utilization score (0-100)."""
        if not accounts.exists():
            return 50
        
        total_balance = sum(float(acc.balance) for acc in accounts)
        total_limit = sum(float(acc.account_limit or 0) for acc in accounts if acc.account_type == 'credit')
        
        if total_limit == 0:
            return 70  # No credit accounts = good utilization
        
        utilization = total_balance / total_limit
        
        # Lower utilization is better
        if utilization < 0.1:
            return 95
        elif utilization < 0.3:
            return 85
        elif utilization < 0.5:
            return 70
        elif utilization < 0.7:
            return 50
        elif utilization < 0.9:
            return 30
        else:
            return 15
    
    def _calculate_credit_history_length(self, accounts):
        """Calculate credit history length score (0-100)."""
        if not accounts.exists():
            return 40
        
        # Find oldest account
        oldest_account = min(accounts, key=lambda a: a.opened_date or timezone.now().date())
        
        if not oldest_account.opened_date:
            return 40
        
        age_days = (timezone.now().date() - oldest_account.opened_date).days
        age_years = age_days / 365.25
        
        if age_years >= 10:
            return 95
        elif age_years >= 7:
            return 85
        elif age_years >= 5:
            return 75
        elif age_years >= 3:
            return 65
        elif age_years >= 1:
            return 50
        else:
            return 35
    
    def _calculate_credit_mix(self, accounts):
        """Calculate credit mix score (0-100)."""
        if not accounts.exists():
            return 40
        
        account_types = set(accounts.values_list('account_type', flat=True))
        type_count = len(account_types)
        
        # More diverse account types = better score
        if type_count >= 4:
            return 95
        elif type_count >= 3:
            return 80
        elif type_count >= 2:
            return 65
        else:
            return 50
    
    def _calculate_new_credit(self, user):
        """Calculate new credit score (0-100)."""
        # Check recent loan applications
        recent_apps = LoanApplication.objects.filter(
            borrower=user,
            created_at__gte=timezone.now() - timezone.timedelta(days=90)
        ).count()
        
        # Fewer recent applications = better score
        if recent_apps == 0:
            return 90
        elif recent_apps <= 2:
            return 75
        elif recent_apps <= 4:
            return 55
        elif recent_apps <= 6:
            return 35
        else:
            return 20
    
    def _detect_regular_income(self, transactions):
        """Detect if user has regular income pattern."""
        income_transactions = transactions.filter(
            transaction_type='credit',
            category='income'
        ).order_by('transaction_date')
        
        if income_transactions.count() < 3:
            return 0
        
        # Check for monthly patterns (within 5-day window)
        dates = [t.transaction_date for t in income_transactions]
        monthly_pattern = 0
        
        for i in range(1, len(dates)):
            days_diff = (dates[i] - dates[i-1]).days
            if 25 <= days_diff <= 35:
                monthly_pattern += 1
        
        pattern_ratio = monthly_pattern / (len(dates) - 1) if len(dates) > 1 else 0
        return pattern_ratio
    
    def _get_risk_category(self, score):
        """Get risk category based on score."""
        categories = settings.CREDIT_SCORING_CONFIG['RISK_CATEGORIES']
        for cat, bounds in categories.items():
            if bounds['min'] <= score <= bounds['max']:
                return cat
        return 'poor'
    
    def _get_risk_level(self, score):
        """Get risk level based on score."""
        if score >= 750:
            return 'low'
        elif score >= 670:
            return 'moderate'
        elif score >= 580:
            return 'moderate'
        else:
            return 'high'
    
    def _calculate_default_probability(self, score):
        """Calculate probability of default based on score."""
        # Logistic function mapping score to probability
        # Score 300 -> ~80% probability
        # Score 850 -> ~2% probability
        normalized = (score - 300) / 550  # 0 to 1
        probability = 80 * math.exp(-3 * normalized)
        return round(probability, 2)
    
    def _generate_factors(self, payment, utilization, history, mix, new_credit):
        """Generate positive and negative factors."""
        positive = []
        negative = []
        
        if payment > 70:
            positive.append("Strong payment history with regular income deposits")
        elif payment < 40:
            negative.append("Irregular payment patterns or failed transactions detected")
        
        if utilization > 70:
            positive.append("Low credit utilization - responsible credit usage")
        elif utilization < 30:
            negative.append("High credit utilization ratio")
        
        if history > 70:
            positive.append("Long credit history demonstrates financial stability")
        elif history < 40:
            negative.append("Limited credit history available")
        
        if mix > 70:
            positive.append("Diverse credit portfolio")
        
        if new_credit > 70:
            positive.append("Few recent credit inquiries")
        elif new_credit < 40:
            negative.append("Multiple recent loan applications")
        
        if not positive:
            positive.append("Active bank account with transaction history")
        
        return positive, negative
