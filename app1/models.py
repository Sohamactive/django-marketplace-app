from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Product(models.Model):
    name=models.CharField(max_length=50)
    description=models.TextField(blank=True)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    image=models.ImageField(upload_to='images/', default='images/default2.png')
    stock=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    category=models.CharField(max_length=50)
    size_option=models.CharField(blank=True,max_length=50)

    def __str__(self):
        string1="LOW" if self.stock<10 else "GOOD"
        return f"{self.name} stock: {self.stock} "+string1+" availability"
    

class Cartitem(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    added_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} quantity added : {self.quantity}"
    
    def get_total_price(self):
        return self.product.price * self.quantity

class Wishlistitem(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    added_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product}"

class Order(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    total_price=models.DecimalField(max_digits=10, decimal_places=2)
    address=models.ForeignKey('Address',on_delete=models.CASCADE)
    payment_status=models.CharField(max_length=50)

    def __str__(self):
        return f"Order #{self.id} — {self.payment_status}"

class Orderitem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    price_at_order=models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.order} {self.product} quantity: {self.quantity}"
    

class Address(models.Model):
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    address_name=models.CharField(max_length=50)
    street_address=models.TextField()
    city=models.CharField(max_length=30)
    state=models.CharField(max_length=30)
    zipcode=models.IntegerField(default=0)
    phone_number=PhoneNumberField()

    def __str__(self):
        return f"{self.address_name} - {self.city}, {self.state} ({self.zipcode})"
    
 