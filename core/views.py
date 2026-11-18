from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from workouts.models import WorkoutPlan, Exercise, ExerciseCategory
from nutrition.models import DietPlan
from .models import ContactMessage, Feedback


def home_view(request):
    """Public Website Home Page"""
    featured_workouts = WorkoutPlan.objects.filter(is_featured=True)[:3]
    if not featured_workouts.exists():
        featured_workouts = WorkoutPlan.objects.all()[:3]

    featured_diets = DietPlan.objects.filter(is_featured=True)[:3]
    if not featured_diets.exists():
        featured_diets = DietPlan.objects.all()[:3]

    feedbacks = Feedback.objects.filter(is_featured=True)[:3]
    categories = ExerciseCategory.objects.all()[:6]

    stats = {
        'total_exercises': Exercise.objects.count(),
        'total_plans': WorkoutPlan.objects.count(),
        'total_diets': DietPlan.objects.count(),
    }

    context = {
        'featured_workouts': featured_workouts,
        'featured_diets': featured_diets,
        'feedbacks': feedbacks,
        'categories': categories,
        'stats': stats,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    """About Us Page"""
    return render(request, 'core/about.html')


def programs_view(request):
    """Fitness Programs Page with filter"""
    goal_filter = request.GET.get('goal', '')
    difficulty_filter = request.GET.get('difficulty', '')

    plans = WorkoutPlan.objects.all()
    if goal_filter:
        plans = plans.filter(goal=goal_filter)
    if difficulty_filter:
        plans = plans.filter(difficulty_level=difficulty_filter)

    context = {
        'plans': plans,
        'selected_goal': goal_filter,
        'selected_diff': difficulty_filter,
    }
    return render(request, 'core/programs.html', context)


def exercises_view(request):
    """Public Exercise Library"""
    query = request.GET.get('q', '').strip()
    muscle_filter = request.GET.get('muscle', '').strip()
    diff_filter = request.GET.get('difficulty', '').strip()

    exercises = Exercise.objects.all()
    if query:
        exercises = exercises.filter(name__icontains=query)
    if muscle_filter:
        exercises = exercises.filter(target_muscle__icontains=muscle_filter)
    if diff_filter:
        exercises = exercises.filter(difficulty=diff_filter)

    categories = ExerciseCategory.objects.all()
    muscles = ['Chest', 'Back', 'Quads', 'Core', 'Arms', 'Shoulders', 'Full Body']

    context = {
        'exercises': exercises,
        'categories': categories,
        'muscles': muscles,
        'query': query,
        'selected_muscle': muscle_filter,
        'selected_diff': diff_filter,
    }
    return render(request, 'core/exercises.html', context)


def nutrition_view(request):
    """Public Nutrition & Diet Plans"""
    diet_plans = DietPlan.objects.all()
    context = {
        'diet_plans': diet_plans,
    }
    return render(request, 'core/nutrition.html', context)


@ensure_csrf_cookie
def contact_view(request):
    """Contact Us Page with form submission"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject or 'General Inquiry',
                message=message
            )
            messages.success(request, "Thank you for reaching out! Your message has been sent to our fitness team.")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'core/contact.html')


def bmi_calculator_view(request):
    """Interactive BMI Calculator page"""
    return render(request, 'core/bmi_calculator.html')


def calories_calculator_view(request):
    """Interactive Calories & TDEE Calculator page"""
    return render(request, 'core/calories_calculator.html')
