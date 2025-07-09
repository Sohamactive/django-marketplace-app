from django.urls import path
from . import views
app_name='app1'
urlpatterns = [
    path('',views.homepage,name="homepage"),
    path('cart/',views.cart,name="cart"),
    path('wishlist/',views.wishlist,name="wishlist"),
    path('add_to_cart/<int:product_id>/',views.add_to_cart,name="add_to_cart"),
    path('add_to_wishlist/<int:product_id>/',views.add_to_wishlist,name="add_to_wishlist"),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('order_history/', views.order_history, name='order_history'),
    path('checkout/',views.checkout,name="checkout"),
    path('add_to_cart_ajax',views.add_to_cart_ajax,name="add_to_cart_ajax"),
    path('remove_from_wishlist_ajax',views.remove_from_wishlist_ajax,name="remove_from_wishlist_ajax"),
    path('pay/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),

]
