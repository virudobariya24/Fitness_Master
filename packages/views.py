from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg
from django.contrib.auth import get_user_model
from accounts.models import User, ContactMessage
from .models import Packages
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
    # Ensure active admin session is not masked by old user portal session flag
    if 'is_user_authenticated' in request.session:
        request.session.pop('is_user_authenticated', None)

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
    Task (1): Detailed view page for a specific package.
    Retrieves package by primary key and renders package_detail.html
    displaying all 9 fields, Indian Rupee pricing, duration, and enrollment actions.
    Accessible to both authenticated admins, session-authenticated users, and visitors.
    """
    package = get_object_or_404(Packages, pk=pk)
    related_packages = Packages.objects.exclude(pk=pk).order_by('price')[:2]
    is_user_portal = bool(request.session.get('is_user_authenticated') or request.GET.get('portal') == 'user')
    return render(request, 'packages/package_detail.html', {
        'package': package,
        'related_packages': related_packages,
        'is_user_page': is_user_portal,
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
