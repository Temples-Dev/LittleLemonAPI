from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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
        return f'Order ID: {self.pk} User : {self.user.username}'
    
    def update_total(self):
        # Calculate total based on associated order items
        print("yoyo update total")
        total = sum(item.price for item in self.order_items.all())
        self.total = total
        self.save()


        
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items',on_delete = models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete = models.CASCADE)
    quantity = models.SmallIntegerField()
    unitprice= models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    
    def __str__(self) -> str:
         return f'Order Id: {self.order.pk},  User: {self.order.user},  Order Item: {self.menuitem.title} '
    
    class Meta:
        unique_together = ("order", "menuitem")
        
    def save(self, *args, **kwargs):
        # Calculate the price based on the quantity and unit price
        self.price = self.quantity * self.unitprice
        super().save(*args, **kwargs)
        
    
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance:Order, **kwargs):
    # Update total of the associated order whenever an OrderItem is saved or deleted
    instance.order.update_total()

        