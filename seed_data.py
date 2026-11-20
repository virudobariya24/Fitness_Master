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

    # 2. Reset and Insert exactly 3 Dummy Packages (Task 4)
    print("\n🧹 Removing any old/extra packages...")
    deleted_count, _ = Packages.objects.all().delete()
    print(f"🗑️ Removed {deleted_count} old package(s).")

    packages_data = [
        {
            'title': 'Silver Fitness Package',
            'price': 1499.00,
            'duration': '1 Month',
            'access_hours': '6:00 AM - 10:00 PM',
            'instruments': 'Cardio Machines, Basic Dumbbells, Free Weights, and Stretching Area',
            'classes_per_week': '2 Classes / Week',
            'membership_duration': 'Monthly',
            'drinking_package': 'Filtered Mineral Water Station Included',
            'personal_instructor': 'General Floor Fitness Coach Support',
        },
        {
            'title': 'Gold Pro Package',
            'price': 2999.00,
            'duration': '3 Months',
            'access_hours': '5:00 AM - 11:00 PM',
            'instruments': 'Cardio Zone, Olympic Lifting Platforms, Squat Racks, Resistance Machines, Kettlebells',
            'classes_per_week': '4 Classes / Week',
            'membership_duration': 'Quarterly',
            'drinking_package': 'Hydration Bar + BCAA Energy Drinks Included',
            'personal_instructor': '2 Personal Trainer Sessions / Month',
        },
        {
            'title': 'Platinum Elite Package',
            'price': 4999.00,
            'duration': '6 Months',
            'access_hours': '24/7 Unlimited VIP Access',
            'instruments': 'Complete Pro Equipment Floor, Crossfit Rig, Steam Room, Sauna & Recovery Zone',
            'classes_per_week': 'Unlimited Classes (HIIT, Yoga, Zumba, CrossFit)',
            'membership_duration': 'Semi-Annual',
            'drinking_package': 'Unlimited Premium Protein Shakes & Fresh Juice Bar',
            'personal_instructor': 'Dedicated Certified Personal Instructor Weekly',
        },
    ]

    for pdata in packages_data:
        pkg = Packages.objects.create(**pdata)
        print(f"📦 Added Package: {pkg.title} (₹{pkg.price})")

    print("\n🎉 Database Seeding Completed Successfully!")
    print(f"Total Admins: {AdminModel.objects.count()}")
    print(f"Total Packages: {Packages.objects.count()}")


if __name__ == '__main__':
    seed_database()
