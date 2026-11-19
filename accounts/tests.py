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
