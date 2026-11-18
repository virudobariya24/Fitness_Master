import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from functools import wraps
from django.views.decorators.csrf import ensure_csrf_cookie

from accounts.models import UserProfile
from workouts.models import WorkoutPlan, Exercise, ExerciseCategory, WorkoutLog
from nutrition.models import DietPlan
from challenges.models import Challenge
from core.models import ContactMessage, Feedback

User = get_user_model()


def admin_required(view_func):
    """Decorator ensuring only authenticated admin users can access the custom admin panel."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('custom_admin_login')
        if not request.user.is_admin_user():
            messages.error(request, "Access restricted. Please sign in as an Administrator (Viraj) to access the Custom Admin Portal.")
            return redirect('custom_admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@ensure_csrf_cookie
def admin_login_view(request):
    """Custom Admin Login"""
    if request.user.is_authenticated and request.user.is_admin_user():
        return redirect('admin_dashboard')

    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '')

        user_match = User.objects.filter(Q(username__iexact=u) | Q(email__iexact=u)).first()
        actual_username = user_match.username if user_match else u
        user = authenticate(request, username=actual_username, password=p)
        if user is not None:
            if user.is_admin_user():
                login(request, user)
                messages.success(request, f"Welcome to Custom Admin Panel, {user.username}!")
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access denied. The provided account is not an administrator.")
        else:
            messages.error(request, "Invalid admin username or password.")

    return render(request, 'custom_admin/login.html')


def admin_logout_view(request):
    """Custom Admin Logout"""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Admin logged out successfully.")
    return redirect('custom_admin_login')


@admin_required
def admin_dashboard_view(request):
    """Custom Admin Main Dashboard"""
    total_users = User.objects.filter(role='USER').count()
    total_exercises = Exercise.objects.count()
    total_workouts = WorkoutPlan.objects.count()
    total_diets = DietPlan.objects.count()
    total_challenges = Challenge.objects.count()
    total_messages = ContactMessage.objects.count()

    recent_users = User.objects.filter(role='USER').order_by('-date_joined')[:6]
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]

    # Chart 1: Workout Plans by Goal distribution
    goal_counts = WorkoutPlan.objects.values('goal').annotate(c=Count('id'))
    chart_goals = [item['goal'] for item in goal_counts] or ['Weight Loss', 'Muscle Building', 'Full Body']
    chart_goal_vals = [item['c'] for item in goal_counts] or [4, 3, 2]

    # Chart 2: Recent 7 days activity
    dates = []
    reg_counts = []
    today = timezone.now().date()
    for i in range(6, -1, -1):
        day = today - timezone.timedelta(days=i)
        dates.append(day.strftime('%b %d'))
        count = User.objects.filter(date_joined__date=day, role='USER').count()
        reg_counts.append(count)

    context = {
        'total_users': total_users,
        'total_exercises': total_exercises,
        'total_workouts': total_workouts,
        'total_diets': total_diets,
        'total_challenges': total_challenges,
        'total_messages': total_messages,
        'recent_users': recent_users,
        'recent_messages': recent_messages,
        'chart_goals_json': json.dumps(chart_goals),
        'chart_goal_vals_json': json.dumps(chart_goal_vals),
        'chart_dates_json': json.dumps(dates),
        'chart_regs_json': json.dumps(reg_counts),
    }
    return render(request, 'custom_admin/dashboard.html', context)


# ==========================================
# USER MANAGEMENT (CRUD + BLOCK/UNBLOCK)
# ==========================================
@admin_required
def admin_users_view(request):
    """Admin: List and search users and admins in dedicated separate tables"""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    regular_users = User.objects.filter(role='USER').order_by('-date_joined')
    admin_users = User.objects.filter(role='ADMIN').order_by('-date_joined')

    if query:
        regular_users = regular_users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        admin_users = admin_users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))

    if status_filter == 'blocked':
        regular_users = regular_users.filter(is_blocked=True)
        admin_users = admin_users.filter(is_blocked=True)
    elif status_filter == 'active':
        regular_users = regular_users.filter(is_blocked=False)
        admin_users = admin_users.filter(is_blocked=False)

    return render(request, 'custom_admin/users_list.html', {
        'regular_users': regular_users,
        'admin_users': admin_users,
        'users': regular_users,
        'total_regular_count': regular_users.count(),
        'total_admin_count': admin_users.count(),
        'query': query,
        'status_filter': status_filter,
    })


@admin_required
def admin_user_add_view(request):
    """Admin: Add New User manually"""
    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        e = request.POST.get('email', '').strip()
        p = request.POST.get('password', '')
        fn = request.POST.get('first_name', '').strip()
        ln = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'USER')
        goal = request.POST.get('fitness_goal', 'keep_fit')

        if u and e and p:
            if User.objects.filter(username__iexact=u).exists():
                messages.error(request, "Username already exists.")
            elif User.objects.filter(email__iexact=e).exists():
                messages.error(request, "Email already exists.")
            else:
                user = User.objects.create_user(
                    username=u, email=e, password=p,
                    first_name=fn, last_name=ln, role=role
                )
                if role == 'ADMIN':
                    user.is_staff = True
                    user.save()
                profile = user.profile
                profile.fitness_goal = goal
                profile.save()
                messages.success(request, f"User '{u}' created successfully.")
                return redirect('admin_users')
        else:
            messages.error(request, "Please enter username, email, and password.")

    return render(request, 'custom_admin/user_form.html', {'action': 'Add', 'user_obj': None})


@admin_required
def admin_user_edit_view(request, pk):
    """Admin: Edit User"""
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name', '').strip()
        user_obj.last_name = request.POST.get('last_name', '').strip()
        user_obj.email = request.POST.get('email', '').strip()
        user_obj.role = request.POST.get('role', user_obj.role)
        if user_obj.role == 'ADMIN':
            user_obj.is_staff = True
        user_obj.save()

        profile = user_obj.profile
        profile.fitness_goal = request.POST.get('fitness_goal', profile.fitness_goal)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.save()

        messages.success(request, f"User '{user_obj.username}' updated successfully.")
        return redirect('admin_users')

    return render(request, 'custom_admin/user_form.html', {'action': 'Edit', 'user_obj': user_obj})


@admin_required
def admin_user_toggle_block_view(request, pk):
    """Admin: Block or Unblock User"""
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.error(request, "You cannot block yourself.")
    else:
        user_obj.is_blocked = not user_obj.is_blocked
        user_obj.save()
        status_text = "blocked" if user_obj.is_blocked else "unblocked"
        messages.success(request, f"User '{user_obj.username}' has been {status_text}.")
    return redirect('admin_users')


@admin_required
def admin_user_delete_view(request, pk):
    """Admin: Delete User"""
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.error(request, "You cannot delete yourself.")
    else:
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f"User '{username}' was permanently deleted.")
    return redirect('admin_users')


# ==========================================
# EXERCISE MANAGEMENT (CRUD)
# ==========================================
@admin_required
def admin_exercises_view(request):
    """Admin: Exercise List"""
    exercises = Exercise.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/exercises_list.html', {'exercises': exercises})


@admin_required
def admin_exercise_add_view(request):
    """Admin: Add Exercise"""
    categories = ExerciseCategory.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        cat_id = request.POST.get('category')
        muscle = request.POST.get('target_muscle', '').strip()
        diff = request.POST.get('difficulty', 'Beginner')
        sets = int(request.POST.get('default_sets', 3))
        reps = request.POST.get('default_reps', '12 reps')
        duration = request.POST.get('duration', '45s')
        rest = request.POST.get('rest_time', '60s')
        instr = request.POST.get('instructions', '')
        equip = request.POST.get('equipment_required', 'None')
        img = request.FILES.get('image')

        category = ExerciseCategory.objects.filter(id=cat_id).first() if cat_id else None

        if name and muscle:
            Exercise.objects.create(
                name=name, category=category, target_muscle=muscle,
                difficulty=diff, default_sets=sets, default_reps=reps,
                duration=duration, rest_time=rest, instructions=instr,
                equipment_required=equip, image=img
            )
            messages.success(request, f"Exercise '{name}' added successfully.")
            return redirect('admin_exercises')
        else:
            messages.error(request, "Please enter exercise name and target muscle.")

    return render(request, 'custom_admin/exercise_form.html', {'action': 'Add', 'categories': categories, 'item': None})


@admin_required
def admin_exercise_edit_view(request, pk):
    """Admin: Edit Exercise"""
    item = get_object_or_404(Exercise, pk=pk)
    categories = ExerciseCategory.objects.all()

    if request.method == 'POST':
        item.name = request.POST.get('name', '').strip()
        cat_id = request.POST.get('category')
        item.category = ExerciseCategory.objects.filter(id=cat_id).first() if cat_id else None
        item.target_muscle = request.POST.get('target_muscle', '').strip()
        item.difficulty = request.POST.get('difficulty', item.difficulty)
        item.default_sets = int(request.POST.get('default_sets', item.default_sets))
        item.default_reps = request.POST.get('default_reps', item.default_reps)
        item.duration = request.POST.get('duration', item.duration)
        item.rest_time = request.POST.get('rest_time', item.rest_time)
        item.instructions = request.POST.get('instructions', item.instructions)
        item.equipment_required = request.POST.get('equipment_required', item.equipment_required)
        if request.FILES.get('image'):
            item.image = request.FILES.get('image')
        item.save()
        messages.success(request, f"Exercise '{item.name}' updated.")
        return redirect('admin_exercises')

    return render(request, 'custom_admin/exercise_form.html', {'action': 'Edit', 'categories': categories, 'item': item})


@admin_required
def admin_exercise_delete_view(request, pk):
    """Admin: Delete Exercise"""
    item = get_object_or_404(Exercise, pk=pk)
    name = item.name
    item.delete()
    messages.success(request, f"Exercise '{name}' deleted.")
    return redirect('admin_exercises')


# ==========================================
# WORKOUT PLAN MANAGEMENT (CRUD)
# ==========================================
@admin_required
def admin_workouts_view(request):
    """Admin: Workout Plans List"""
    plans = WorkoutPlan.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/workouts_list.html', {'plans': plans})


@admin_required
def admin_workout_add_view(request):
    """Admin: Add Workout Plan"""
    categories = ExerciseCategory.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        goal = request.POST.get('goal', 'Full Body Workout')
        diff = request.POST.get('difficulty_level', 'Beginner')
        duration = int(request.POST.get('duration_weeks', 4))
        days = int(request.POST.get('days_per_week', 4))
        cal = int(request.POST.get('estimated_calories_burn', 350))
        desc = request.POST.get('description', '')
        featured = request.POST.get('is_featured') == 'on'
        img = request.FILES.get('image')

        if title:
            WorkoutPlan.objects.create(
                title=title, goal=goal, difficulty_level=diff,
                duration_weeks=duration, days_per_week=days,
                estimated_calories_burn=cal, description=desc,
                is_featured=featured, image=img
            )
            messages.success(request, f"Workout Plan '{title}' created successfully.")
            return redirect('admin_workouts')
        else:
            messages.error(request, "Please enter a plan title.")

    return render(request, 'custom_admin/workout_form.html', {'action': 'Add', 'categories': categories, 'plan': None})


@admin_required
def admin_workout_edit_view(request, pk):
    """Admin: Edit Workout Plan"""
    plan = get_object_or_404(WorkoutPlan, pk=pk)
    categories = ExerciseCategory.objects.all()

    if request.method == 'POST':
        plan.title = request.POST.get('title', '').strip()
        plan.goal = request.POST.get('goal', plan.goal)
        plan.difficulty_level = request.POST.get('difficulty_level', plan.difficulty_level)
        plan.duration_weeks = int(request.POST.get('duration_weeks', plan.duration_weeks))
        plan.days_per_week = int(request.POST.get('days_per_week', plan.days_per_week))
        plan.estimated_calories_burn = int(request.POST.get('estimated_calories_burn', plan.estimated_calories_burn))
        plan.description = request.POST.get('description', plan.description)
        plan.is_featured = request.POST.get('is_featured') == 'on'
        if request.FILES.get('image'):
            plan.image = request.FILES.get('image')
        plan.save()
        messages.success(request, f"Workout Plan '{plan.title}' updated.")
        return redirect('admin_workouts')

    return render(request, 'custom_admin/workout_form.html', {'action': 'Edit', 'categories': categories, 'plan': plan})


@admin_required
def admin_workout_delete_view(request, pk):
    """Admin: Delete Workout Plan"""
    plan = get_object_or_404(WorkoutPlan, pk=pk)
    title = plan.title
    plan.delete()
    messages.success(request, f"Workout Plan '{title}' deleted.")
    return redirect('admin_workouts')


# ==========================================
# DIET PLAN MANAGEMENT (CRUD)
# ==========================================
@admin_required
def admin_diets_view(request):
    """Admin: Diet Plans List"""
    diets = DietPlan.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/diets_list.html', {'diets': diets})


@admin_required
def admin_diet_add_view(request):
    """Admin: Add Diet Plan"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        plan_type = request.POST.get('plan_type', 'Maintenance Diet')
        cal = int(request.POST.get('target_calories', 2000))
        pro = int(request.POST.get('target_protein', 140))
        carbs = int(request.POST.get('target_carbs', 220))
        fat = int(request.POST.get('target_fat', 60))
        desc = request.POST.get('description', '')
        featured = request.POST.get('is_featured') == 'on'
        img = request.FILES.get('image')

        if name:
            DietPlan.objects.create(
                name=name, plan_type=plan_type, target_calories=cal,
                target_protein=pro, target_carbs=carbs, target_fat=fat,
                description=desc, is_featured=featured, image=img
            )
            messages.success(request, f"Diet Plan '{name}' added successfully.")
            return redirect('admin_diets')
        else:
            messages.error(request, "Please enter a diet plan name.")

    return render(request, 'custom_admin/diet_form.html', {'action': 'Add', 'diet': None})


@admin_required
def admin_diet_edit_view(request, pk):
    """Admin: Edit Diet Plan"""
    diet = get_object_or_404(DietPlan, pk=pk)
    if request.method == 'POST':
        diet.name = request.POST.get('name', '').strip()
        diet.plan_type = request.POST.get('plan_type', diet.plan_type)
        diet.target_calories = int(request.POST.get('target_calories', diet.target_calories))
        diet.target_protein = int(request.POST.get('target_protein', diet.target_protein))
        diet.target_carbs = int(request.POST.get('target_carbs', diet.target_carbs))
        diet.target_fat = int(request.POST.get('target_fat', diet.target_fat))
        diet.description = request.POST.get('description', diet.description)
        diet.is_featured = request.POST.get('is_featured') == 'on'
        if request.FILES.get('image'):
            diet.image = request.FILES.get('image')
        diet.save()
        messages.success(request, f"Diet Plan '{diet.name}' updated.")
        return redirect('admin_diets')

    return render(request, 'custom_admin/diet_form.html', {'action': 'Edit', 'diet': diet})


@admin_required
def admin_diet_delete_view(request, pk):
    """Admin: Delete Diet Plan"""
    diet = get_object_or_404(DietPlan, pk=pk)
    name = diet.name
    diet.delete()
    messages.success(request, f"Diet Plan '{name}' deleted.")
    return redirect('admin_diets')


# ==========================================
# CHALLENGES MANAGEMENT (CRUD)
# ==========================================
@admin_required
def admin_challenges_view(request):
    """Admin: Challenges List"""
    challenges = Challenge.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/challenges_list.html', {'challenges': challenges})


@admin_required
def admin_challenge_add_view(request):
    """Admin: Add Challenge"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        c_type = request.POST.get('challenge_type', 'Workout')
        days = int(request.POST.get('duration_days', 30))
        target = request.POST.get('target_description', '')
        badge = request.POST.get('badge_name', 'Fitness Master Badge')
        desc = request.POST.get('description', '')
        img = request.FILES.get('image')

        if title:
            Challenge.objects.create(
                title=title, challenge_type=c_type, duration_days=days,
                target_description=target, badge_name=badge,
                description=desc, image=img
            )
            messages.success(request, f"Challenge '{title}' created successfully.")
            return redirect('admin_challenges')
        else:
            messages.error(request, "Please enter challenge title.")

    return render(request, 'custom_admin/challenge_form.html', {'action': 'Add', 'challenge': None})


@admin_required
def admin_challenge_edit_view(request, pk):
    """Admin: Edit Challenge"""
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == 'POST':
        challenge.title = request.POST.get('title', '').strip()
        challenge.challenge_type = request.POST.get('challenge_type', challenge.challenge_type)
        challenge.duration_days = int(request.POST.get('duration_days', challenge.duration_days))
        challenge.target_description = request.POST.get('target_description', challenge.target_description)
        challenge.badge_name = request.POST.get('badge_name', challenge.badge_name)
        challenge.description = request.POST.get('description', challenge.description)
        if request.FILES.get('image'):
            challenge.image = request.FILES.get('image')
        challenge.save()
        messages.success(request, f"Challenge '{challenge.title}' updated.")
        return redirect('admin_challenges')

    return render(request, 'custom_admin/challenge_form.html', {'action': 'Edit', 'challenge': challenge})


@admin_required
def admin_challenge_delete_view(request, pk):
    """Admin: Delete Challenge"""
    challenge = get_object_or_404(Challenge, pk=pk)
    title = challenge.title
    challenge.delete()
    messages.success(request, f"Challenge '{title}' deleted.")
    return redirect('admin_challenges')


# ==========================================
# CONTACT MESSAGES & FEEDBACK
# ==========================================
@admin_required
def admin_messages_view(request):
    """Admin: View Inquiries & Feedback"""
    inquiries = ContactMessage.objects.all().order_by('-created_at')
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/messages_list.html', {
        'inquiries': inquiries,
        'feedbacks': feedbacks,
    })


@admin_required
def admin_message_toggle_read_view(request, pk):
    """Admin: Toggle Message Read Status"""
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save()
    status = "marked as read" if msg.is_read else "marked as unread"
    messages.success(request, f"Message from {msg.name} {status}.")
    return redirect('admin_messages')


@admin_required
def admin_message_delete_view(request, pk):
    """Admin: Delete Message"""
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, "Message deleted.")
    return redirect('admin_messages')


# ==========================================
# REPORTS & ANALYTICS
# ==========================================
@admin_required
def admin_analytics_view(request):
    """Admin: Reports & Analytics with Chart.js"""
    total_users = User.objects.filter(role='USER').count()
    total_logs = WorkoutLog.objects.count()
    total_minutes = sum(log.duration_minutes for log in WorkoutLog.objects.all())

    # User registration breakdown by fitness goal
    goal_distribution = UserProfile.objects.values('fitness_goal').annotate(c=Count('id'))
    goal_labels = [dict(UserProfile.GOAL_CHOICES).get(g['fitness_goal'], g['fitness_goal']) for g in goal_distribution]
    goal_counts = [g['c'] for g in goal_distribution]

    # Weekly workout minutes
    today = timezone.now().date()
    days_labels = []
    daily_minutes = []
    for i in range(6, -1, -1):
        d = today - timezone.timedelta(days=i)
        days_labels.append(d.strftime('%a %d'))
        mins = sum(l.duration_minutes for l in WorkoutLog.objects.filter(completed_at__date=d))
        daily_minutes.append(mins)

    context = {
        'total_users': total_users,
        'total_logs': total_logs,
        'total_minutes': total_minutes,
        'goal_labels_json': json.dumps(goal_labels or ['Weight Loss', 'Muscle Building', 'General Fitness']),
        'goal_counts_json': json.dumps(goal_counts or [5, 4, 3]),
        'days_labels_json': json.dumps(days_labels),
        'daily_minutes_json': json.dumps(daily_minutes),
    }
    return render(request, 'custom_admin/analytics.html', context)


# ==========================================
# ADMIN PROFILE & SETTINGS
# ==========================================
@admin_required
def admin_profile_view(request):
    """Admin: Profile & Settings"""
    admin_user = request.user
    if request.method == 'POST':
        admin_user.first_name = request.POST.get('first_name', '').strip()
        admin_user.last_name = request.POST.get('last_name', '').strip()
        admin_user.email = request.POST.get('email', '').strip()
        new_pwd = request.POST.get('new_password', '').strip()
        if new_pwd:
            admin_user.set_password(new_pwd)
        admin_user.save()
        messages.success(request, "Admin settings updated successfully.")
        return redirect('admin_profile')

    return render(request, 'custom_admin/profile.html', {'admin_user': admin_user})
