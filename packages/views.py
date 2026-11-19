from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg
from django.contrib.auth import get_user_model
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
    packages = Packages.objects.all().order_by('price')
    total_packages = packages.count()
    avg_price = packages.aggregate(avg=Avg('price'))['avg'] or 0.0
    admins = AdminModel.objects.all().order_by('-date_joined')
    total_admins = admins.count()

    form = PackageForm()

    context = {
        'packages': packages,
        'total_packages': total_packages,
        'avg_price': round(avg_price, 2),
        'admins': admins,
        'total_admins': total_admins,
        'form': form,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def package_add_view(request):
    """Create a new package"""
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            pkg = form.save()
            messages.success(request, f"Package '{pkg.title}' has been successfully created!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Failed to create package. Please review the errors in the form.")
    return redirect('admin_dashboard')


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
            return redirect('admin_dashboard')
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
    if request.method == 'POST':
        title = package.title
        package.delete()
        messages.success(request, f"Package '{title}' was deleted successfully.")
    return redirect('admin_dashboard')
