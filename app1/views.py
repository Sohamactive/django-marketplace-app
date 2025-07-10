from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate  # Import authenticate
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
import urllib.parse
import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import razorpay
import time
from datetime import datetime, timedelta



def login_auth0(request):
    # Generate CSRF state token
    state_token = secrets.token_urlsafe(32)
    request.session['auth0_state'] = state_token
    
    # Get the next URL and include it in state
    next_url = request.GET.get('next', '/marketplace/')
    state_data = f"{state_token}|{next_url}"
    
    # Build redirect URI dynamically
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    
    # Construct Auth0 authorization URL
    auth0_url = (
        f"https://{settings.AUTH0_DOMAIN}/authorize?"
        f"response_type=code&"
        f"client_id={settings.AUTH0_CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"scope=openid%20profile%20email&"
        f"state={urllib.parse.quote(state_data)}"
    )
    
    return redirect(auth0_url)

def callback(request):
    # Verify state parameter for CSRF protection
    state_param = request.GET.get('state', '')
    if '|' in state_param:
        received_state, next_url = state_param.split('|', 1)
    else:
        received_state = state_param
        next_url = '/marketplace/'
    
    expected_state = request.session.get('auth0_state')
    if not expected_state or received_state != expected_state:
        return HttpResponse("Invalid state parameter", status=400)
    
    # Clean up session
    del request.session['auth0_state']
    
    # Get authorization code
    code = request.GET.get('code')
    if not code:
        error = request.GET.get('error', 'No code provided')
        error_description = request.GET.get('error_description', '')
        return HttpResponse(f"Auth0 Error: {error} - {error_description}", status=400)
    
    # Build redirect URI (same as in login)
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    
    # Exchange code for token
    token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri,
    }
    
    try:
        response = requests.post(token_url, json=token_data, timeout=10)
        response.raise_for_status()
        token_info = response.json()
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error exchanging code for token: {str(e)}", status=400)
    
    id_token = token_info.get('id_token')
    if not id_token:
        return HttpResponse("No ID token received", status=400)
    
    # Authenticate user using the custom Auth0 backend
    user = authenticate(request, token=id_token)
    if user:
        login(request, user, backend='app1.auth0backend.Auth0Backend')
        return redirect(next_url)
    
    return HttpResponse("Authentication failed", status=401)

def logout_auth0(request):
    logout(request)
    
    # Build return URL dynamically
    return_url = request.build_absolute_uri('/')
    
    # Redirect to Auth0 logout endpoint
    logout_url = (
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        f"client_id={settings.AUTH0_CLIENT_ID}&"
        f"returnTo={urllib.parse.quote(return_url)}"
    )
    
    return redirect(logout_url)


def homepage(request):
    products = Product.objects.all()
    return render(request, "app1/homepage.html", {"products": products})

@login_required
def add_to_cart(request, product_id):
    product=get_object_or_404(Product,id=product_id)

    cart_item,created= Cartitem.objects.get_or_create(
        user=request.user,
        product=product,
        
    )
    if not created:
        cart_item.quantity +=1
        cart_item.save()
    messages.success(request,f'{product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'app1:homepage'))

@login_required
def add_to_wishlist(request, product_id):
    product=get_object_or_404(Product,id=product_id)
    wishlist_item,created=Wishlistitem.objects.get_or_create(
        user=request.user,
        product=product
    )
    if created==False:
        messages.info(request,f'{product.name} already added to  wishlist!')
    # don't need to save the when used get_or_created
    # wishlist_item.save()
    else:
        messages.success(request,f'{product.name} added to wishlist!')
    return redirect('app1:homepage')

@login_required
def cart(request):
    cartitems=Cartitem.objects.filter(user=request.user)
    total_price=sum(i.product.price*i.quantity for i in cartitems)
    total_items=sum(i.quantity for i in cartitems )
    tax=round(float(total_price)*(0.18),2)
    discount=0
    total=float(total_price)+float(tax)-discount
    return render(request, "app1/cart.html",{"cartitems": cartitems,
                                             "subtotal":total_price,
                                             "total_item":total_items,
                                             "tax":tax,
                                             "total":total,
                                             "discount":discount,})

@login_required
def wishlist(request):

    wishlistitems=Wishlistitem.objects.filter(user=request.user)
    
    return render(request,"app1/wishlist.html",{"wishlistitems":wishlistitems})

@login_required
def add_to_cart_ajax(request):
    try:
        data = json.loads(request.body)
        product_id=data.get('product_id')
        product= Product.objects.get(id=product_id)
        cart_item,created= Cartitem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def remove_from_wishlist_ajax(request):
    try:
        data = json.loads(request.body)
        wishlist_id = data.get('wishlist_id')
        
        # Remove from wishlist
        wishlist_item = Wishlistitem.objects.get(id=wishlist_id, user=request.user)
        wishlist_item.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
        

@login_required
def order_history(request):
    return render(request, "app1/order_history.html")

@login_required
def checkout(request):
    cartitems=Cartitem.objects.filter(user=request.user)
    address=Address.objects.filter(user=request.user)
    total_price=sum(i.product.price*i.quantity for i in cartitems)
    total_items=sum(i.quantity for i in cartitems )
    tax=round(float(total_price)*(0.18),2)
    discount=0
    print(address)
    total=float(total_price)+float(tax)-discount
    
    # total_product_price=
    order_summary={
        'addresses':address,
        'cartitems':cartitems,
        'total_price':round(total_price,2),
        'total_items':round(total_items,2),
        'tax':round(tax,2),
        'discount':round(discount,2),
        'total':round(total,2)
    }
    return render(request, "app1/checkout.html",order_summary)

@login_required
def update_cart_quantity(request):
    if request.method == 'POST':
        try:
            # this will parse the JSON data from the request body
            # parse means to convert the JSON string into a Python dictionary
            # the json data comes from the frontend, typically from a JavaScript fetch or AJAX call
            data = json.loads(request.body)
            cart_item_id=data.get('cart_item_id')
            # action is a string that indicates the action to be performed
            # it can be 'increase' or 'decrease'
            action=data.get('action')

            # we are giving two parameters to get the cart item
            # one is the cart_item_id which is the id of the cart item
            # the other is the user who is logged in
            # this is to ensure that the cart item belongs to the logged in user
            # this is important for security reasons
            # can work with id also if the user is not given
            # but it is a good practice to give the user as well
            cart_item=Cartitem.objects.get(id=cart_item_id,user=request.user)


            # here we are checking the action
            # if the action is 'increase', we increase the quantity by 1
            if action == 'increase':
                cart_item.quantity += 1
            # if the action is 'decrease', we decrease the quantity by 1
            elif action == 'decrease':
                # if the quantity is greater than 1, we decrease the quantity by 1
                if cart_item.quantity > 1:
                    cart_item.quantity -=1
                else:
                    # if the quantity is 1, we delete the cart item
                    cart_item.delete()
                    # we return a JSON response indicating that the item was removed
                    return JsonResponse({
                        'success': True,
                        'removed' : True,
                        'message': 'Item removed from cart successfully.'
                    })
            # handle remove action
            elif action == 'remove':
                cart_item.delete()
                return JsonResponse({
                    'success': True,
                    'removed': True,
                    'message': 'Item removed from cart successfully.'
                })
                
            cart_item.save()

            # here we are calculating the subtotal, total items, tax, and total
            # again because we need to return this data to the frontend
            # this is to update the cart total in the frontend
            # we are using the same logic as in the cart view
            # this is to ensure that the frontend has the latest data
            cart_items = Cartitem.objects.filter(user=request.user)
            subtotal = sum(item.product.price * item.quantity for item in cart_items)
            total_items = sum(item.quantity for item in cart_items)
            tax = round(float(subtotal) * 0.18, 2)  # 18% tax to match cart view
            discount = 0  # You can add discount logic here
            total = float(subtotal) + float(tax) - discount # Including shipping

            return JsonResponse({
                'success':True,
                'new_quantity': cart_item.quantity,
                'item_total': float(cart_item.product.price * cart_item.quantity),
                'subtotal': float(subtotal),
                'total_items': total_items,
                'tax': float(tax),
                'total': round(float(total),2),
                'discount':discount,
            })

        # Handle the case where the cart item does not exist
        # usually not possible if the user is logged in
        # we will be giving the only user ids where the cart item belongs to the user
        except Cartitem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cart item not found'})
        # Handle any other exceptions that may occur
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}) 
    # If the request method is not POST, return an error response
    # usually not possible as we are using AJAX to send the request
    # but it is a good practice to handle this case
    # this is to ensure that the view only handles POST requests
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def initiate_payment(request):

    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    cartitems=Cartitem.objects.filter(user=request.user)
    total_price=sum(i.product.price*i.quantity for i in cartitems)
    total_items=sum(i.quantity for i in cartitems )
    tax=round(float(total_price)*(0.18),2)
    discount=0
    total=float(total_price)+float(tax)-discount
    amount = total*100
    currency = 'INR'
    receipt = 'order_rcptid_11'

    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        receipt=receipt,
        payment_capture=1
    ))

    context = {
        'order_id': razorpay_order['id'],
        'amount': round(total,2),  # Amount in rupees for display
        'amount_in_paise': amount,  # Amount in paise for Razorpay
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'currency': currency,
        'user':request.user
    }
    return render(request, 'app1/payment_page.html', context)

def payment_success(request):
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    if request.method == "POST":
        try:
            # Extract POST data
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Get cart details for order creation
            cartitems = Cartitem.objects.filter(user=request.user)
            total_price = sum(i.product.price * i.quantity for i in cartitems)
            tax = round(float(total_price) * 0.18, 2)
            total = float(total_price) + float(tax)
            

            # Create order record (you might want to add this)
            order = Order.objects.create(
                user=request.user,
                total_price=total,
                payment_status='Completed'
            )
            cartitems.delete()
            
            # Get user's address for delivery info
            user_address = Address.objects.filter(user=request.user).first()
            
            # Calculate estimated delivery
            from datetime import datetime, timedelta
            estimated_delivery = datetime.now() + timedelta(days=5)
            
            context = {
                'payment_id': razorpay_payment_id,
                'order_id': razorpay_order_id,
                'amount': total,
                'payment_method': 'Online Payment',
                'order': {
                    'id': razorpay_order_id[-6:],
                    'created_at': datetime.now(),
                },
                'estimated_delivery': estimated_delivery.strftime('%B %d-%d, %Y'),
                'shipping_address': str(user_address) if user_address else 'Your selected address',
                'user': request.user,
            }
            
            return render(request, 'app1/success.html', context)

        except Exception as e:
            print(f"Payment error: {e}")
            return render(request, 'app1/success.html', {
                'error': 'Payment verification failed',
                'amount': 0
            })

    # If GET request, redirect to homepage
    return redirect('app1:homepage')