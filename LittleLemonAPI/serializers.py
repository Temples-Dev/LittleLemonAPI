from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import MenuItem, Cart, Category, Order , OrderItem, User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from decimal import Decimal

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = "__all__"
        depth = 1


class CartSerializer(serializers.ModelSerializer):
  
    price = serializers.SerializerMethodField(method_name="get_price",read_only = True)
    unitprice = serializers.DecimalField(max_digits=6,decimal_places=2,read_only = True )
    
    class Meta:
        model = Cart
        fields = "__all__"
     
    def get_price(self, cart: Cart):
        self.unitprice = cart.menuitem.price
        return cart.quantity * cart.unitprice




class OrderSerializer(serializers.ModelSerializer):
    
    order_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = "__all__"
        # depth = 1
        
    def get_order_items(self, obj):
        items = OrderItemSerializer(OrderItem.objects.filter(order=obj), many=True).data
        print(items)
        return  {i['id'] : i for i in items}
    
    def get_total(self, obj):
        items = OrderItemSerializer(OrderItem.objects.filter(order=obj), many=True).data
        return sum([Decimal(i["price"]) for i in items])
        
    

class OrderItemSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = OrderItem
        fields = "__all__"




class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[
                                   UniqueValidator(queryset=User.objects.all())], write_only=True)

    password = serializers.CharField(
        required=True, min_length=8, write_only=True, validators=[validate_password])

    first_name = serializers.CharField(
        required=True, max_length=150, write_only=True)
    last_name = serializers.CharField(
        required=True, max_length=150, write_only=True)

    class Meta:

        model = User
        fields = ['id', 'username', 'password', "first_name",
                  "last_name", "email", "groups"]

        extra_kwargs = {  # extra_kwargs
            'id': {
                "read_only": True
            },
            'groups': {
                'write_only': True
            }

        }

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
