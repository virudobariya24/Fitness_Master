import random
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Sum
from django.contrib.auth import get_user_model
from accounts.models import User, ContactMessage
from .models import Packages, Order
from .forms import PackageForm

AdminModel = get_user_model()


def admin_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def admin_dashboard_view(request):
    """
    Task (6): Basic dashboard page that loads after admin login.
    Displays:
    - Welcome banner showing logged-in admin's username and email
    - Overview KPI cards (Total Packages, Average Price, Registered Admins)
    - Full Packages table with all required fields (Task 4)
    - Admin users list with link to Django Admin for manual admin addition (Task 2)
    - Form to add new package
    """
    packages = Packages.objects.all().order_by('price')
    total_packages = packages.count()
    avg_price = packages.aggregate(avg=Avg('price'))['avg'] or 0.0
    admins = AdminModel.objects.all().order_by('-date_joined')
    total_admins = admins.count()
    registered_users = User.objects.all().order_by('-created_at')
    total_registered_users = registered_users.count()
    recent_inquiries = ContactMessage.objects.all().order_by('-created_at')[:5]
    total_inquiries = ContactMessage.objects.count()
    unread_inquiries = ContactMessage.objects.filter(is_read=False).count()
    orders = Order.objects.all().order_by('-booking_date')
    total_orders = orders.count()
    total_revenue = orders.filter(payment_status='Paid').aggregate(total=Sum('package_price'))['total'] or 0.0

    form = PackageForm()

    context = {
        'packages': packages,
        'total_packages': total_packages,
        'avg_price': round(avg_price, 2),
        'admins': admins,
        'total_admins': total_admins,
        'registered_users': registered_users[:6],
        'total_registered_users': total_registered_users,
        'recent_inquiries': recent_inquiries,
        'total_inquiries': total_inquiries,
        'unread_inquiries': unread_inquiries,
        'orders': orders[:5],
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'form': form,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def packages_list_view(request):
    """
    Dedicated Page for Option 2: Packages Management.
    Lists all subscription packages with full details for all 9 fields.
    Includes search, filter, and modal to add new package.
    """
    search_query = request.GET.get('q', '').strip()
    packages = Packages.objects.all()

    if search_query:
        packages = packages.filter(title__icontains=search_query)

    packages = packages.order_by('price')
    total_packages = packages.count()
    avg_price = packages.aggregate(avg=Avg('price'))['avg'] or 0.0

    form = PackageForm()

    return render(request, 'packages/packages_list.html', {
        'packages': packages,
        'total_packages': total_packages,
        'avg_price': round(avg_price, 2),
        'form': form,
        'search_query': search_query,
    })


def packages_cards_view(request):
    """
    Task (1): Create a view that retrieves all available packages from the database.
    Task (2): Design a template to display packages in a card-based Bootstrap layout.
    """
    packages = Packages.objects.all().order_by('price')
    total_packages = packages.count()
    avg_price = packages.aggregate(avg=Avg('price'))['avg'] or 0.0
    form = PackageForm()

    is_user_portal = bool(request.session.get('is_user_authenticated') or request.GET.get('portal') == 'user')

    return render(request, 'packages/packages_cards.html', {
        'packages': packages,
        'total_packages': total_packages,
        'avg_price': round(avg_price, 2),
        'form': form,
        'is_user_page': is_user_portal,
    })


def package_detail_view(request, pk):
    """
    Task (2): Detailed view for each fitness package with all 9 fields shown:
    - title, price, duration, access_hours, instruments, classes_per_week,
      membership_duration, drinking_package, personal_instructor.
    Task (3): Adds a "Book Now" button visible ONLY if the member is logged in.
    """
    package = get_object_or_404(Packages, pk=pk)
    related_packages = Packages.objects.exclude(pk=pk).order_by('price')[:2]

    # Session authentication validation for gym members
    is_member_authenticated = bool(
        request.session.get('is_user_authenticated') and request.session.get('user_id')
    )
    is_admin_authenticated = bool(
        request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    )

    # Check if this user has already booked this package
    user_has_booked = False
    active_order = None
    if is_member_authenticated:
        user_id = request.session.get('user_id')
        active_order = Order.objects.filter(
            user_id=user_id,
            package=package,
            status__in=['Confirmed', 'Active']
        ).first()
        user_has_booked = bool(active_order)

    # When user requests portal=user or is a gym member, use the member/public layout
    is_user_portal = is_member_authenticated or bool(request.GET.get('portal') == 'user') or not is_admin_authenticated

    return render(request, 'packages/package_detail.html', {
        'package': package,
        'related_packages': related_packages,
        'is_user_page': is_user_portal,
        'is_member_authenticated': is_member_authenticated,
        'user_has_booked': user_has_booked,
        'active_order': active_order,
    })


def package_book_view(request, pk):
    """
    Task (3): Package Booking Action View.
    - Accessible only by authenticated gym members.
    - Validates member session, creates an Order record in database.
    - Sets unique reference order_number, snapshots package title, price, duration.
    - Redirects to booking confirmation / receipt page with success notification.
    """
    is_member_authenticated = bool(
        request.session.get('is_user_authenticated') and request.session.get('user_id')
    )
    if not is_member_authenticated:
        messages.warning(request, "Please sign in to your member account to book a fitness package.")
        return redirect('user_login')

    user_id = request.session.get('user_id')
    user = get_object_or_404(User, pk=user_id)
    package = get_object_or_404(Packages, pk=pk)

    if request.method == 'POST':
        # Generate unique order tracking number: ORD-YYYYMMDD-XXXX
        order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        payment_method = request.POST.get('payment_method', 'UPI / Online Payment')
        notes = request.POST.get('notes', '').strip()

        order = Order.objects.create(
            user=user,
            package=package,
            order_number=order_number,
            package_title=package.title,
            package_price=package.price,
            package_duration=package.duration,
            status='Confirmed',
            payment_status='Paid',
            payment_method=payment_method,
            notes=notes if notes else f"Enrolled in {package.title} ({package.duration})"
        )

        messages.success(
            request,
            f"🎉 Congratulations {user.name or user.username}! You have successfully booked the '{package.title}' package. Your order reference is #{order.order_number}."
        )
        return redirect('user_order_detail', order_id=order.id)

    return redirect('package_detail', pk=pk)


def user_orders_view(request):
    """
    Member Portal: My Bookings & Orders View.
    Lists all orders placed by the currently authenticated gym member.
    """
    is_member_authenticated = bool(
        request.session.get('is_user_authenticated') and request.session.get('user_id')
    )
    if not is_member_authenticated:
        messages.warning(request, "Please sign in to access your package bookings.")
        return redirect('user_login')

    user_id = request.session.get('user_id')
    user = get_object_or_404(User, pk=user_id)
    orders = Order.objects.filter(user=user).order_by('-booking_date')

    return render(request, 'accounts/user_orders.html', {
        'user': user,
        'orders': orders,
        'total_orders': orders.count(),
        'active_orders_count': orders.filter(status__in=['Confirmed', 'Active']).count(),
        'is_user_page': True,
    })


def user_order_detail_view(request, order_id):
    """
    Member Portal: Order Details & Printable Receipt View.
    Displays detailed invoice/receipt for a specific booking.
    """
    is_member_authenticated = bool(
        request.session.get('is_user_authenticated') and request.session.get('user_id')
    )
    if not is_member_authenticated:
        messages.warning(request, "Please sign in to view your booking receipt.")
        return redirect('user_login')

    user_id = request.session.get('user_id')
    order = get_object_or_404(Order, pk=order_id, user_id=user_id)

    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'is_user_page': True,
    })


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def admin_orders_list_view(request):
    """
    Admin Portal: Manage Package Booking Orders.
    Displays all member bookings with search, status filters, and revenue analytics.
    """
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    orders = Order.objects.all().select_related('user', 'package').order_by('-booking_date')

    if search_query:
        orders = orders.filter(
            order_number__icontains=search_query
        ) | orders.filter(
            user__username__icontains=search_query
        ) | orders.filter(
            user__email__icontains=search_query
        ) | orders.filter(
            package_title__icontains=search_query
        )

    if status_filter:
        orders = orders.filter(status=status_filter)

    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(payment_status='Paid').aggregate(total=Sum('package_price'))['total'] or 0.0

    return render(request, 'packages/admin_orders_list.html', {
        'orders': orders,
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'search_query': search_query,
        'status_filter': status_filter,
    })


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def package_add_view(request):
    """Create a new package"""
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'packages_list'
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            pkg = form.save()
            messages.success(request, f"Package '{pkg.title}' has been successfully created!")
            return redirect(next_url)
        else:
            messages.error(request, "Failed to create package. Please review the errors in the form.")
    return redirect(next_url)


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def package_edit_view(request, pk):
    """Edit an existing package"""
    package = get_object_or_404(Packages, pk=pk)
    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, f"Package '{package.title}' has been updated successfully!")
            return redirect('packages_list')
        else:
            messages.error(request, "Failed to update package. Please verify the inputs.")
    else:
        form = PackageForm(instance=package)

    return render(request, 'packages/package_edit.html', {
        'form': form,
        'package': package,
    })


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def package_delete_view(request, pk):
    """Delete a package"""
    package = get_object_or_404(Packages, pk=pk)
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'packages_list'
    if request.method == 'POST':
        title = package.title
        package.delete()
        messages.success(request, f"Package '{title}' was deleted successfully.")
    return redirect(next_url)
