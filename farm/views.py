
from decimal import Decimal, InvalidOperation


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from farm.models import Profile, Crop, CropExpense, CropSale


# Create your views here.
# def my_crops(request):
#     return HttpResponse("welcome to my crops")




@login_required
@never_cache
def profile(request):
   profile, created = Profile.objects.get_or_create(
       user=request.user,
       defaults={
           'mobile': '',
           'village': '',
           'taluk': '',
           'district': '',
           'total_land_acres': Decimal('0.00'),
       }
   )


   if request.method == 'POST':
       email = request.POST.get('email', '').strip()
       mobile = request.POST.get('mobile', '').strip()
       village = request.POST.get('village', '').strip()
       taluk = request.POST.get('taluk', '').strip()
       district = request.POST.get('district', '').strip()
       total_land = request.POST.get('total_land_acres', '').strip()


       try:
           if not email:
               raise ValueError('Email is required.')


           if len(email) > 254 or '@' not in email:
               raise ValueError('Enter a valid email address.')


           land = Decimal(total_land)


           if not land.is_finite() or land < 0 or land > Decimal('9999.99'):
               raise ValueError('Enter land between 0 and 9999.99 acres.')


           if land.as_tuple().exponent < -2:
               raise ValueError('Land can have at most 2 decimal places.')


           request.user.email = email
           request.user.save(update_fields=['email'])


           profile.mobile = mobile
           profile.village = village
           profile.taluk = taluk
           profile.district = district
           profile.total_land_acres = land
           profile.save()


           messages.success(request, 'Profile updated successfully.')
           return redirect('profile')


       except (ValueError, InvalidOperation):
           messages.error(request, 'Please check your email and land details.')


   return render(request, 'profile.html', {'profile': profile})
@login_required
@never_cache
def crop_create_view(request):
    if request.method == 'POST':
        harvested_quantity = request.POST.get('harvested_quantity')
        Crop.objects.create(
            farmer=request.user,
            name=request.POST.get('name'),
            variety=request.POST.get('variety', ''),
            acres=request.POST.get('acres'),
            season=request.POST.get('season'),
            start_date=request.POST.get('start_date'),
            harvested_quantity=Decimal(str(harvested_quantity)) if harvested_quantity else 0,
            actual_harvest_date=request.POST.get('actual_harvest_date') or None,
            status=request.POST.get('status', 'Planned'),
            notes=request.POST.get('notes', '')
        )
        return redirect('my_crops')
    return render(request, 'crop_form.html', {'title': 'Add Crop'})
@login_required
@never_cache
def crop_list_view(request):
    crops = Crop.objects.filter(farmer=request.user)
    return render(request, 'crop_list.html', {'crops': crops})


@login_required
@never_cache
def crop_update_view(request, pk):
    crop = get_object_or_404(Crop, pk=pk, farmer=request.user)
    if request.method == 'POST':
        crop.name = request.POST.get('name')
        crop.variety = request.POST.get('variety', '')
        crop.acres = request.POST.get('acres')
        crop.season = request.POST.get('season')
        crop.start_date = request.POST.get('start_date')
        harvested_quantity = request.POST.get('harvested_quantity')
        crop.harvested_quantity = Decimal(str(harvested_quantity)) if harvested_quantity else 0
        crop.actual_harvest_date = request.POST.get('actual_harvest_date') or None
        crop.status = request.POST.get('status')
        crop.notes = request.POST.get('notes', '')
        crop.save()
        return redirect('my_crops',)
    return render(request, 'crop_form.html', {'crop': crop, 'title': 'Edit Crop'})


@login_required
@never_cache
def crop_delete_view(request, pk):
    crop = get_object_or_404(Crop, pk=pk, farmer=request.user)
    if request.method == 'POST':
        crop.delete()
        return redirect('my_crops',)
    return render(request, 'crop_confirm_delete.html', {'crop': crop})




@login_required
@never_cache
def crop_detail_view(request, pk):
    crop = get_object_or_404(Crop, pk=pk, farmer=request.user)
    expenses = crop.expenses.all()
    sales = crop.sales.all()

    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_revenue = sum([sale.sales_revenue for sale in sales])
    net_profit = total_revenue - total_expense

    context = {
        'crop': crop,
        'expenses': expenses,
        'sales': sales,
        'total_expense': total_expense,
        'total_revenue': total_revenue,
        'net_profit': net_profit,
    }
    return render(request, 'crop_detail.html', context)


@login_required
@never_cache
def expense_create_view(request, crop_pk):
    crop = get_object_or_404(Crop, pk=crop_pk, farmer=request.user)
    if request.method == 'POST':
        CropExpense.objects.create(
            crop=crop,
            expense_date=request.POST.get('expense_date'),
            category=request.POST.get('category'),
            amount=request.POST.get('amount'),
            description=request.POST.get('description', ''),
            quantity=request.POST.get('quantity', '')
        )
        return redirect('crop_detail', pk=crop.pk)
    return render(request, 'expense_form.html', {'crop': crop})



@login_required
@never_cache
def sale_create_view(request, crop_pk):
   crop = get_object_or_404(Crop, pk=crop_pk, farmer=request.user)


   if request.method == 'POST':
       quantity_sold = request.POST.get('quantity_sold')
       unit_price = request.POST.get('unit_price')


       quantity_sold_decimal = Decimal(str(quantity_sold)) if quantity_sold else Decimal('0')
       already_sold = crop.sales.aggregate(total=Sum('quantity_sold'))['total'] or Decimal('0')
       if already_sold + quantity_sold_decimal > crop.harvested_quantity:
           remaining = crop.harvested_quantity - already_sold
           messages.error(request, f"Cannot sell {quantity_sold_decimal} units. Only {remaining} units remain to sell from the harvested quantity ({crop.harvested_quantity} total).")
           return render(request, 'sale_form.html', {'crop': crop, 'remaining_quantity': remaining})


       unit_price_decimal = Decimal(str(unit_price)) if unit_price else Decimal('0')


       CropSale.objects.create(
           crop=crop,
           sale_date=request.POST.get('sale_date'),
           quantity_sold=quantity_sold_decimal,
           unit_price=unit_price_decimal,
       )
       return redirect('crop_detail', pk=crop.pk)


   remaining_quantity = crop.harvested_quantity - (crop.sales.aggregate(total=Sum('quantity_sold'))['total'] or Decimal('0'))
   return render(request, 'sale_form.html', {'crop': crop, 'remaining_quantity': remaining_quantity})


@login_required
@never_cache
def dashboard_view(request):
   crops = Crop.objects.filter(farmer=request.user)
   active_crops_count = crops.filter(status='Growing').count()
   total_acres = crops.aggregate(Sum('acres'))['acres__sum'] or 0


   total_investment = CropExpense.objects.filter(crop__farmer=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
   sales = CropSale.objects.filter(crop__farmer=request.user)
   total_sales = sum([sale.sales_revenue for sale in sales])
   total_profit = total_sales - total_investment


   context = {
       'active_crops_count': active_crops_count,
       'total_acres': total_acres,
       'total_investment': total_investment,
       'total_sales': total_sales,
       'total_profit': total_profit,
       'recent_crops': crops[:5]
   }
   return render(request, 'farmer_dashboard.html', context)


