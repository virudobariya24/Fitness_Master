from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import WorkoutPlan, Exercise, WorkoutLog, ExerciseCategory


@login_required(login_url='login')
def workout_plans_list_view(request):
    """User Panel: Browse Workout Plans"""
    goal_filter = request.GET.get('goal', '')
    plans = WorkoutPlan.objects.all()
    if goal_filter:
        plans = plans.filter(goal=goal_filter)

    categories = ExerciseCategory.objects.all()
    context = {
        'plans': plans,
        'categories': categories,
        'selected_goal': goal_filter,
    }
    return render(request, 'workouts/plans_list.html', context)


@login_required(login_url='login')
def workout_plan_detail_view(request, pk):
    """User Panel: View Plan & Exercise Steps"""
    plan = get_object_or_404(WorkoutPlan, pk=pk)
    items = plan.items.select_related('exercise').all()
    context = {
        'plan': plan,
        'items': items,
    }
    return render(request, 'workouts/plan_detail.html', context)


@login_required(login_url='login')
def start_workout_view(request, pk):
    """User Panel: Interactive live workout session"""
    plan = get_object_or_404(WorkoutPlan, pk=pk)
    items = plan.items.select_related('exercise').all()

    if request.method == 'POST':
        duration = int(request.POST.get('duration_minutes', 30))
        calories = int(request.POST.get('calories_burned', plan.estimated_calories_burn))
        completed_count = int(request.POST.get('completed_count', items.count()))
        notes = request.POST.get('notes', '').strip()

        WorkoutLog.objects.create(
            user=request.user,
            workout_plan=plan,
            workout_name=plan.title,
            duration_minutes=duration,
            calories_burned=calories,
            exercises_completed=completed_count,
            notes=notes
        )
        messages.success(request, f"🔥 Fantastic effort! '{plan.title}' completed and logged successfully.")
        return redirect('user_workout_history')

    context = {
        'plan': plan,
        'items': items,
    }
    return render(request, 'workouts/start_workout.html', context)


@login_required(login_url='login')
def log_workout_view(request):
    """User Panel: Manually log any workout session"""
    if request.method == 'POST':
        workout_name = request.POST.get('workout_name', '').strip()
        duration = int(request.POST.get('duration_minutes', 30))
        calories = int(request.POST.get('calories_burned', 200))
        exercises_completed = int(request.POST.get('exercises_completed', 5))
        notes = request.POST.get('notes', '').strip()

        if workout_name:
            WorkoutLog.objects.create(
                user=request.user,
                workout_name=workout_name,
                duration_minutes=duration,
                calories_burned=calories,
                exercises_completed=exercises_completed,
                notes=notes
            )
            messages.success(request, f"Workout '{workout_name}' has been saved to your history.")
            return redirect('user_workout_history')
        else:
            messages.error(request, "Please specify the workout name.")

    plans = WorkoutPlan.objects.all()
    return render(request, 'workouts/log_workout.html', {'plans': plans})


@login_required(login_url='login')
def workout_history_view(request):
    """User Panel: Full Workout History"""
    logs = WorkoutLog.objects.filter(user=request.user).order_by('-completed_at')
    total_minutes = sum(log.duration_minutes for log in logs)
    total_calories = sum(log.calories_burned for log in logs)

    context = {
        'logs': logs,
        'total_workouts': logs.count(),
        'total_minutes': total_minutes,
        'total_calories': total_calories,
    }
    return render(request, 'workouts/history.html', context)


@login_required(login_url='login')
def exercise_library_view(request):
    """User Panel: Searchable Exercise Library"""
    query = request.GET.get('q', '').strip()
    muscle_filter = request.GET.get('muscle', '').strip()

    exercises = Exercise.objects.all()
    if query:
        exercises = exercises.filter(name__icontains=query)
    if muscle_filter:
        exercises = exercises.filter(target_muscle__icontains=muscle_filter)

    muscles = ['Chest', 'Back', 'Quads', 'Core', 'Arms', 'Shoulders', 'Full Body']
    context = {
        'exercises': exercises,
        'muscles': muscles,
        'query': query,
        'selected_muscle': muscle_filter,
    }
    return render(request, 'workouts/exercise_library.html', context)
