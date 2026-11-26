from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from accounts.models import User
from packages.models import Packages, Order

AdminModel = get_user_model()


class UserModelAndOrderModelTests(TestCase):
    """
    Task (1): Tests for:
    - User model with name, email, password fields (PBKDF2 hashed)
    - Order model with necessary fields (user, package, order_number, package_title, package_price, etc.)
    """
    def setUp(self):
        self.user = User.objects.create(
            name="Viraj Dobariya",
            username="virajdobariya",
            email="viraj@example.com",
            password=make_password("Secret123")
        )
        self.package = Packages.objects.create(
            title="VIP Platinum Elite",
            price=1999.00,
            duration="12 Months",
            access_hours="24/7 Unlimited Access",
            instruments="Olympic Barbells, Cable Machines, Cardio Suite",
            classes_per_week="Unlimited Daily Classes",
            membership_duration="Annual",
            drinking_package="Unlimited Protein & Smoothies",
            personal_instructor="Dedicated 1-on-1 Master Trainer"
        )

    def test_user_model_fields(self):
        """User model contains name, email, password fields, with hashed password"""
        u = User.objects.get(username="virajdobariya")
        self.assertEqual(u.name, "Viraj Dobariya")
        self.assertEqual(u.email, "viraj@example.com")
        self.assertTrue(check_password("Secret123", u.password))
        self.assertNotEqual(u.password, "Secret123")
        self.assertEqual(str(u), f"{u.name} ({u.username}) - {u.email}")

    def test_order_model_creation_and_fields(self):
        """Order model records member package bookings with all required fields"""
        order = Order.objects.create(
            user=self.user,
            package=self.package,
            order_number="ORD-20261125-9999",
            package_title=self.package.title,
            package_price=self.package.price,
            package_duration=self.package.duration,
            status="Confirmed",
            payment_status="Paid",
            payment_method="UPI / Online Payment",
            notes="VIP Enrollment"
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.package, self.package)
        self.assertEqual(order.order_number, "ORD-20261125-9999")
        self.assertEqual(order.package_title, "VIP Platinum Elite")
        self.assertEqual(float(order.package_price), 1999.00)
        self.assertEqual(order.package_duration, "12 Months")
        self.assertEqual(order.status, "Confirmed")
        self.assertEqual(order.payment_status, "Paid")
        self.assertIn("ORD-20261125-9999", str(order))
        self.assertIn("VIP Platinum Elite", str(order))


class PackageDetailViewAllFieldsTests(TestCase):
    """
    Task (2): Detailed view for each fitness package with all 9 fields shown:
    1. title
    2. price (in ₹)
    3. duration
    4. access_hours
    5. instruments
    6. classes_per_week
    7. membership_duration
    8. drinking_package
    9. personal_instructor
    """
    def setUp(self):
        self.client = Client()
        self.package = Packages.objects.create(
            title="Premium Pro Fitness",
            price=1499.50,
            duration="3 Months",
            access_hours="5:00 AM - 11:00 PM Daily",
            instruments="Free Weights, Smith Machine, Treadmills, Rowers",
            classes_per_week="5 Classes/week (HIIT & Yoga)",
            membership_duration="Quarterly",
            drinking_package="Daily Fresh Electrolyte Water",
            personal_instructor="2 Dedicated Sessions / Month"
        )

    def test_package_detail_view_renders_all_9_fields(self):
        """Detailed view for package contains all 9 required fields and Indian Rupee ₹ pricing"""
        url = reverse('package_detail', kwargs={'pk': self.package.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # 1. Title
        self.assertContains(resp, "Premium Pro Fitness")
        # 2. Price in ₹
        self.assertContains(resp, "₹1499.50")
        # 3. Duration
        self.assertContains(resp, "3 Months")
        # 4. Access hours
        self.assertContains(resp, "5:00 AM - 11:00 PM Daily")
        # 5. Instruments
        self.assertContains(resp, "Free Weights, Smith Machine, Treadmills, Rowers")
        # 6. Classes per week
        self.assertContains(resp, "5 Classes/week (HIIT &amp; Yoga)")
        # 7. Membership duration
        self.assertContains(resp, "Quarterly")
        # 8. Drinking package
        self.assertContains(resp, "Daily Fresh Electrolyte Water")
        # 9. Personal instructor
        self.assertContains(resp, "2 Dedicated Sessions / Month")


class BookNowButtonVisibilityAndOrderFlowTests(TestCase):
    """
    Task (3):
    - 'Book Now' button visible ONLY if user is logged in
    - When unauthenticated: 'Book Now' button is not visible, 'Sign In to Book' prompt is shown
    - When authenticated: 'Book Now' button is visible with confirmation modal
    - Booking action creates Order and redirects to receipt
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            name="Viraj Dobariya",
            username="viraj",
            email="viraj@fitnessmaster.com",
            password=make_password("Viraj123")
        )
        self.package = Packages.objects.create(
            title="CrossFit Champion",
            price=899.00,
            duration="1 Month",
            access_hours="6:00 AM - 10:00 PM",
            instruments="Kettlebells, Battle Ropes, Plyo Boxes",
            classes_per_week="4 Classes/week",
            membership_duration="Monthly",
            drinking_package="Filtered Mineral Water",
            personal_instructor="Group Coach Included"
        )

    def test_book_now_button_hidden_when_user_unauthenticated(self):
        """Unauthenticated visitor does NOT see 'Book Now' button; sees 'Sign In to Book' instead"""
        url = reverse('package_detail', kwargs={'pk': self.package.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # 'Book Now' button must NOT be visible
        self.assertNotContains(resp, '<button type="button" class="btn btn-success fw-bold px-4 py-2.5 shadow-sm rounded-3 d-flex align-items-center gap-2" data-bs-toggle="modal" data-bs-target="#bookPackageModal"')
        # Prompt to sign in must be present
        self.assertContains(resp, "Sign In to Book")
        self.assertContains(resp, reverse('user_login'))

    def test_book_now_button_visible_when_user_authenticated(self):
        """Session-authenticated member DOES see 'Book Now' button and booking modal"""
        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('package_detail', kwargs={'pk': self.package.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # 'Book Now' button must be visible
        self.assertContains(resp, "Book Now")
        self.assertContains(resp, "data-bs-target=\"#bookPackageModal\"")
        # 'Sign In to Book' button must NOT be present
        self.assertNotContains(resp, "Sign In to Book")

    def test_package_book_view_requires_authentication(self):
        """Unauthenticated user booking request redirects to login"""
        url = reverse('package_book', kwargs={'pk': self.package.pk})
        resp = self.client.post(url, {'payment_method': 'UPI / Online Payment'})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('user_login'))

    def test_package_book_view_creates_order_and_redirects_to_receipt(self):
        """Authenticated member booking request creates Order in database and redirects to receipt"""
        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('package_book', kwargs={'pk': self.package.pk})
        resp = self.client.post(url, {
            'payment_method': 'UPI / Online Payment',
            'notes': 'Joining morning session'
        })
        self.assertEqual(resp.status_code, 302)

        # Order must exist in DB
        order = Order.objects.filter(user=self.user, package=self.package).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.package_title, "CrossFit Champion")
        self.assertEqual(float(order.package_price), 899.00)
        self.assertEqual(order.status, "Confirmed")
        self.assertEqual(order.payment_status, "Paid")
        self.assertEqual(order.payment_method, "UPI / Online Payment")
        self.assertTrue(order.order_number.startswith("ORD-"))

        # Redirects to order receipt
        self.assertRedirects(resp, reverse('user_order_detail', kwargs={'order_id': order.id}))

    def test_user_orders_view_lists_member_bookings(self):
        """Member can view all placed bookings on My Bookings page"""
        Order.objects.create(
            user=self.user,
            package=self.package,
            order_number="ORD-20261125-1111",
            package_title=self.package.title,
            package_price=self.package.price,
            package_duration=self.package.duration,
            status="Confirmed",
            payment_status="Paid"
        )
        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('user_orders')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ORD-20261125-1111")
        self.assertContains(resp, "CrossFit Champion")
        self.assertContains(resp, "₹899.00")

    def test_user_order_detail_view_shows_receipt(self):
        """Member can view detailed printable receipt for an order"""
        order = Order.objects.create(
            user=self.user,
            package=self.package,
            order_number="ORD-20261125-2222",
            package_title=self.package.title,
            package_price=self.package.price,
            package_duration=self.package.duration,
            status="Confirmed",
            payment_status="Paid"
        )
        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('user_order_detail', kwargs={'order_id': order.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ORD-20261125-2222")
        self.assertContains(resp, "Booking Confirmation &amp; Receipt")
        self.assertContains(resp, "Print Receipt")

    def test_admin_orders_list_view_accessible_by_admin(self):
        """Admin portal displays all member bookings with search and revenue"""
        admin = AdminModel.objects.create_superuser(
            username="AdminOrderTest",
            email="adminorder@test.com",
            password="AdminPassword123"
        )
        Order.objects.create(
            user=self.user,
            package=self.package,
            order_number="ORD-20261125-3333",
            package_title=self.package.title,
            package_price=self.package.price,
            package_duration=self.package.duration,
            status="Confirmed",
            payment_status="Paid"
        )

        self.client.login(username="AdminOrderTest", password="AdminPassword123")
        url = reverse('admin_orders')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ORD-20261125-3333")
        self.assertContains(resp, "CrossFit Champion")
        self.assertContains(resp, "₹899.0")

    def test_package_book_get_renders_booking_form_with_payment_modes(self):
        """GET /packages/<pk>/book/ renders dedicated booking form with Online & Cash payment options"""
        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('package_book', kwargs={'pk': self.package.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Confirm Package Booking")
        self.assertContains(resp, "CrossFit Champion")
        self.assertContains(resp, "Online Payment (Razorpay Payment Gateway)")
        self.assertContains(resp, "Cash on Arrival (Pay at Gym Reception Desk)")
        self.assertContains(resp, "rzp_test_RRohlnOxODtIQJ")

    def test_package_book_cash_payment_mode(self):
        """Booking with Cash on Arrival payment mode creates Confirmed order with Pending payment"""
        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('package_book', kwargs={'pk': self.package.pk})
        resp = self.client.post(url, {
            'payment_mode': 'cash',
            'notes': 'Will pay cash at reception tomorrow'
        })
        self.assertEqual(resp.status_code, 302)

        order = Order.objects.filter(user=self.user, package=self.package, payment_method='Cash (Pay at Gym Desk)').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'Confirmed')
        self.assertEqual(order.payment_status, 'Pending')
        self.assertRedirects(resp, reverse('user_order_detail', kwargs={'order_id': order.id}))

    def test_package_book_razorpay_create_order_ajax(self):
        """AJAX request to create Razorpay order returns JSON with razorpay_order_id and creates pending order"""
        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('package_book', kwargs={'pk': self.package.pk})
        resp = self.client.post(url, {
            'action': 'create_razorpay_order',
            'notes': 'Online payment test'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('razorpay_order_id', data)
        self.assertEqual(data['amount'], 89900)
        self.assertEqual(data['key'], 'rzp_test_RRohlnOxODtIQJ')

        # Pending order exists in DB
        order = Order.objects.filter(pk=data['order_id']).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'Pending')
        self.assertEqual(order.payment_status, 'Pending')
        self.assertEqual(order.payment_method, 'Online (Razorpay)')

    def test_razorpay_verify_payment_view_updates_order_to_paid(self):
        """Payment verification endpoint confirms order and marks payment as Paid"""
        order = Order.objects.create(
            user=self.user,
            package=self.package,
            order_number="ORD-20261126-RP999",
            package_title=self.package.title,
            package_price=self.package.price,
            package_duration=self.package.duration,
            status='Pending',
            payment_status='Pending',
            payment_method='Online (Razorpay)',
            razorpay_order_id='order_test_999'
        )

        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('razorpay_verify_payment')
        resp = self.client.post(url, {
            'order_id': order.id,
            'razorpay_order_id': 'order_test_999',
            'razorpay_payment_id': 'pay_test_999888',
            'razorpay_signature': 'mock_signature_abc'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')

        order.refresh_from_db()
        self.assertEqual(order.status, 'Confirmed')
        self.assertEqual(order.payment_status, 'Paid')
        self.assertEqual(order.razorpay_payment_id, 'pay_test_999888')

    def test_booking_confirmation_page_displays_summary(self):
        """Booking confirmation page displays complete order summary and details"""
        order = Order.objects.create(
            user=self.user,
            package=self.package,
            order_number="ORD-20261126-CONFIRM",
            package_title=self.package.title,
            package_price=self.package.price,
            package_duration=self.package.duration,
            status='Confirmed',
            payment_status='Paid',
            payment_method='Online (Razorpay)',
            razorpay_payment_id='pay_live_confirm_123'
        )

        session = self.client.session
        session['is_user_authenticated'] = True
        session['user_id'] = self.user.id
        session['user_username'] = self.user.username
        session.save()

        url = reverse('booking_confirmation', kwargs={'order_id': order.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ORD-20261126-CONFIRM")
        self.assertContains(resp, "CrossFit Champion")
        self.assertContains(resp, "Online (Razorpay)")
        self.assertContains(resp, "pay_live_confirm_123")
