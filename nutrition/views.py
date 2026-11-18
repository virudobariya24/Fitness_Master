from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DietPlan


@login_required(login_url='login')
def diet_plans_view(request):
    """User Panel: Browse Nutrition & Diet Plans"""
    diet_plans = DietPlan.objects.all()
    user_goal = getattr(request.user.profile, 'fitness_goal', '')

    context = {
        'diet_plans': diet_plans,
        'user_goal': user_goal,
    }
    return render(request, 'nutrition/plans_list.html', context)


@login_required(login_url='login')
def diet_plan_detail_view(request, pk):
    """User Panel: View Daily Meals and Food Items with Macro breakdown"""
    plan = get_object_or_404(DietPlan, pk=pk)
    meals = plan.meals.prefetch_related('food_items').all()

    total_cal = sum(meal.total_calories for meal in meals)
    total_pro = sum(meal.total_protein for meal in meals)

    context = {
        'plan': plan,
        'meals': meals,
        'total_cal': total_cal,
        'total_pro': total_pro,
    }
    return render(request, 'nutrition/plan_detail.html', context)
