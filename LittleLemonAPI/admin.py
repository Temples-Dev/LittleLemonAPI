from django.contrib import admin
from .models import Category, MenuItem, Cart, Order,OrderItem

# Register your models here.

admin.site.register(Category)
admin.site.register(MenuItem)

class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('price','unitprice')

admin.site.register(Cart, CartAdmin)

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('total')

admin.site.register(Order)

class OrderItemAdmin(admin.ModelAdmin):
    readonly_fields = ('price','unitprice') #quantity

admin.site.register(OrderItem, OrderItemAdmin)