from django.shortcuts import render
from .models import Committee, Staff

def team_list_view(request):
    """
    Displays active committees, their members, and the management team (staff).
    """
    active_committees = Committee.objects.filter(is_active=True).prefetch_related('memberships__person')
    management_team = Staff.objects.filter(is_active=True).select_related('person')

    context = {
        'committees': active_committees,
        'management_team': management_team,
        'page_title': 'Our Team'
    }
    return render(request, 'team/team_list.html', context)

def past_team_list_view(request):
    """
    Displays past committees and their members.
    """
    past_committees = Committee.objects.filter(is_active=False).order_by('-tenure_bs').prefetch_related('memberships__person')
    
    context = {
        'committees': past_committees,
        'page_title': 'Past Committees'
    }
    return render(request, 'team/past_team_list.html', context)
