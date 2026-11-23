from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from packages.models import Packages

AdminModel = get_user_model()


class FitnessMaster6TasksTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Task (2): Create Admin user with username, password, email
        self.admin = AdminModel.objects.create_superuser(
            username='Viraj',
            email='viraj@fitnessmaster.com',
            password='Viraj123',
            first_name='Viraj',
            last_name='Dobariya'
        )

        # Task (4): Create sample package
        self.package = Packages.objects.create(
            title='Gold Pro Membership',
            price=79.99,
            duration='6 Months',
            access_hours='24/7 Access',
            instruments='All Cardio & Strength Equipment',
            classes_per_week='Unlimited',
            membership_duration='Semi-Annual',
            drinking_package='Unlimited Protein Shakes',
            personal_instructor='Dedicated Certified Trainer'
        )

    # =========================================================================
    # TASK 1: Admin Login/Logout Functionality using Django Authentication
    # =========================================================================
    def test_admin_login_with_valid_credentials(self):
        """Admin can log in using Django authentication system and is redirected to dashboard"""
        resp = self.client.post(reverse('login'), {
            'username': 'Viraj',
            'password': 'Viraj123'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('admin_dashboard'))

    def test_admin_login_with_email_address(self):
        """Admin can log in using email address and password"""
        resp = self.client.post(reverse('login'), {
            'username': 'viraj@fitnessmaster.com',
            'password': 'Viraj123'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('admin_dashboard'))

    def test_admin_login_fails_with_invalid_credentials(self):
        """Invalid credentials show error and remain on login page"""
        resp = self.client.post(reverse('login'), {
            'username': 'Viraj',
            'password': 'WrongPassword999'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Invalid admin credentials")

    def test_admin_logout(self):
        """Logging out terminates session and redirects to login page"""
        self.client.login(username='Viraj', password='Viraj123')
        resp = self.client.get(reverse('logout'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('login'))

    # =========================================================================
    # TASK 2: Admin Model with username, password (hashed), and email
    # =========================================================================
    def test_admin_model_fields_and_password_hashing(self):
        """Admin model has username, email, and securely hashed password"""
        admin_user = AdminModel.objects.get(username='Viraj')
        self.assertEqual(admin_user.username, 'Viraj')
        self.assertEqual(admin_user.email, 'viraj@fitnessmaster.com')
        # Ensure password is not plain text and is properly hashed
        self.assertNotEqual(admin_user.password, 'Viraj123')
        self.assertTrue(check_password('Viraj123', admin_user.password))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    # =========================================================================
    # TASK 3: Basic Settings Configured
    # =========================================================================
    def test_basic_settings_configuration(self):
        """Settings configure apps, static, media, and auth user model"""
        from django.conf import settings
        self.assertEqual(settings.AUTH_USER_MODEL, 'accounts.Admin')
        self.assertIn('packages.apps.PackagesConfig', settings.INSTALLED_APPS)
        self.assertIn('accounts.apps.AccountsConfig', settings.INSTALLED_APPS)
        self.assertTrue(settings.STATIC_URL)
        self.assertTrue(settings.MEDIA_URL)

    # =========================================================================
    # TASK 4: Packages Model with all 9 required fields
    # =========================================================================
    def test_packages_model_all_fields(self):
        """Packages model contains all 9 required fields and saves correctly"""
        pkg = Packages.objects.get(id=self.package.id)
        self.assertEqual(pkg.title, 'Gold Pro Membership')
        self.assertEqual(float(pkg.price), 79.99)
        self.assertEqual(pkg.duration, '6 Months')
        self.assertEqual(pkg.access_hours, '24/7 Access')
        self.assertEqual(pkg.instruments, 'All Cardio & Strength Equipment')
        self.assertEqual(pkg.classes_per_week, 'Unlimited')
        self.assertEqual(pkg.membership_duration, 'Semi-Annual')
        self.assertEqual(pkg.drinking_package, 'Unlimited Protein Shakes')
        self.assertEqual(pkg.personal_instructor, 'Dedicated Certified Trainer')

    # =========================================================================
    # TASK 5 & 6: Bootstrap Dashboard that loads after admin login
    # =========================================================================
    def test_dashboard_loads_after_admin_login(self):
        """Dashboard page loads with status 200 after admin login with Bootstrap UI"""
        self.client.login(username='Viraj', password='Viraj123')
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 200)
        # Verify Bootstrap layout & elements
        self.assertContains(resp, 'bootstrap.min.css')
        self.assertContains(resp, 'bootstrap.bundle.min.js')
        self.assertContains(resp, 'Admin Dashboard')
        self.assertContains(resp, 'Welcome Back, Administrator Viraj!')
        # Verify Packages table
        self.assertContains(resp, 'Gold Pro Membership')
        self.assertContains(resp, '₹79.99')
        self.assertContains(resp, '24/7 Access')
        self.assertContains(resp, 'Unlimited Protein Shakes')
        # Verify Admin accounts table
        self.assertContains(resp, 'viraj@fitnessmaster.com')

    def test_unauthenticated_user_cannot_access_dashboard(self):
        """Unauthenticated user is redirected to login page"""
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('admin_dashboard')}")

    def test_package_crud_operations(self):
        """Admin can add, edit, and delete packages from the dashboard"""
        self.client.login(username='Viraj', password='Viraj123')

        # 1. Add Package
        new_data = {
            'title': 'Starter Gym Pass',
            'price': 24.99,
            'duration': '1 Month',
            'access_hours': '6 AM - 10 PM',
            'instruments': 'Cardio and Free weights',
            'classes_per_week': '2 Classes/week',
            'membership_duration': 'Monthly',
            'drinking_package': 'Water station',
            'personal_instructor': 'None',
        }
        add_resp = self.client.post(reverse('package_add'), new_data)
        self.assertEqual(add_resp.status_code, 302)
        self.assertTrue(Packages.objects.filter(title='Starter Gym Pass').exists())

        # 2. Edit Package
        pkg = Packages.objects.get(title='Starter Gym Pass')
        new_data['title'] = 'Starter Gym Pass Deluxe'
        new_data['price'] = 29.99
        edit_resp = self.client.post(reverse('package_edit', args=[pkg.id]), new_data)
        self.assertEqual(edit_resp.status_code, 302)
        pkg.refresh_from_db()
        self.assertEqual(pkg.title, 'Starter Gym Pass Deluxe')
        self.assertEqual(float(pkg.price), 29.99)

        # 3. Delete Package
        del_resp = self.client.post(reverse('package_delete', args=[pkg.id]))
        self.assertEqual(del_resp.status_code, 302)
        self.assertFalse(Packages.objects.filter(id=pkg.id).exists())

    def test_django_admin_site_accessible(self):
        """Django admin site is accessible for manually adding admin users"""
        self.client.login(username='Viraj', password='Viraj123')
        resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Admins')
        self.assertContains(resp, 'Packages')

    # =========================================================================
    # INDIVIDUAL SIDEBAR PAGES TESTS
    # =========================================================================
    def test_packages_list_individual_page(self):
        """Dedicated Packages Management page loads with status 200 and displays catalog"""
        self.client.login(username='Viraj', password='Viraj123')
        resp = self.client.get(reverse('packages_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Packages Management')
        self.assertContains(resp, 'Gold Pro Membership')
        self.assertContains(resp, '₹79.99')

    def test_admin_accounts_individual_page(self):
        """Dedicated Admin Accounts page loads with status 200 and displays admins list"""
        self.client.login(username='Viraj', password='Viraj123')
        resp = self.client.get(reverse('admin_accounts'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Admin Accounts Management')
        self.assertContains(resp, 'Viraj')
        self.assertContains(resp, 'viraj@fitnessmaster.com')

    def test_create_admin_from_individual_page(self):
        """Admin can create another admin user with hashed password from the dedicated page"""
        self.client.login(username='Viraj', password='Viraj123')
        resp = self.client.post(reverse('admin_accounts'), {
            'username': 'RahulAdmin',
            'email': 'rahul@fitnessmaster.com',
            'password': 'RahulPassword123',
            'confirm_password': 'RahulPassword123',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(AdminModel.objects.filter(username='RahulAdmin').exists())
        new_admin = AdminModel.objects.get(username='RahulAdmin')
        self.assertTrue(check_password('RahulPassword123', new_admin.password))
        self.assertTrue(new_admin.is_staff)

    # =========================================================================
    # TASK 1 & 2: CARD-BASED BOOTSTRAP PACKAGES VIEW TESTS
    # =========================================================================
    def test_packages_cards_view_authenticated(self):
        """Card view retrieves all packages from DB and renders in card-based Bootstrap layout"""
        self.client.login(username='Viraj', password='Viraj123')
        resp = self.client.get(reverse('packages_cards'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fitness Packages (1 Box per Package)')
        self.assertContains(resp, 'Gold Pro Membership')
        self.assertContains(resp, '₹79.99')
        self.assertContains(resp, 'card h-100')

    def test_packages_cards_view_unauthenticated(self):
        """Card view renders public card-based Bootstrap layout for visitors"""
        resp = self.client.get(reverse('packages_cards'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fitness Master Packages')
        self.assertContains(resp, 'Gold Pro Membership')
        self.assertContains(resp, '₹79.99')

    # =========================================================================
    # NEW TASK 1: "View More" Button on Each Card & Detailed View Page
    # =========================================================================
    def test_package_detail_view_authenticated(self):
        """Package detailed view page displays full specifications for authenticated admin"""
        self.client.login(username='Viraj', password='Viraj123')
        detail_url = reverse('package_detail', args=[self.package.pk])
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Gold Pro Membership')
        self.assertContains(resp, '₹79.99')
        self.assertContains(resp, '24/7 Access')
        self.assertContains(resp, 'Unlimited Protein Shakes')
        self.assertContains(resp, 'Dedicated Certified Trainer')
        self.assertContains(resp, 'Cardio')
        self.assertContains(resp, 'Edit Plan')

    def test_package_detail_view_unauthenticated(self):
        """Package detailed view page displays full specifications for visitor / session user"""
        detail_url = reverse('package_detail', args=[self.package.pk])
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Gold Pro Membership')
        self.assertContains(resp, '₹79.99')
        self.assertContains(resp, 'Plan Specifications')
        self.assertContains(resp, '24/7 Access')

    def test_cards_and_dashboard_contain_view_more_buttons(self):
        """Verify 'View More' buttons linking to package_detail exist on package cards and dashboard"""
        self.client.login(username='Viraj', password='Viraj123')
        detail_url = reverse('package_detail', args=[self.package.pk])

        # 1. Packages Cards Page
        resp_cards = self.client.get(reverse('packages_cards'))
        self.assertContains(resp_cards, detail_url)
        self.assertContains(resp_cards, 'View More')

        # 2. Dashboard Page
        resp_dash = self.client.get(reverse('admin_dashboard'))
        self.assertContains(resp_dash, detail_url)
        self.assertContains(resp_dash, 'View More')

        # 3. Dedicated Packages List Page
        resp_list = self.client.get(reverse('packages_list'))
        self.assertContains(resp_list, detail_url)
        self.assertContains(resp_list, 'View More')

    # =========================================================================
    # NEW TASK 2: Custom User Model with Name, Email, Password & Registration
    # =========================================================================
    def test_custom_user_model_creation_and_hashing(self):
        """Custom User model saves name, email, username and securely hashes password"""
        from accounts.models import User
        user = User.objects.create(
            name='Aarav Patel',
            username='aarav',
            email='aarav@example.com'
        )
        user.set_password('SecretUserPass123')
        user.save()

        saved_user = User.objects.get(username='aarav')
        self.assertEqual(saved_user.name, 'Aarav Patel')
        self.assertEqual(saved_user.email, 'aarav@example.com')
        self.assertNotEqual(saved_user.password, 'SecretUserPass123')
        self.assertTrue(saved_user.check_password('SecretUserPass123'))
        self.assertFalse(saved_user.check_password('WrongPass'))

    def test_user_registration_view_success(self):
        """User registration form successfully creates user in custom User model"""
        from accounts.models import User
        resp = self.client.post(reverse('user_register'), {
            'name': 'Pooja Sharma',
            'username': 'poojafit',
            'email': 'pooja@fitnessmaster.com',
            'password': 'PoojaPassword123',
            'confirm_password': 'PoojaPassword123',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('user_login'))
        self.assertTrue(User.objects.filter(username='poojafit').exists())

        new_user = User.objects.get(username='poojafit')
        self.assertEqual(new_user.email, 'pooja@fitnessmaster.com')
        self.assertTrue(new_user.check_password('PoojaPassword123'))

    def test_user_registration_duplicate_username_fails(self):
        """Registration with existing username returns validation error"""
        from accounts.models import User
        User.objects.create(username='existinguser', email='exist@example.com', password='hashedpassword')

        resp = self.client.post(reverse('user_register'), {
            'username': 'existinguser',
            'email': 'different@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'This username is already taken')

    # =========================================================================
    # NEW TASK 3: User Login / Logout Functionality Using Django Sessions
    # =========================================================================
    def test_user_session_login_and_logout(self):
        """User can log in using Django sessions and log out successfully"""
        from accounts.models import User
        user = User.objects.create(
            name='Kavya Joshi',
            username='kavyaj',
            email='kavya@example.com'
        )
        user.set_password('KavyaPass456')
        user.save()

        # 1. Login with valid credentials
        resp_login = self.client.post(reverse('user_login'), {
            'username': 'kavyaj',
            'password': 'KavyaPass456'
        })
        self.assertEqual(resp_login.status_code, 302)
        self.assertRedirects(resp_login, reverse('user_dashboard'))

        # Check Django session keys
        session = self.client.session
        self.assertTrue(session.get('is_user_authenticated'))
        self.assertEqual(session.get('user_id'), user.id)
        self.assertEqual(session.get('user_username'), 'kavyaj')

        # 2. Access User Dashboard with session
        resp_dash = self.client.get(reverse('user_dashboard'))
        self.assertEqual(resp_dash.status_code, 200)
        self.assertContains(resp_dash, 'Kavya Joshi')
        self.assertContains(resp_dash, 'Gold Pro Membership')
        self.assertContains(resp_dash, 'View More Details')

        # 3. Logout terminates session
        resp_logout = self.client.get(reverse('user_logout'))
        self.assertEqual(resp_logout.status_code, 302)
        self.assertRedirects(resp_logout, reverse('user_login'))

        session = self.client.session
        self.assertIsNone(session.get('is_user_authenticated'))
        self.assertIsNone(session.get('user_id'))

    def test_user_dashboard_unauthenticated_session_redirects(self):
        """User dashboard requires active Django session; redirects unauthenticated visitors"""
        resp = self.client.get(reverse('user_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('user_login'))

