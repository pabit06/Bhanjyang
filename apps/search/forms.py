from django import forms
from django.db.models import Q
from apps.news_events.models import NewsArticle
from apps.services.models import SavingsAccount, FixedDeposit, LoanType, RemittanceService, MemberRelief
from apps.about.models import Person

class SearchForm(forms.Form):
    """Search form for the website"""
    query = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'Search news, services, team members...',
            'autocomplete': 'off'
        }),
        label='Search'
    )
    
    content_type = forms.ChoiceField(
        choices=[
            ('all', 'All Content'),
            ('news', 'News Articles'),
            ('services', 'Services'),
            ('team', 'Team Members'),
        ],
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent'
        }),
        required=False,
        initial='all'
    )

class QuickSearchForm(forms.Form):
    """Quick search form for header"""
    q = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'Quick search...',
            'autocomplete': 'off'
        }),
        required=False
    )
