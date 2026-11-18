import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitnessMaster.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from workouts.models import ExerciseCategory, Exercise, WorkoutPlan, WorkoutItem
from nutrition.models import DietPlan, Meal, FoodItem
from challenges.models import Challenge
from core.models import Feedback, ContactMessage

User = get_user_model()


def seed():
    print("Seeding initial Fitness Master data...")

    # 1. Create Admins (including Viraj)
    admin_viraj, _ = User.objects.get_or_create(
        username='Viraj',
        defaults={
            'email': 'viraj@fitnessmaster.com',
            'first_name': 'Viraj',
            'last_name': 'Administrator',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    admin_viraj.set_password('Viraj123')
    admin_viraj.role = 'ADMIN'
    admin_viraj.is_staff = True
    admin_viraj.is_superuser = True
    admin_viraj.save()
    print("Admin Viraj ready: Viraj / Viraj123")

    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@fitnessmaster.com',
            'first_name': 'Chief',
            'last_name': 'Admin',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    admin_user.set_password('adminpassword123')
    admin_user.save()
    print("Admin user ready: admin / adminpassword123")

    # 2. Create Regular Demo User
    demo_user, _ = User.objects.get_or_create(
        username='john_athlete',
        defaults={
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Miller',
            'role': 'USER',
        }
    )
    demo_user.set_password('userpassword123')
    demo_user.save()
    
    p = demo_user.profile
    p.height = 178.0
    p.current_weight = 76.5
    p.target_weight = 72.0
    p.fitness_goal = 'weight_loss'
    p.activity_level = 'moderate'
    p.daily_water_goal = 2500
    p.daily_calorie_goal = 2100
    p.bio = "Dedicated to building functional strength and lean conditioning."
    p.save()
    print("Demo user ready: john_athlete / userpassword123")

    # 3. Exercise Categories
    cat_data = [
        ('Weight Loss', 'fa-fire', 'High energy expenditure sessions designed for maximum caloric burn.'),
        ('Muscle Building', 'fa-dumbbell', 'Hypertrophy focused resistance training targeting progressive overload.'),
        ('Home Workout', 'fa-house', 'Effective bodyweight and minimal gear routines you can do anywhere.'),
        ('Gym Workout', 'fa-building', 'Comprehensive gym equipment workouts for optimal strength gains.'),
        ('Full Body Workout', 'fa-person-running', 'Compound movements engaging multiple major muscle groups.'),
    ]
    categories = {}
    for name, icon, desc in cat_data:
        cat, _ = ExerciseCategory.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})
        categories[name] = cat

    # 4. Exercises
    ex_list = [
        ('Barbell Back Squat', 'Muscle Building', 'Quads, Glutes & Hamstrings', 'Intermediate', 4, '8-10 reps', '45s', '90s', 'Keep chest elevated, sit hips back, descend to parallel and explode through heels.', 'Barbell & Squat Rack'),
        ('Dumbbell Bench Press', 'Muscle Building', 'Chest & Triceps', 'Beginner', 3, '10-12 reps', '40s', '60s', 'Lie flat on bench, lower dumbbells with elbows at 45 degrees, press straight up.', 'Dumbbells & Flat Bench'),
        ('Standard Push-ups', 'Home Workout', 'Chest, Shoulders & Core', 'Beginner', 3, '15-20 reps', '45s', '45s', 'Maintain rigid plank posture, lower chest until inch from floor, press firmly upward.', 'None (Bodyweight)'),
        ('Romanian Deadlift', 'Gym Workout', 'Hamstrings & Lower Back', 'Intermediate', 3, '10-12 reps', '45s', '75s', 'Hinge at the hips keeping a neutral spine, slight bend in knees, feel stretch in hamstrings.', 'Barbell or Dumbbells'),
        ('Mountain Climbers', 'Weight Loss', 'Core & Cardiovascular', 'Beginner', 3, '45 seconds', '45s', '30s', 'From high plank, rapidly drive alternating knees toward chest with cadence.', 'None (Bodyweight)'),
        ('Dumbbell Bicep Curls', 'Gym Workout', 'Biceps & Forearms', 'Beginner', 3, '12-15 reps', '35s', '45s', 'Keep elbows pinned to your sides, curl weights smoothly toward shoulders.', 'Dumbbells'),
        ('Core Plank Hold', 'Full Body Workout', 'Core & Abdominals', 'Beginner', 3, '60 seconds', '60s', '45s', 'Hold forearm plank position with engaged glutes, flat back and braced core.', 'None (Bodyweight)'),
        ('Burpees', 'Weight Loss', 'Full Body & Conditioning', 'Advanced', 4, '15 reps', '60s', '45s', 'Drop into pushup, jump feet back in, and explode vertically into an overhead reach.', 'None (Bodyweight)'),
    ]

    exercises = {}
    for name, cat_name, muscle, diff, sets, reps, dur, rest, instr, equip in ex_list:
        cat = categories.get(cat_name)
        ex, _ = Exercise.objects.get_or_create(
            name=name,
            defaults={
                'category': cat,
                'target_muscle': muscle,
                'difficulty': diff,
                'default_sets': sets,
                'default_reps': reps,
                'duration': dur,
                'rest_time': rest,
                'instructions': instr,
                'equipment_required': equip
            }
        )
        exercises[name] = ex

    # 5. Workout Plans
    plan1, _ = WorkoutPlan.objects.get_or_create(
        title='4-Week Fat Burn Express',
        defaults={
            'category': categories['Weight Loss'],
            'difficulty_level': 'Beginner',
            'goal': 'Weight Loss',
            'duration_weeks': 4,
            'days_per_week': 4,
            'estimated_calories_burn': 380,
            'description': 'A high-impact metabolic conditioning program designed to elevate heart rate and accelerate fat reduction.',
            'is_featured': True
        }
    )
    WorkoutItem.objects.get_or_create(workout_plan=plan1, exercise=exercises['Mountain Climbers'], defaults={'order': 1, 'sets': 3, 'reps': '45 secs'})
    WorkoutItem.objects.get_or_create(workout_plan=plan1, exercise=exercises['Standard Push-ups'], defaults={'order': 2, 'sets': 3, 'reps': '15 reps'})
    WorkoutItem.objects.get_or_create(workout_plan=plan1, exercise=exercises['Burpees'], defaults={'order': 3, 'sets': 3, 'reps': '12 reps'})
    WorkoutItem.objects.get_or_create(workout_plan=plan1, exercise=exercises['Core Plank Hold'], defaults={'order': 4, 'sets': 3, 'reps': '60 secs'})

    plan2, _ = WorkoutPlan.objects.get_or_create(
        title='Hypertrophy Strength Builder',
        defaults={
            'category': categories['Muscle Building'],
            'difficulty_level': 'Intermediate',
            'goal': 'Muscle Building',
            'duration_weeks': 6,
            'days_per_week': 4,
            'estimated_calories_burn': 420,
            'description': 'Classic resistance splits targeting muscle volume, progressive overload, and upper-lower body power.',
            'is_featured': True
        }
    )
    WorkoutItem.objects.get_or_create(workout_plan=plan2, exercise=exercises['Dumbbell Bench Press'], defaults={'order': 1, 'sets': 4, 'reps': '10 reps'})
    WorkoutItem.objects.get_or_create(workout_plan=plan2, exercise=exercises['Barbell Back Squat'], defaults={'order': 2, 'sets': 4, 'reps': '8 reps'})
    WorkoutItem.objects.get_or_create(workout_plan=plan2, exercise=exercises['Romanian Deadlift'], defaults={'order': 3, 'sets': 3, 'reps': '10 reps'})
    WorkoutItem.objects.get_or_create(workout_plan=plan2, exercise=exercises['Dumbbell Bicep Curls'], defaults={'order': 4, 'sets': 3, 'reps': '12 reps'})

    plan3, _ = WorkoutPlan.objects.get_or_create(
        title='30-Day Full Body Shred',
        defaults={
            'category': categories['Full Body Workout'],
            'difficulty_level': 'Advanced',
            'goal': 'Full Body Workout',
            'duration_weeks': 4,
            'days_per_week': 5,
            'estimated_calories_burn': 480,
            'description': 'Intense compound workouts combining heavy endurance with high-volume body shaping movements.',
            'is_featured': True
        }
    )
    WorkoutItem.objects.get_or_create(workout_plan=plan3, exercise=exercises['Barbell Back Squat'], defaults={'order': 1, 'sets': 4, 'reps': '10 reps'})
    WorkoutItem.objects.get_or_create(workout_plan=plan3, exercise=exercises['Burpees'], defaults={'order': 2, 'sets': 4, 'reps': '15 reps'})
    WorkoutItem.objects.get_or_create(workout_plan=plan3, exercise=exercises['Standard Push-ups'], defaults={'order': 3, 'sets': 3, 'reps': '20 reps'})

    # 6. Diet Plans
    diet1, _ = DietPlan.objects.get_or_create(
        name='High Protein Lean Physique',
        defaults={
            'plan_type': 'Muscle Gain Diet',
            'target_calories': 2400,
            'target_protein': 165,
            'target_carbs': 240,
            'target_fat': 65,
            'description': 'Nutrient-rich fuel structured for muscle repair, glycogen replenishment, and energetic training.',
            'is_featured': True
        }
    )
    m1, _ = Meal.objects.get_or_create(diet_plan=diet1, meal_type='Breakfast', defaults={'name': 'Power Oatmeal & Eggs', 'timing': '08:00 AM'})
    FoodItem.objects.get_or_create(meal=m1, name='Rolled Oats with Berries', defaults={'serving_size': '80g', 'calories': 320, 'protein': 11.0, 'carbohydrates': 54.0, 'fat': 5.0})
    FoodItem.objects.get_or_create(meal=m1, name='Boiled Eggs (3 whole)', defaults={'serving_size': '3 eggs', 'calories': 210, 'protein': 18.0, 'carbohydrates': 1.5, 'fat': 15.0})

    m2, _ = Meal.objects.get_or_create(diet_plan=diet1, meal_type='Lunch', defaults={'name': 'Grilled Chicken & Quinoa', 'timing': '01:00 PM'})
    FoodItem.objects.get_or_create(meal=m2, name='Grilled Chicken Breast', defaults={'serving_size': '200g', 'calories': 330, 'protein': 62.0, 'carbohydrates': 0.0, 'fat': 7.0})
    FoodItem.objects.get_or_create(meal=m2, name='Steamed Quinoa & Broccoli', defaults={'serving_size': '150g', 'calories': 180, 'protein': 7.0, 'carbohydrates': 32.0, 'fat': 3.0})

    m3, _ = Meal.objects.get_or_create(diet_plan=diet1, meal_type='Dinner', defaults={'name': 'Salmon Fillet & Sweet Potato', 'timing': '07:30 PM'})
    FoodItem.objects.get_or_create(meal=m3, name='Baked Atlantic Salmon', defaults={'serving_size': '180g', 'calories': 370, 'protein': 36.0, 'carbohydrates': 0.0, 'fat': 24.0})
    FoodItem.objects.get_or_create(meal=m3, name='Roasted Sweet Potato', defaults={'serving_size': '150g', 'calories': 130, 'protein': 2.0, 'carbohydrates': 30.0, 'fat': 0.5})

    diet2, _ = DietPlan.objects.get_or_create(
        name='Clean Fat Loss Deficit Plan',
        defaults={
            'plan_type': 'Weight Loss Diet',
            'target_calories': 1800,
            'target_protein': 140,
            'target_carbs': 160,
            'target_fat': 45,
            'description': 'Balanced volumetric meal strategy focusing on lean protein, fiber-dense vegetables, and sustained satiety.',
            'is_featured': True
        }
    )
    m4, _ = Meal.objects.get_or_create(diet_plan=diet2, meal_type='Breakfast', defaults={'name': 'Greek Yogurt Berry Bowl', 'timing': '08:30 AM'})
    FoodItem.objects.get_or_create(meal=m4, name='0% Fat Greek Yogurt', defaults={'serving_size': '200g', 'calories': 120, 'protein': 20.0, 'carbohydrates': 8.0, 'fat': 0.0})

    # 7. Challenges
    Challenge.objects.get_or_create(
        title='30-Day Fitness Revolution',
        defaults={
            'challenge_type': 'Workout',
            'duration_days': 30,
            'target_description': 'Complete 1 workout session daily for 30 consecutive days',
            'badge_name': '30-Day Master Champion',
            'badge_icon': 'fa-medal',
            'description': 'Build an unbreakable exercise habit with progressive daily sessions.'
        }
    )
    Challenge.objects.get_or_create(
        title='2.5L Daily Hydration Streak',
        defaults={
            'challenge_type': 'Hydration',
            'duration_days': 14,
            'target_description': 'Hit minimum 2,500ml water intake every single day',
            'badge_name': 'Hydration Hero Badge',
            'badge_icon': 'fa-droplet',
            'description': 'Keep muscle tissue primed, flush toxins, and supercharge recovery.'
        }
    )
    Challenge.objects.get_or_create(
        title='7-Day Core Ignite Sprint',
        defaults={
            'challenge_type': 'Workout',
            'duration_days': 7,
            'target_description': 'Perform a 10-minute abdominal & core routine every morning',
            'badge_name': 'Steel Abs Badge',
            'badge_icon': 'fa-fire-flame-curved',
            'description': 'Fortify your lower back, posture, and rotational core stability.'
        }
    )

    # 8. Feedbacks / Testimonials
    Feedback.objects.get_or_create(
        name='Sarah Jenkins',
        defaults={
            'role_or_title': 'Marathoner & Fitness Enthusiast',
            'rating': 5,
            'comment': 'Fitness Master transformed how I track my workouts and nutrition. The water tracker and calculators keep me accountable daily!',
            'is_featured': True
        }
    )
    Feedback.objects.get_or_create(
        name='Marcus Vance',
        defaults={
            'role_or_title': 'Bodybuilding Athlete',
            'rating': 5,
            'comment': 'The workout execution mode with sets and rest timers is incredible. Cleanest UI I have used for personal training.',
            'is_featured': True
        }
    )

    # 9. Contact Message
    ContactMessage.objects.get_or_create(
        email='alex.trainer@fitmail.com',
        defaults={
            'name': 'Alex Trainer',
            'subject': 'Inquiry about customized nutrition splits',
            'message': 'Hello Fitness Master team, I wanted to inquire about adding vegetarian high-protein meal options.',
            'is_read': False
        }
    )

    print("Initial seeding completed successfully!")


if __name__ == '__main__':
    seed()
