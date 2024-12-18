from django.shortcuts import render, get_object_or_404,redirect
from orders.models import Order, OrderedFood
from vendor.models import Vendor
from vendor.forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from accounts.views import check_role_vendor
from menu.models import Category,FoodItem
from .utils import get_vendor
from menu.forms import CategoryForm, FoodItemForm
from django.utils.text import slugify




# Create your views here.
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
  profile = get_object_or_404(UserProfile,user=request.user)
  vendor = get_object_or_404(Vendor, user=request.user)

  if request.method == 'POST':
    profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
    vendor_form = VendorForm(request.POST,request.FILES,instance=vendor)
    if profile_form.is_valid() and vendor_form.is_valid():
      profile_form.save()
      vendor_form.save()
      messages.success(request,'Profile updated.')
      return redirect('vprofile')
    else:
      print(profile_form.errors)
      print(vendor_form.errors)
  else:
    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)
  context={
    'profile_form':profile_form,
    'vendor_form':vendor_form,
    'profile':profile,
    'vendor':vendor
    }
  return render(request,'vendor/vprofile.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
  vendor = get_vendor(request)
  categories = Category.objects.filter(vendor=vendor).order_by("created_at")

  context={
    'categories':categories,
  }
  return render(request,"vendor/menu_builder.html", context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request,pk=None):
  vendor = vendor = get_vendor(request)
  category = get_object_or_404(Category, pk = pk)
  fooditems = FoodItem.objects.filter(vendor=vendor,category=category)
  # print(fooditems)
  context = {
    'category':category,
    'fooditems':fooditems,
  }
  return render(request,"vendor/fooditems_by_category.html",context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category  = form.save(commit=False)
      category.vendor= get_vendor(request)
      category.save()
      category.slug = slugify(category_name)+'-'+str(category.id)
      category.save()
      messages.success(request,"Category Added Successfully.")
      return redirect("menu_builder")
    else:
      print(form.errors)
  else:
    form = CategoryForm()
  context={
    'form':form
  }
  return render(request,"vendor/add_category.html",context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request,id=None):
  category  = get_object_or_404(Category,pk=id)
  if request.method == 'POST':
    form = CategoryForm(request.POST,instance=category)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category  = form.save(commit=False)
      category.vendor= get_vendor(request)
      category.slug = slugify(category_name)+'-'+str(category.id)
      category.save() #here category id will be generated
      messages.success(request,"Category Updated Successfully.")
      return redirect("menu_builder")
    else:
      print(form.errors)
  else:
    form = CategoryForm(instance=category)
  context={
    'form':form,
    'category':category
  }
  return render(request,"vendor/edit_category.html",context)
  


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request,id=None):
  vendor =  get_vendor(request)
  category = get_object_or_404(Category, pk = id)
  category.delete()
  messages.success(request,"Category Deleted Successfully.")
  return redirect("menu_builder")


# food crud
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
  vendor = get_vendor(request)
  # category = get_object_or_404(Category,pk=id)
  if request.method == 'POST':
    form = FoodItemForm(request.POST,request.FILES)
    if form.is_valid():
      food_title = form.cleaned_data['food_title']
      food = form.save(commit=False)
      food.vendor = vendor
      food.save()
      # print(food.id)  #here we will get food id
      food.slug = slugify(food_title)+"-"+str(food.id)
      food.save()
      messages.success(request,'Food has been added successfully.')
      return redirect("fooditems_by_category",food.category.id)
    else:
      print(form.errors)
  else:
    form = FoodItemForm()
    # modify this form
    form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
  context={
    'form':form,
  }
  return render(request,"vendor/add_food.html",context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request,id=None):
  food = get_object_or_404(FoodItem,pk=id)
  if request.method == 'POST':
    form = FoodItemForm(request.POST,request.FILES,instance=food)
    if form.is_valid():
      food_title = form.cleaned_data['food_title']
      food = form.save(commit=False)
      food.vendor = get_vendor(request)
      food.save()
      food.slug = slugify(food_title)+"-"+str(food.id)
      food.save()
      messages.success(request,'Food has been updated successfully.')
      return redirect("fooditems_by_category",food.category.id)
    else:
      print(form.errors)
  else:
    form = FoodItemForm(instance=food)
    # modify the form
    form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

  context={
    'form':form,
    'food':food
  }
  return render(request,"vendor/edit_food.html",context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request,id):
  vendor = get_vendor(request)
  food = get_object_or_404(FoodItem, pk = id)
  food.delete()
  messages.success(request,"Food Item Deleted Successfully.")
  return redirect("fooditems_by_category",food.category.id)




def order_detail(request, order_number=None):
  context={}
  try:
    order = Order.objects.get(order_number = order_number, is_ordered = True)
    ordered_food = OrderedFood.objects.filter(order=order,fooditem__vendor = get_vendor(request))
    # print(order)
    
  except Exception as e:
    print(e)
    return redirect("vendor")
  # vendor = Vendor.objects.get(user=request.user)
  # order = Order.objects.filter(vendor=vendor)
  context['order'] = order
  context['ordered_food'] = ordered_food
  context['subtotal'] = order.get_total_by_vendor()['subtotal']
  context['tax_dict'] = order.get_total_by_vendor()['tax_dict']
  context['grand_total'] = order.get_total_by_vendor()['grand_total']
  return render(request,"vendor/order_detail.html",context)

def vendor_my_orders(request):
  context={}
  vendor = Vendor.objects.get(user=request.user)
  orders = Order.objects.filter(vendors__in = [vendor.id],is_ordered=True).order_by("-created_at")

  context['orders'] = orders
  return render(request, "vendor/vendor_my_orders.html",context)