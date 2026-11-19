from django.db import models


class Packages(models.Model):
    """
    Task (4): Model named Packages with fields:
    - title: Package title (e.g. Basic Starter, Gold Pro, VIP Elite)
    - price: Price in currency (e.g. 49.99)
    - duration: Duration of package (e.g. 1 Month, 3 Months, 1 Year)
    - access_hours: Access hours allowed (e.g. 24/7 Access, 6:00 AM - 10:00 PM)
    - instruments: Equipment / Instruments available
    - classes_per_week: Group / specialized classes per week
    - membership_duration: Monthly / Quarterly / Semi-Annual / Annual
    - drinking_package: Free water / Energy drinks / Protein shakes included
    - personal_instructor: Dedicated personal trainer / coach included
    """
    title = models.CharField(
        max_length=150,
        verbose_name="Package Title",
        help_text="Title or name of the package"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Price",
        help_text="Package price"
    )
    duration = models.CharField(
        max_length=80,
        verbose_name="Duration",
        help_text="Duration (e.g. 1 Month, 3 Months, 6 Months, 1 Year)"
    )
    access_hours = models.CharField(
        max_length=120,
        verbose_name="Access Hours",
        help_text="Gym access hours (e.g. 24/7 Access, 6 AM - 10 PM)"
    )
    instruments = models.TextField(
        verbose_name="Instruments / Equipment",
        help_text="Equipment and instruments included with this package"
    )
    classes_per_week = models.CharField(
        max_length=80,
        verbose_name="Classes Per Week",
        help_text="Number of classes per week (e.g. 3 Classes/week, Unlimited)"
    )
    membership_duration = models.CharField(
        max_length=80,
        verbose_name="Membership Duration",
        help_text="Billing / commitment duration (e.g. Monthly, Quarterly, Annual)"
    )
    drinking_package = models.CharField(
        max_length=150,
        verbose_name="Drinking Package",
        help_text="Beverage benefits (e.g. Unlimited Mineral Water, Protein Shakes Included, None)"
    )
    personal_instructor = models.CharField(
        max_length=150,
        verbose_name="Personal Instructor",
        help_text="Trainer allocation (e.g. 1-on-1 Dedicated Trainer, 2 Free Sessions/Month, None)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"
        ordering = ['price']

    def __str__(self):
        return f"{self.title} (${self.price}) - {self.duration}"
