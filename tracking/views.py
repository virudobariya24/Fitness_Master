import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import WaterLog, WeightLog


@login_required(login_url='login')
def progress_overview_view(request):
    """User Panel: Centralized Tracking Hub"""
    user = request.user
    profile = user.profile

    today = timezone.now().date()
    water_log, _ = WaterLog.objects.get_or_create(
        user=user, date=today,
        defaults={'goal_ml': profile.daily_water_goal or 2500}
    )

    recent_weights = list(WeightLog.objects.filter(user=user).order_by('recorded_date')[:14])
    weight_dates = [log.recorded_date.strftime('%b %d') for log in recent_weights]
    weight_values = [float(log.weight) for log in recent_weights]

    context = {
        'profile': profile,
        'water_log': water_log,
        'recent_weights': list(reversed(recent_weights)),
        'weight_dates_json': json.dumps(weight_dates),
        'weight_values_json': json.dumps(weight_values),
    }
    return render(request, 'tracking/overview.html', context)


@login_required(login_url='login')
def water_tracker_view(request):
    """User Panel: Water Intake Tracker with interactive glass counter"""
    user = request.user
    profile = user.profile
    today = timezone.now().date()

    water_log, _ = WaterLog.objects.get_or_create(
        user=user, date=today,
        defaults={'goal_ml': profile.daily_water_goal or 2500}
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_glass':
            water_log.glasses += 1
            water_log.amount_ml += 250
            water_log.save()
            messages.success(request, "💧 Glass added (+250ml)! Keep hydrated.")
        elif action == 'remove_glass' and water_log.glasses > 0:
            water_log.glasses -= 1
            water_log.amount_ml = max(0, water_log.amount_ml - 250)
            water_log.save()
        elif action == 'custom':
            try:
                ml = int(request.POST.get('custom_ml', 0))
                if ml > 0:
                    water_log.amount_ml += ml
                    water_log.glasses = water_log.amount_ml // 250
                    water_log.save()
                    messages.success(request, f"Added {ml}ml to your daily water intake.")
            except ValueError:
                pass
        return redirect('user_water_tracker')

    # Last 7 days water history
    history = WaterLog.objects.filter(user=user).order_by('-date')[:7]

    context = {
        'water_log': water_log,
        'history': history,
        'profile': profile,
    }
    return render(request, 'tracking/water_tracker.html', context)


@login_required(login_url='login')
def add_water_quick_view(request):
    """Quick POST action to increment water log from anywhere"""
    if request.method == 'POST':
        user = request.user
        today = timezone.now().date()
        water_log, _ = WaterLog.objects.get_or_create(
            user=user, date=today,
            defaults={'goal_ml': user.profile.daily_water_goal or 2500}
        )
        water_log.glasses += 1
        water_log.amount_ml += 250
        water_log.save()
        messages.success(request, "💧 +1 Glass (250ml) added!")
    return redirect(request.META.get('HTTP_REFERER', 'user_dashboard'))


@login_required(login_url='login')
def weight_tracker_view(request):
    """User Panel: Weight Tracker with Chart.js visualization"""
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        try:
            val = float(request.POST.get('weight', 0))
            date_str = request.POST.get('recorded_date')
            notes = request.POST.get('notes', '').strip()

            rec_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()

            if val > 20:
                WeightLog.objects.create(
                    user=user,
                    weight=val,
                    recorded_date=rec_date,
                    notes=notes
                )
                # Update current weight on profile
                profile.current_weight = val
                profile.save()
                messages.success(request, f"⚖️ Weight entry of {val} kg recorded.")
                return redirect('user_weight_tracker')
            else:
                messages.error(request, "Please enter a valid weight.")
        except ValueError:
            messages.error(request, "Invalid weight format.")

    logs = WeightLog.objects.filter(user=user).order_by('recorded_date')
    history_logs = WeightLog.objects.filter(user=user).order_by('-recorded_date')

    dates = [log.recorded_date.strftime('%b %d') for log in logs]
    weights = [float(log.weight) for log in logs]

    context = {
        'profile': profile,
        'history_logs': history_logs,
        'dates_json': json.dumps(dates),
        'weights_json': json.dumps(weights),
        'today': timezone.now().date().strftime('%Y-%m-%d'),
    }
    return render(request, 'tracking/weight_tracker.html', context)
