from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.views import View 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password,check_password
from .models import *
from django.urls import reverse
from django.db.models import Count,Sum
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.db.models import Q

import os
from django.conf import settings
from django.http import HttpResponse, Http404



# Create your views here.
def signup(request):
    if request.method == 'POST':
        cid = get_random_string(length=6)
        name = request.POST['name']
        email = request.POST['email']
        DOB = request.POST['DOB']
        password = request.POST.get('pass')
        cpassword = request.POST.get('cpass')
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zip = request.POST['zip']
        mobile = request.POST['mobile']
        profile_image = request.POST['image']
        
        if password != cpassword:
            messages.warning(request, 'Passwords do not match')
            return redirect('signup')
        
        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')
        password = make_password(request.POST.get('pass'))
        # Create the user
        user = CustomUser.objects.create(cid=cid,name=name, email=email,mobile=mobile, DOB=DOB, password=password, cpassword=password, address=address, city=city, state=state, zip=zip,profile_image=profile_image)
        user.save()
        messages.success(request, 'Account created successfully')
        return redirect('login')
    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.warning(request, 'Invalid Email ID!!')
            return redirect('login')
        if check_password(pass1, user.password):
            # login(request, user)
            request.session['user_id'] = user.cid
            messages.success(request, 'Logged in successfully')
            return redirect('home')
        
        else:
            messages.warning(request, 'Invalid Password!!')
            return redirect('login')
    return render(request, 'login.html')

def logout(request):
    # logout(request)
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('login')

def forgotpass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        cpass1 = request.POST.get('cpassword')
        if pass1 == cpass1:
            if CustomUser.objects.filter(email=email).exists():
                user = CustomUser.objects.get(email=email)
                password = make_password(pass1)
                user.password=password
                user.cpassword=password
                user.save()
                messages.success(request, 'Password Reset successfully')
                return redirect('login')
            else:
                messages.success(request, 'Invalid Email Address')
                return redirect('forgotpass')
        else:
            messages.success(request, 'Password are Not Matching')
            return redirect('forgotpass')
    return render(request, 'forgotpass.html')

def home(request):
    if 'user_id' in request.session:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get the user ID from the session
        user_id = request.session.get('user_id', None)
        
        # Get the username from the session
        user = CustomUser.objects.get(cid=user_id)
        username = user.name
        cid = user.cid
        products = Medical_Store.objects.all()
        return render(request, 'home.html', {'products': products, 'name':username ,'cid':cid})
    else:
        messages.warning(request, 'You are not login')
        return render(request, 'login.html')
    
def index(request):
    if 'user_id' in request.session:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get the user ID from the session
        user_id = request.session.get('user_id', None)
        
        # Get the username from the session
        user = CustomUser.objects.get(cid=user_id)
        username = user.name
        cid = user.cid
        products = Medical_Store.objects.all()
        return render(request, 'home.html', {'products': products, 'name':username ,'cid':cid})
    else:
        messages.warning(request, 'You are not login')
        return render(request, 'login.html')

def search(request):
    if request.method == 'POST':
        search = request.POST.get('search')
        products = Medical_Store.objects.filter(Q(medical_name=search) | Q(city=search))
    return render(request, 'search.html' ,{'products': products})


class facility(View):
    def get(self,request,val):
       products = Medical_Store.objects.filter(role=val)
       return render(request, 'facility.html' ,{'products': products})

class medical(View):
    def get(self,request,val):
       products = medicine.objects.filter(sid=val)
       products1 = Medical_Store.objects.filter(sid=val)
       products2 = List.objects.filter(sid=val)
       return render(request, 'medical.html' , {'products': products , 'products1': products1, 'products2': products2})
    
def insertmedicine(request):
    if 'user_id' in request.session:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get the user ID from the session
        user_id = request.session.get('user_id', None)
        
        # Get the username from the session
        user = CustomUser.objects.get(cid=user_id)
        cid = user.cid
        if request.method == 'POST':
            medic = request.POST.get('medicine')
            sid = request.POST.get('sid')
            mid = request.POST.get('mid')
            quantity = request.POST.get('quantity')
            price = request.POST.get('price')
            discount = request.POST.get('discount')
            p = int(price)
            q= int(quantity)
            d = int(discount)
            total = q * p
            Mtotal = total - ( total * (d / 100))
            if Cart.objects.filter(cid=cid, sid=sid, mid=mid).exists():
                if quantity == '0':
                    user = Cart.objects.get(cid=cid, sid=sid, mid=mid)
                    user.delete()
                    products = medicine.objects.filter(sid=sid)
                    products1 = Medical_Store.objects.filter(sid=sid)
                else:
                    user = Cart.objects.get(cid=cid, sid=sid, mid=mid)
                    user.quantity=quantity
                    user.total=total
                    user.Medicine_total=Mtotal
                    user.Final_total=Mtotal
                    user.save()
                    products = medicine.objects.filter(sid=sid)
                    products1 = Medical_Store.objects.filter(sid=sid)
            else:
                user = Cart.objects.create(cid=cid, sid=sid, mid=mid,medicine= medic, price=price,discount=discount, quantity=quantity,  total=total, Medicine_total=Mtotal,Final_total=Mtotal)
                user.save()
                products = medicine.objects.filter(sid=sid)
                products1 = Medical_Store.objects.filter(sid=sid)
                
        return render(request, 'medical.html' , {'products': products , 'products1': products1})
    
def checkoutinsert(request):
    if 'user_id' in request.session:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get the user ID from the session
        user_id = request.session.get('user_id', None)
        
        # Get the username from the session
        user = CustomUser.objects.get(cid=user_id)
        cid = user.cid
        if request.method == 'POST':
            medic = request.POST.get('medicine')
            sid = request.POST.get('sid')
            mid = request.POST.get('mid')
            quantity = request.POST.get('quantity')
            price = request.POST.get('price')
            discount = request.POST.get('discount')
            p = int(price)
            q= int(quantity)
            d = int(discount)
            total = q * p
            Mtotal = total - ( total * (d / 100))
            if Cart.objects.filter(cid=cid, sid=sid, mid=mid).exists():
                if quantity == '0':
                    user = Cart.objects.get(cid=cid, sid=sid, mid=mid)
                    user.delete()
                    products = medicine.objects.filter(sid=sid)
                    products1 = Medical_Store.objects.filter(sid=sid)
                else:
                    user = Cart.objects.get(cid=cid, sid=sid, mid=mid)
                    user.quantity=quantity
                    user.total=total
                    user.Medicine_total=Mtotal
                    user.Final_total=Mtotal
                    user.save()    
            return redirect('checkout', val=sid)   
      

def history(request,val):
    if 'user_id' in request.session:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        user_id = request.session.get('user_id', None)
        # Get the user ID from the session
        if val == "MS":
            products = Order.objects.filter(cid=user_id).annotate(num_orders=Count('oid'))
            sid= 147252	
            products1 = Medical_Store.objects.filter(sid=sid)
        elif val == "HS": 
            products = Appointment.objects.filter(cid=user_id)
            sid = products[0].sid
            products1 = Medical_Store.objects.filter(sid=sid)
        else:
            products = Lab.objects.filter(cid=user_id)
            sid = products[0].sid
            products1 = Medical_Store.objects.filter(sid=sid)
        return render(request, 'histroy.html' ,{'products':products, 'products1':products1})
    else:
        messages.warning(request, 'You are not login')
        return render(request, 'login.html')
    
class checkout(View):
    def get(self,request,val):
        if 'user_id' in request.session:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            
            # Get the user ID from the session
            user_id = request.session.get('user_id', None)


            products = Cart.objects.filter(cid=user_id , sid = val)
            total_price = Cart.objects.filter(cid=user_id,sid = val).aggregate(Sum('Medicine_total'))['Medicine_total__sum']
            if products:
                products1 = Medical_Store.objects.filter(sid=val)
                dis = products1[0].discount
                total = total_price - ( total_price * (dis / 100))
                return render(request, 'checkout.html', {'products': products, 'products1': products1 ,'total' : total_price, 'total1' :total})
            else:
                products = medicine.objects.filter(sid=val)
                products1 = Medical_Store.objects.filter(sid=val)
                return render(request, 'medical.html' , {'products': products , 'products1': products1})
        else:
            messages.warning(request, 'You are not login')
            return render(request, 'login.html')
        

def order(request, sid):
    order_id = get_random_string(length=12)
    # # get all items in the cart for the given store
    cart_items = Cart.objects.filter(sid=sid)
    # # loop through all cart items and add them to the order
    for item in cart_items:
        order_item = Order.objects.create(oid=order_id,cid=item.cid,mid=item.mid,sid=item.sid,medicine=item.medicine,price=item.price,discount=item.discount, quantity=item.quantity,total=item.total,Medicine_total=item.Medicine_total,Final_total=item.Final_total,status='Pending')
        order_item.save()
        user = Cart.objects.get(cid=item.cid, sid=sid, mid=item.mid)
        user.delete()
 
    if 'user_id' in request.session:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get the user ID from the session
        user_id = request.session.get('user_id', None)
        
        # Get the username from the session
        user = CustomUser.objects.get(cid=user_id)
        username = user.name
        products = Medical_Store.objects.all()
        messages.success(request, 'Order Place successfully')
        return render(request, 'home.html', {'products': products, 'name':username})

def terms(request):
    return render(request, 'terms.html')

def about(request):
    return render(request, 'about.html')

def profile(request ,val):
    products = CustomUser.objects.filter(cid=val)
    return render(request, 'profile.html' ,{'products': products})



def appointment(request, val, val1):
    products = List.objects.filter(mid=val1)
    if products:
        name = products[0].name
        products1 = Medical_Store.objects.filter(sid=val)
        return render(request, 'appointment.html' , {'products': products,'dname': name , 'products1': products1})
    else:
        return render(request, 'appointment.html', {'dname': None})

def appointment1(request):
    if 'user_id' in request.session:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get the user ID from the session
        user_id = request.session.get('user_id', None)
        if request.method == 'POST':
            Aid = get_random_string(length=20)
            sid = request.POST['sid']
            mid = request.POST['mid']
            name = request.POST['name']
            patient = request.POST['pname']
            age = request.POST['age']
            date = request.POST['date']
            gender = request.POST['gender']
            disease = request.POST['disease']
            occupation = request.POST['occupation']
            price = request.POST['price']
            user = Appointment.objects.create(Aid=Aid,cid=user_id,sid=sid,mid=mid,name=name,patient=patient,age=age,gender=gender,occupation=occupation,disease=disease ,price=price,Appointment_date=date,Appointment_time='0:0:0',status='Pending')
            user.save()

         # Get the username from the session
        user = CustomUser.objects.get(cid=user_id)
        username = user.name
        products = Medical_Store.objects.all()
        messages.success(request, 'Appointment Book successfully')
        return render(request, 'home.html', {'products': products, 'name':username})    
    
def appointment2(request):
    if 'user_id' in request.session:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get the user ID from the session
        user_id = request.session.get('user_id', None)
        if request.method == 'POST':
            Aid = get_random_string(length=20)
            sid = request.POST['sid']
            mid = request.POST['mid']
            name = request.POST['name']
            patient = request.POST['pname']
            age = request.POST['age']
            date = request.POST['date']
            gender = request.POST['gender']
            disease = request.POST['disease']
            occupation = request.POST['occupation']
            price = request.POST['price']
            total = int(price)
            discount = request.POST['discount']
            discount1 = request.POST['discount1']
            d = int(discount)
            di = int(discount1)
            Mtotal = total - (total * (d/100))
            Ftotal = Mtotal - (Mtotal * (di/100))
            user1 = Lab.objects.create(Aid=Aid,cid=user_id,sid=sid,mid=mid,name=name,patient=patient,age=age,gender=gender,occupation=occupation,disease=disease ,price=price,discount=discount,total=total,Medicine_total=Mtotal,Final_total=Ftotal,Appointment_date=date,Appointment_time='0:0:0',status='Pending')
            user1.save()

            
         # Get the username from the session
        user = CustomUser.objects.get(cid=user_id)
        username = user.name
        products = Medical_Store.objects.all()
        messages.success(request, 'Appointment Book successfully')
        return render(request, 'home.html', {'products': products, 'name':username})    