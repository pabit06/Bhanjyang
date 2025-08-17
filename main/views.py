from django.shortcuts import render
from team.models import Committee, Membership, Person

def index(request):
    """
    View for the homepage.
    """
    return render(request, 'main/index.html')

def about_view(request):
    """
    View for the 'About Us' page.
    It fetches all the necessary data for the detailed template, including
    different committees, leadership messages, and other context.
    """
    context = {
        'board_members': [],
        'account_supervisor_committee': [],
        'branch_management_sub_committee': [],
        'loan_subcommittee': [],
        'advisory_committee': [],
        'management_team': [],
        'chairman': None,
        'manager': None,
        'former_committees_names': [],
    }

    try:
        # Fetch all active committees and their members efficiently
        active_committees = Committee.objects.filter(is_active=True).prefetch_related('memberships__person').order_by('order')
        
        # A dictionary to map committee names (keywords) to context keys
        committee_map = {
            'Board of Directors': 'board_members',
            'सञ्चालक समिति': 'board_members',
            'Account Supervisor': 'account_supervisor_committee',
            'लेखा समिति': 'account_supervisor_committee',
            'Branch Management': 'branch_management_sub_committee',
            'सेवा केन्द्र': 'branch_management_sub_committee',
            'Loan Subcommittee': 'loan_subcommittee',
            'ऋण उपसमिति': 'loan_subcommittee',
            'Advisory': 'advisory_committee',
            'सल्लाहकार': 'advisory_committee',
            'Management Team': 'management_team',
            'कर्मचारी': 'management_team',
        }

        # Populate the context dictionary based on committee names
        for committee in active_committees:
            for keyword, key in committee_map.items():
                if keyword in committee.name:
                    context[key] = committee.memberships.order_by('order')
                    break
        
        # Specifically find the Chairman and Manager for the message section
        if context['board_members']:
            chairman_membership = context['board_members'].filter(position__icontains='Chairman').first()
            if not chairman_membership:
                chairman_membership = context['board_members'].filter(position__icontains='अध्यक्ष').first()
            if chairman_membership:
                context['chairman'] = chairman_membership.person

        if context['management_team']:
            manager_membership = context['management_team'].filter(position__icontains='Manager').first()
            if not manager_membership:
                manager_membership = context['management_team'].filter(position__icontains='व्यवस्थापक').first()
            if manager_membership:
                context['manager'] = manager_membership.person
                
        # Fetch names of former committees
        context['former_committees_names'] = Committee.objects.filter(is_active=False).values_list('name', flat=True).order_by('-tenure_bs')

    except Exception as e:
        # This will prevent the page from crashing if there's a database error
        print(f"Error fetching data for about page: {e}")

    return render(request, 'main/about.html', context)
