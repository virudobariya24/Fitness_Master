import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import UserProfile
from workouts.models import WorkoutLog, WorkoutPlan
from tracking.models import WaterLog, WeightLog
from challenges.models import ChallengeProgress


@login_required(login_url='login')
def dashboard_overview_view(request):
    """User Personal Fitness Dashboard"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Today's Water Log
    today = timezone.now().date()
    water_log, _ = WaterLog.objects.get_or_create(
        user=user, date=today,
        defaults={'goal_ml': profile.daily_water_goal or 2500}
    )

    # Recent Workouts
    recent_workouts = WorkoutLog.objects.filter(user=user).order_by('-completed_at')[:5]
    total_workouts_count = WorkoutLog.objects.filter(user=user).count()

    # Weight history for Chart.js
    weight_logs = WeightLog.objects.filter(user=user).order_by('recorded_date')[:10]
    weight_dates = [log.recorded_date.strftime('%b %d') for log in weight_logs]
    weight_values = [float(log.weight) for log in weight_logs]

    # If no logs yet, supply default current weight
    if not weight_values and profile.current_weight:
        weight_dates = ['Start', 'Current']
        weight_values = [float(profile.current_weight), float(profile.current_weight)]

    # Active challenges
    active_challenges = ChallengeProgress.objects.filter(user=user, is_completed=False)[:3]

    # Weekly streak estimation
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    weekly_workouts = WorkoutLog.objects.filter(user=user, completed_at__gte=one_week_ago).count()

    context = {
        'profile': profile,
        'water_log': water_log,
        'recent_workouts': recent_workouts,
        'total_workouts_count': total_workouts_count,
        'weekly_workouts': weekly_workouts,
        'active_challenges': active_challenges,
        'weight_dates_json': json.dumps(weight_dates),
        'weight_values_json': json.dumps(weight_values),
        'target_weight': float(profile.target_weight) if profile.target_weight else None,
    }
    return render(request, 'dashboard/overview.html', context)
