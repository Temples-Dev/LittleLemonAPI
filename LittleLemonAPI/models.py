from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length = 255, db_index = True)
    
    def __str__(self) -> str:
        return self.title
    
    
class MenuItem(models.Model):
    title = models.CharField(max_length = 255, db_index = True)
    price = models.DecimalField(max_digits=6,decimal_places=2, db_index = True)
    featured = models.BooleanField(db_index = True)
    category = models.ForeignKey(Category, on_delete = models.PROTECT)
    
    def __str__(self) -> str:
        return self.title
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete = models.CASCADE)
    quantity = models.SmallIntegerField()
    unitprice= models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    
    def __str__(self) -> str:
        return f'Cart : {self.user.username}'
    
    class Meta:
        unique_together = ("menuitem", "user")
    
     # Calculate the price before saving
    def save(self, *args, **kwargs):
        self.unitprice = self.menuitem.price
        self.price = self.quantity * self.unitprice 
        super(Cart, self).save(*args, **kwargs)
        

class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete = models.SET_NULL, related_name="delivery_crew", null= True)
    status = models.BooleanField(db_index = True, default = 0)
    total = models.DecimalField(max_digits=6,decimal_places=2)
    date = models.DateField(db_index = True)
    
    def __str__(self) -> str:
        return f'Order : {self.user.username}'
    

class OrderItem(models.Model):
    order = models.ForeignKey(User, on_delete = models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete = models.CASCADE)
    quantity = models.SmallIntegerField(),
    unitprice= models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    
    def __str__(self) -> str:
         return f'Order Item: {self.order.username}'
    
    class Meta:
        unique_together = ("order", "menuitem")
        

        