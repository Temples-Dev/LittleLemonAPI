from django.contrib import admin
from .models import Category, MenuItem, Cart, Order,OrderItem

# Register your models here.

admin.site.register(Category)
admin.site.register(MenuItem)

class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('price','unitprice')

admin.site.register(Cart, CartAdmin)


admin.site.register(Order)
admin.site.register(OrderItem)