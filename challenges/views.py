from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Challenge, ChallengeProgress, Achievement


@login_required(login_url='login')
def challenges_list_view(request):
    """User Panel: Browse and track fitness challenges"""
    challenges = Challenge.objects.all()
    user_progress = {
        cp.challenge_id: cp
        for cp in ChallengeProgress.objects.filter(user=request.user)
    }

    challenge_items = []
    for ch in challenges:
        prog = user_progress.get(ch.id)
        challenge_items.append({
            'challenge': ch,
            'is_joined': prog is not None,
            'progress': prog,
        })

    context = {
        'challenge_items': challenge_items,
    }
    return render(request, 'challenges/challenges_list.html', context)


@login_required(login_url='login')
def join_challenge_view(request, pk):
    """Join a challenge"""
    challenge = get_object_or_404(Challenge, pk=pk)
    prog, created = ChallengeProgress.objects.get_or_create(
        user=request.user,
        challenge=challenge
    )
    if created:
        messages.success(request, f"🏆 You have joined the '{challenge.title}'! Let's crush it together.")
    else:
        messages.info(request, f"You are already enrolled in '{challenge.title}'.")
    return redirect('user_challenges')


@login_required(login_url='login')
def checkin_challenge_day_view(request, pk):
    """Check in a completed daily task for the challenge"""
    prog = get_object_or_404(ChallengeProgress, user=request.user, pk=pk)
    if not prog.is_completed:
        prog.days_completed += 1
        prog.save()
        prog.check_and_complete()
        if prog.is_completed:
            messages.success(request, f"🎉 Congratulations! You have conquered the '{prog.challenge.title}' and unlocked a new achievement badge!")
        else:
            messages.success(request, f"✅ Day {prog.days_completed} completed! Keep the momentum going.")
    return redirect('user_challenges')


@login_required(login_url='login')
def achievements_view(request):
    """User Panel: Badges and Achievements"""
    unlocked = Achievement.objects.filter(user=request.user).order_by('-unlocked_at')
    
    # Available badge showcase
    all_challenges = Challenge.objects.all()

    context = {
        'unlocked': unlocked,
        'all_challenges': all_challenges,
        'unlocked_count': unlocked.count(),
    }
    return render(request, 'challenges/achievements.html', context)
