from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from unicodedata import decimal


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile = models.CharField(max_length=15, default='')
    village = models.CharField(max_length=100, default='')
    taluk = models.CharField(max_length=100, default='')
    district = models.CharField(max_length=100, default='')
    total_land_acres = models.DecimalField(max_digits=6,decimal_places=2, default='0.00')

class Crop(models.Model):
   STATUS_CHOICES = [
       ('Planned', 'Planned'),
       ('Growing', 'Growing'),
       ('Harvested', 'Harvested'),
       ('Failed', 'Failed'),
   ]




   farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crops')
   name = models.CharField(max_length=100)
   variety = models.CharField(max_length=100, blank=True)
   acres = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.01)])
   season = models.CharField(max_length=50)
   start_date = models.DateField()
   harvested_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.0)])
   actual_harvest_date = models.DateField(null=True, blank=True)
   status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planned')
   notes = models.TextField(blank=True)




   def __str__(self):
       return f"{self.name} ({self.variety}) - {self.farmer.username}"



class CropExpense(models.Model):
    CATEGORY_CHOICES = [
        ('seeds', 'Seeds'),
        ('fertilizer', 'Fertilizer'),
        ('pesticides', 'Pesticides'),
        ('labour', 'Labour'),
        ('tractor', 'Tractor/Ploughing'),
        ('irrigation', 'Irrigation/Electricity'),
        ('equipment', 'Equipment Rental'),
        ('transport', 'Transport'),
        ('harvesting', 'Harvesting'),
        ('other', 'Other'),
    ]

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='expenses')
    expense_date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    description = models.TextField(blank=True)
    quantity = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.category} - {self.amount} for {self.crop.name}"





class CropSale(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='sales')
    sale_date = models.DateField()
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])

    @property
    def sales_revenue(self):
        quantity = Decimal(str(self.quantity_sold))
        unit_price = Decimal(str(self.unit_price))
        return quantity * unit_price

    def __str__(self):
        return f"Sale of {self.quantity_sold} from {self.crop.name}"

