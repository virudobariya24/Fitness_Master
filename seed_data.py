import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitnessMaster.settings')
django.setup()

from django.contrib.auth import get_user_model
from packages.models import Packages

AdminModel = get_user_model()


def seed_database():
    print("=" * 60)
    print("🌱 SEEDING FITNESS MASTER: ADMIN USER & PACKAGES MODEL")
    print("=" * 60)

    # 1. Create/Ensure Fixed Admin User 'Viraj' (Task 1 & 2)
    admin_user = AdminModel.objects.filter(username__iexact='Viraj').first()
    if not admin_user:
        admin_user = AdminModel.objects.create_superuser(
            username='Viraj',
            email='viraj@fitnessmaster.com',
            password='Viraj123',
            first_name='Viraj',
            last_name='Dobariya'
        )
        print("✅ Created Fixed Admin user: Viraj / Viraj123 (viraj@fitnessmaster.com)")
    else:
        admin_user.set_password('Viraj123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.email = 'viraj@fitnessmaster.com'
        admin_user.save()
        print("✅ Updated Fixed Admin user: Viraj / Viraj123")

    # 2. Seed Default Packages (Task 4)
    packages_data = [
        {
            'title': 'Starter Fitness Pass',
            'price': 1499.00,
            'duration': '1 Month',
            'access_hours': '6:00 AM - 10:00 PM',
            'instruments': 'All Cardio Machines (Treadmills, Rowers, Ellipticals) and Basic Dumbbells & Barbells.',
            'classes_per_week': '2 Classes / Week',
            'membership_duration': 'Monthly',
            'drinking_package': 'Filtered Mineral Water Station Included',
            'personal_instructor': 'General Floor Fitness Coach Support',
        },
        {
            'title': 'Silver Strength & Conditioning',
            'price': 2999.00,
            'duration': '3 Months',
            'access_hours': '24/7 Unlimited Access',
            'instruments': 'Cardio Zone, Olympic Lifting Platforms, Squat Racks, Resistance Machines, Kettlebells.',
            'classes_per_week': '4 Classes / Week',
            'membership_duration': 'Quarterly',
            'drinking_package': 'Hydration Bar + BCAA Energy Drinks Included',
            'personal_instructor': '2 Free 1-on-1 Personal Trainer Sessions / Month',
        },
        {
            'title': 'Gold Pro Athlete Membership',
            'price': 4999.00,
            'duration': '6 Months',
            'access_hours': '24/7 VIP Access',
            'instruments': 'Full Gym Floor, Functional Turf, Crossfit Rig, Recovery Compression Boots & Infrared Sauna.',
            'classes_per_week': 'Unlimited Classes (HIIT, Spin, Yoga, Crossfit)',
            'membership_duration': 'Semi-Annual',
            'drinking_package': 'Unlimited Premium Protein Shakes & Fresh Juice Bar',
            'personal_instructor': 'Dedicated 1-on-1 Certified Personal Instructor Weekly',
        },
        {
            'title': 'Diamond VIP Elite Master',
            'price': 8999.00,
            'duration': '12 Months',
            'access_hours': '24/7 Priority VIP Access All Locations',
            'instruments': 'Complete Pro Equipment, Private Studio Access, Hydro-Massage Beds, Cold Plunge & Sauna.',
            'classes_per_week': 'Unlimited All Inclusive & Priority Booking',
            'membership_duration': 'Annual',
            'drinking_package': 'All-Access Unlimited Nutrition & Hydration Bar',
            'personal_instructor': 'Full-Time Master Coach & Dedicated Nutritionist',
        },
    ]

    for pdata in packages_data:
        pkg, created = Packages.objects.update_or_create(
            title=pdata['title'],
            defaults=pdata
        )
        if created:
            print(f"📦 Created Package: {pkg.title} (₹{pkg.price})")
        else:
            print(f"📦 Updated Package: {pkg.title} (₹{pkg.price})")

    print("\n🎉 Database Seeding Completed Successfully!")
    print(f"Total Admins: {AdminModel.objects.count()}")
    print(f"Total Packages: {Packages.objects.count()}")


if __name__ == '__main__':
    seed_database()
