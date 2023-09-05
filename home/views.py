import json
import uuid
import requests
from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from . models import *
from . forms import *

# Create your views here.
def index(request):
    category = Category.objects.all().order_by('id')
    context = {
        'category': category,
    }
    return render(request, "index.html", context)

def product(request):
    product = Product.objects.all().order_by('id')
    context = {
        'product': product
    }
    return render(request, "product.html", context)

def search(request):
    if request.method == 'POST':
        search = request.POST['search']
        searched = Q(Q(name__icontains=search) | Q(slug__icontains=search))
        searched_items = Product.objects.filter(searched)

        context = {
            'search': search,
            'searched_items': searched_items,
        }
    return render(request, 'search.html', context)

def category(request, slug):
    category = Product.objects.filter(category__slug=slug)
    context = {
        'category': category
    }
    return render(request, 'category.html', context)

def allcat(request):
    allcat = Category.objects.all().order_by('id')
    context = {
        'allcat': allcat,
    }
    return render(request, 'allcat.html', context)

@login_required(login_url='signin')
def details(request, slug):
    details = Product.objects.get(slug=slug)
    context = {
        'details': details
    }
    return render(request, 'details.html', context)

def contact(request):
    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Message sent successfully!..")
            return redirect("index")
        else:
            messages.error(request, form.errors)
            return redirect("contact")
    return render(request, "contact.html")

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username= username, password= password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!..")
            return redirect("index")
        else:
            messages.error(request, "Invalid username/password. Please login with valid username/password")
            return redirect("signin")
    return render(request, "login.html")

def signup(request):
    form = SignupForm()
    if request.method == "POST":
      age = request.POST["age"]
      pic = request.POST["pic"]
      phone_no = request.POST["phone_no"]
      address = request.POST["address"]
      form = SignupForm(request.POST)
      if form.is_valid():
          newuser = form.save()
          newprofile = Profile(user=newuser)
          newprofile.firstName = newuser.first_name
          newprofile.lastName = newuser.last_name
          newprofile.email = newuser.email
          newprofile.age = age
          newprofile.pic = pic
          newprofile.phone_no = phone_no
          newprofile.address = address
          newprofile.save()
          login(request, newuser)
          messages.success(request, "Signup successful!..")
          return redirect("index")
      else:
          messages.error(request, form.errors)
          return redirect("signup")
    return render(request, "signup.html")

def signout(request):
    logout(request)
    return redirect("signin")

@login_required(login_url='signin')
def profile(request):
    profile = Profile.objects.get(user__username=request.user.username)
    context = {
        'profile': profile
    }
    return render(request, "profile.html", context)

@login_required(login_url='signin')
def profile_update(request):
    profile = Profile.objects.get(user__username=request.user.username)
    update = ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        update = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if update.is_valid():
            update.save()
            messages.success(request, "Profile Updated Successfully!...")
            return redirect('profile')
        else:
            messages.error(request, update.errors)
            return redirect('profile_update')
    context = {
        "profile": profile,
        "update": update
    }
    return render(request, "profile_update.html", context)

@login_required(login_url='signin')
def password(request):
    profile = Profile.objects.get(user__username = request.user.username)
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        form  = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password Update successful!...")
            return redirect('signin')
        else:
            messages.error(request, forms.errors)
            return redirect('password')
    context = {
        'form': form
    }
    return render(request, 'password.html', context)

@login_required(login_url='signin')
def shopcart(request):
    if request.method == 'POST':
        items_id = request.POST['product_id']
        quantity = int(request.POST['quantity'])
        product = Product.objects.get(pk=items_id)
        order_num = Profile.objects.get(user__username=request.user.username)
        order_no = order_num.id

        cart = Shopcart.objects.filter(user__username=request.user.username, paid=False)
        if cart:
            basket = Shopcart.objects.filter(product_id=product.id, user__username=request.user.username, paid=False).first()
            if basket:
                basket.quantity += quantity
                basket.amount = basket.price * basket. quantity
                basket.save()
                messages.success(request, "added to cart")
                return redirect('product')
            else:
                cart = Shopcart()
                cart.product = product
                cart.user = request.user
                cart.name = product.name
                cart.price = product.price
                cart.quantity = quantity
                cart.amount = product.price * quantity
                cart.paid = False
                cart.order_no = order_no
                cart.save()
                messages.success(request, "first time adding to cart")
                return redirect('product')
        else:
                cart = Shopcart()
                cart.product = product
                cart.user = request.user
                cart.name = product.name
                cart.price = product.price
                cart.quantity = quantity
                cart.amount = product.price * quantity
                cart.paid = False
                cart.order_no = order_no
                cart.save()
                messages.success(request, "second time adding to cart")
                return redirect('product')
    return redirect('product')

@login_required(login_url='signin')
def displaycart(request):
    profile = Profile.objects.filter(user__username=request.user.username)
    trolley = Shopcart.objects.filter(user__username=request.user.username, paid=False)

    vat = 0
    subtotal = 0
    total = 0

    for items in trolley:
        subtotal = items.price * items.quantity

    vat = 0.075 * subtotal

    total = vat + subtotal
    
    context = {
        'total': total,
        'subtotal': subtotal,
        'vat': vat,
        'trolley': trolley,
        'profile': profile,
    }
    return render(request, 'shopcart.html', context)

@login_required(login_url='signin')
def change(request):
    if request.method == 'POST':
        quantity = int(request.POST['quantity'])
        items = request.POST['items_id']
        modify = Shopcart.objects.get(pk=items)
        modify.quantity += quantity
        modify.amount = modify.price * modify.quantity
        modify.save()
        messages.success(request, 'Changed successfully!..')
        return redirect('displaycart')
    else:
        messages.error(request, 'an error occured')
        return redirect('displaycart')
    
@login_required(login_url='signin')
def deleteitem(request):
    if request.method == 'POST':
        items = request.POST['items_id']
        items_del = Shopcart.objects.get(pk=items)
        items_del.delete()
        messages.success(request, "Cart item deleted successfully")
        return redirect('displaycart')
    else:
        messages.error(request, 'Unable to delete cart item. Check again and delete')
        return redirect('displaycart')
    
@login_required(login_url='signin')
def checkout(request):
    profile = Profile.objects.get(user__username=request.user.username)
    trolley = Shopcart.objects.filter(user__username=request.user.username, paid=False)

    vat = 0
    subtotal = 0
    total = 0

    for items in trolley:
        subtotal = items.price * items.quantity

    vat = 0.075 * subtotal

    total = vat + subtotal
    
    context = {
        'total': total,
        'trolley': trolley,
        'profile': profile,
    }
    return render(request, 'checkout.html', context)

@login_required(login_url='signin')
def pay(request):
    if request.method == 'POST':
        api_key = 'sk_test_f7a011adc0d90dc724c4cb13489520a6ab0ca4c8'
        curl = 'https://api.paystack.co/transaction/initialize'
        cburl = 'http://13.51.241.234/callback'
        ref = str(uuid.uuid4())
        profile = Profile.objects.get(user__username=request.user.username)
        shop_code = profile.id
        total = float(request.POST['total']) * 100
        user = User.objects.get(username=request.user.username)
        first_name = user.first_name
        last_name = user.last_name
        email = user.email
        phone_no = request.POST['phone_no']
        address = request.POST['address']
        headers = {'Authorization': f'Bearer {api_key}'}
        data = {'reference': ref, 'callback_url': cburl, 'amount': int(total),
                'email': user.email, 'order_number': shop_code, 'currency': 'NGN'}
        
        try:
            r = requests.post(curl, headers=headers, json=data)
        except Exception:
            messages.error(request, "Network busy. Invalid data")
        else: 
            transback = json.loads(r.text)
            rdurl = transback['data']['authorization_url']

            account = Payment()
            account.user = user
            account.first_name = user.first_name
            account.last_name = user.last_name
            account.email = user.email
            account.phone_no = phone_no
            account.address = address
            account.amount = total/100
            account.pay_code = ref
            account.shop_code = shop_code
            account.paid = True
            account.save()
            return redirect(rdurl)
    return redirect('checkout')

@login_required(login_url='signin')
def callback(request):
    profile = Profile.objects.filter(user__username= request.user.username)
    trolley = Shopcart.objects.filter(user__username= request.user.username, paid=False)
    payment = Payment.objects.filter(user__username= request.user.username, paid=False)

    for items in trolley:
        items.paid = True
        items.save()

        stock = Product.objects.get(pk=items.product_id)
        stock.quantity -= items.quantity
        stock.save()

    context = {
        'profile': profile,
        'trolley': trolley,
        'payment': payment
    }

    return render(request, 'callback.html', context)