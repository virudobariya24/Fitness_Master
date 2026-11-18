from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from workouts.models import WorkoutPlan, ExerciseCategory, Exercise, WorkoutLog
from nutrition.models import DietPlan
from challenges.models import Challenge, ChallengeProgress
from tracking.models import WaterLog, WeightLog
from core.models import ContactMessage

User = get_user_model()


class FitnessMasterComprehensiveTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Admin
        self.admin = User.objects.create_superuser(
            username='site_admin',
            email='admin@fitnessmaster.com',
            password='AdminPassword123!',
            role='ADMIN'
        )

        # Create Regular User
        self.user = User.objects.create_user(
            username='athlete_jane',
            email='jane@fitnessmaster.com',
            password='UserPassword123!',
            role='USER'
        )
        self.user.profile.fitness_goal = 'weight_loss'
        self.user.profile.current_weight = 65.0
        self.user.profile.target_weight = 58.0
        self.user.profile.height = 168.0
        self.user.profile.save()

        # Seed sample category & exercise
        self.cat = ExerciseCategory.objects.create(name='Strength', description='Resistance training')
        self.exercise = Exercise.objects.create(
            category=self.cat,
            name='Barbell Bench Press',
            target_muscle='Chest',
            difficulty='Intermediate',
            default_sets=4,
            default_reps='8-10 reps',
            instructions='Lower the bar to mid-chest with control and press up.'
        )

        # Seed sample workout plan
        self.workout_plan = WorkoutPlan.objects.create(
            title='Chest & Triceps Hypertrophy',
            goal='Muscle Building',
            difficulty_level='Intermediate',
            duration_weeks=6,
            days_per_week=4,
            estimated_calories_burn=420,
            is_featured=True
        )

        # Seed sample diet plan
        self.diet_plan = DietPlan.objects.create(
            name='Lean Definition Diet',
            plan_type='Weight Loss Diet',
            target_calories=1800,
            target_protein=150,
            target_carbs=160,
            target_fat=50,
            is_featured=True
        )

        # Seed sample challenge
        self.challenge = Challenge.objects.create(
            title='30-Day Fitness Challenge',
            challenge_type='Workout',
            duration_days=30,
            target_description='Complete 1 structured routine daily',
            badge_name='Iron Warrior'
        )

    # =========================================================================
    # 1. PUBLIC WEBSITE TESTS
    # =========================================================================
    def test_public_pages_render_successfully(self):
        """All public website pages should return 200 OK"""
        routes = [
            'home', 'about', 'programs', 'public_exercises', 'public_nutrition',
            'contact', 'bmi_calculator', 'calories_calculator',
            'login', 'register'
        ]
        for route in routes:
            resp = self.client.get(reverse(route))
            self.assertEqual(resp.status_code, 200, f"Route '{route}' failed with status {resp.status_code}")

    def test_contact_form_submission(self):
        """Public contact form should save message and redirect with success"""
        data = {
            'name': 'Mark Taylor',
            'email': 'mark@example.com',
            'phone': '1234567890',
            'subject': 'Inquiry regarding personal plans',
            'message': 'Hello, I would like more information on nutrition counseling.'
        }
        resp = self.client.post(reverse('contact'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ContactMessage.objects.filter(email='mark@example.com').exists())

    def test_bmi_calculator_renders_interactive_page(self):
        """BMI calculator renders with status 200 and interactive controls"""
        resp = self.client.get(reverse('bmi_calculator'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'BMI Calculator')
        self.assertContains(resp, 'bmiHeight')
        self.assertContains(resp, 'bmiWeight')

    def test_calories_calculator_renders_interactive_page(self):
        """Calories calculator renders with status 200 and formula controls"""
        resp = self.client.get(reverse('calories_calculator'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Daily Calorie')
        self.assertContains(resp, 'calAge')
        self.assertContains(resp, 'calGender')

    # =========================================================================
    # 2. AUTHENTICATION & SECURITY
    # =========================================================================
    def test_user_registration(self):
        """Registering a new athlete creates User, hashes password, redirects to login with empty profile"""
        reg_data = {
            'first_name': 'New',
            'last_name': 'Athlete',
            'email': 'newathlete@example.com',
            'password': 'SuperPassword789!',
            'confirm_password': 'SuperPassword789!',
        }
        resp = self.client.post(reverse('register'), reg_data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('login'))
        u = User.objects.get(email='newathlete@example.com')
        self.assertEqual(u.role, 'USER')
        self.assertTrue(check_password('SuperPassword789!', u.password))
        self.assertEqual(u.first_name, 'New')
        self.assertEqual(u.last_name, 'Athlete')
        # Profile metrics must remain empty by default
        self.assertIsNone(u.profile.height)
        self.assertIsNone(u.profile.current_weight)
        self.assertIsNone(u.profile.target_weight)
        self.assertIsNone(u.profile.age)
        self.assertEqual(u.profile.phone, '')
        self.assertEqual(u.profile.gender, '')
        self.assertEqual(u.profile.bio, '')

    def test_registration_to_login_to_dashboard_and_profile_fill(self):
        """Full flow: Register -> Redirects to Login -> Sign in -> User Dashboard -> Fill Profile"""
        reg_data = {
            'first_name': 'Karan',
            'last_name': 'Patel',
            'email': 'karan@example.com',
            'password': 'KaranPassword123!',
            'confirm_password': 'KaranPassword123!',
        }
        # 1. Register -> redirects to login
        reg_resp = self.client.post(reverse('register'), reg_data)
        self.assertEqual(reg_resp.status_code, 302)
        self.assertRedirects(reg_resp, reverse('login'))

        # 2. Login -> redirects to user dashboard
        login_resp = self.client.post(reverse('login'), {
            'username': 'karan@example.com',
            'password': 'KaranPassword123!'
        })
        self.assertEqual(login_resp.status_code, 302)
        self.assertRedirects(login_resp, reverse('user_dashboard'))

        # 3. Access Dashboard - verify no errors with empty metrics
        dash_resp = self.client.get(reverse('user_dashboard'))
        self.assertEqual(dash_resp.status_code, 200)

        # 4. Access Profile - fields are initially empty and contains Logout options
        profile_page = self.client.get(reverse('user_profile'))
        self.assertEqual(profile_page.status_code, 200)
        self.assertContains(profile_page, reverse('logout'))
        self.assertContains(profile_page, 'Log Out')

        # 5. Fill profile details
        update_data = {
            'first_name': 'Karan',
            'last_name': 'Patel',
            'phone': '9876543210',
            'gender': 'male',
            'age': 27,
            'height': 178.5,
            'current_weight': 74.0,
            'target_weight': 70.0,
            'fitness_goal': 'muscle_building',
            'activity_level': 'moderate',
            'daily_water_goal': 3000,
            'daily_calorie_goal': 2400,
            'bio': 'Focused on strength and stamina.',
        }
        save_resp = self.client.post(reverse('user_profile'), update_data)
        self.assertEqual(save_resp.status_code, 302)

        # 6. Verify profile saved
        u = User.objects.get(email='karan@example.com')
        self.assertEqual(float(u.profile.height), 178.5)
        self.assertEqual(float(u.profile.current_weight), 74.0)
        self.assertEqual(float(u.profile.target_weight), 70.0)
        self.assertEqual(u.profile.age, 27)
        self.assertEqual(u.profile.fitness_goal, 'muscle_building')

    def test_login_with_email_address(self):
        """User can log in using their email address instead of username"""
        resp = self.client.post(reverse('login'), {
            'username': 'jane@fitnessmaster.com',
            'password': 'UserPassword123!'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('user_dashboard'))

    def test_admin_viraj_login(self):
        """Admin Viraj can log in to custom admin panel using Viraj / Viraj123"""
        viraj = User.objects.create_superuser(
            username='Viraj',
            email='viraj@fitnessmaster.com',
            password='Viraj123',
            role='ADMIN'
        )
        resp = self.client.post(reverse('custom_admin_login'), {
            'username': 'Viraj',
            'password': 'Viraj123'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('admin_dashboard'))

    def test_user_login_and_logout(self):
        """Regular user logs in and is redirected to user panel"""
        resp = self.client.post(reverse('login'), {
            'username': 'athlete_jane',
            'password': 'UserPassword123!'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('user_dashboard'))

        # Logout
        resp_logout = self.client.get(reverse('logout'))
        self.assertEqual(resp_logout.status_code, 302)

    def test_unauthenticated_user_access_blocked(self):
        """Unauthenticated requests to user dashboard should redirect to login"""
        resp = self.client.get(reverse('user_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(reverse('login')))

    def test_non_admin_cannot_access_custom_admin(self):
        """Regular user attempting to access custom admin portal is denied and redirected to admin login"""
        self.client.login(username='athlete_jane', password='UserPassword123!')
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('custom_admin_login'))

    # =========================================================================
    # 3. USER PANEL MODULES
    # =========================================================================
    def test_user_panel_views_render(self):
        """All user dashboard tabs render with 200 OK for logged-in user"""
        self.client.login(username='athlete_jane', password='UserPassword123!')
        user_routes = [
            'user_dashboard', 'user_profile', 'user_workout_plans',
            'user_workout_history', 'user_exercise_library',
            'user_diet_plans', 'user_progress_overview',
            'user_water_tracker', 'user_weight_tracker',
            'user_challenges', 'user_achievements'
        ]
        for route in user_routes:
            resp = self.client.get(reverse(route))
            self.assertEqual(resp.status_code, 200, f"User route '{route}' failed with status {resp.status_code}")

    def test_interactive_water_logging(self):
        """Adding a glass increments user's daily water intake by 250ml"""
        self.client.login(username='athlete_jane', password='UserPassword123!')
        resp = self.client.post(reverse('user_water_tracker'), {'action': 'add_glass'})
        self.assertEqual(resp.status_code, 302)

        log = WaterLog.objects.filter(user=self.user).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.glasses, 1)
        self.assertEqual(log.amount_ml, 250)

    def test_weight_logging(self):
        """Logging a weight entry updates WeightLog and UserProfile"""
        self.client.login(username='athlete_jane', password='UserPassword123!')
        resp = self.client.post(reverse('user_weight_tracker'), {
            'weight': 64.2,
            'recorded_date': '2026-11-18',
            'notes': 'Consistent progression'
        })
        self.assertEqual(resp.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(float(self.user.profile.current_weight), 64.2)

    def test_challenge_enrollment_and_checkin(self):
        """User can enroll in a challenge and check in daily days"""
        self.client.login(username='athlete_jane', password='UserPassword123!')
        resp_join = self.client.post(reverse('user_join_challenge', args=[self.challenge.id]))
        self.assertEqual(resp_join.status_code, 302)

        prog = ChallengeProgress.objects.get(user=self.user, challenge=self.challenge)
        self.assertEqual(prog.days_completed, 0)

        # Check in day 1
        resp_check = self.client.post(reverse('user_checkin_challenge', args=[prog.id]))
        self.assertEqual(resp_check.status_code, 302)
        prog.refresh_from_db()
        self.assertEqual(prog.days_completed, 1)

    # =========================================================================
    # 4. CUSTOM ADMIN PANEL MODULES & CRUD
    # =========================================================================
    def test_admin_login_and_dashboard(self):
        """Admin logs into custom admin and accesses admin dashboard"""
        resp = self.client.post(reverse('custom_admin_login'), {
            'username': 'site_admin',
            'password': 'AdminPassword123!'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('admin_dashboard'))

        resp_dash = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp_dash.status_code, 200)
        self.assertContains(resp_dash, 'Registered Users')

    def test_admin_crud_views_render(self):
        """All custom admin management views respond with 200 OK for admin"""
        self.client.login(username='site_admin', password='AdminPassword123!')
        admin_routes = [
            'admin_dashboard', 'admin_users', 'admin_user_add',
            'admin_exercises', 'admin_exercise_add',
            'admin_workouts', 'admin_workout_add',
            'admin_diets', 'admin_diet_add',
            'admin_challenges', 'admin_challenge_add',
            'admin_messages', 'admin_analytics', 'admin_profile'
        ]
        for route in admin_routes:
            resp = self.client.get(reverse(route))
            self.assertEqual(resp.status_code, 200, f"Admin route '{route}' failed with status {resp.status_code}")

    def test_admin_block_and_unblock_user(self):
        """Admin can toggle block status of a regular user"""
        self.client.login(username='site_admin', password='AdminPassword123!')
        self.assertFalse(self.user.is_blocked)

        # Block user
        self.client.get(reverse('admin_user_toggle_block', args=[self.user.id]))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_blocked)

        # Unblock user
        self.client.get(reverse('admin_user_toggle_block', args=[self.user.id]))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_blocked)
